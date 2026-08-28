#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoForgeSuite - Control / Orchestration Layer (CTRL)
Local MCP-style HTTP server. Material hub (L0) + three video tools routing.

Endpoints:
  GET  /                              -> serve app/index.html
  GET  /static/<path>                 -> static assets
  GET  /materials/<cat>/<name>        -> serve a material file
  GET  /api/tools                     -> status of the 3 tools
  GET  /api/materials                 -> list material library (L0) by category
  GET  /api/status                    -> environment status
  GET  /api/jobs                      -> list running/last generation jobs
  POST /api/generate                  -> trigger an H3 generation
  POST /api/gen_fx                    -> trigger a procedural ffmpeg clip

No third-party deps.
"""

import http.server
import socketserver
import json
import os
import subprocess
import threading
import pathlib
import urllib.parse
import datetime
import shutil
import traceback

# ---------- paths ----------
ROOT = pathlib.Path(r"D:\VideoForgeSuite")
APP = ROOT / "app"
MAT_ROOT = ROOT / "materials"
H3 = ROOT / "h3" / "generate.py"
H3ENV = r"D:\h3_env\Scripts\python.exe"
MODELSCOPE_CACHE = r"D:\modelscope_cache"
FFMPEG = shutil.which("ffmpeg") or r"C:\ffmpeg\ffmpeg.exe"
SERVER_DIR = ROOT / "server"
LOG_DIR = SERVER_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8765
JOBS = {}
JOBS_LOCK = threading.Lock()


# ---------- module-level helpers ----------
def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


# 四大功能分类（按用途划分，而非按文件类型）
CATEGORY_META = {
    "styles":      {"name": "风格",       "icon": "🎨", "desc": "整体视觉风格方向：HTML 视觉冲击、文字入场、Remotion 样片"},
    "widgets":     {"name": "组件·插件",  "icon": "🔧", "desc": "可叠加的小插件：仪表盘/数据、字幕条、HUD 边框、Canvas 图形"},
    "transitions": {"name": "转场",       "icon": "🔀", "desc": "场景与场景之间的跳跃：HTML 转场、视频转场、转场样片"},
    "assets":      {"name": "素材",       "icon": "🗂️", "desc": "底层原料：实拍素材、动态纹理、绿幕"},
}
CATEGORIES = list(CATEGORY_META.keys())


def _media_ext(suf):
    suf = suf.lower()
    if suf in (".mp4", ".webm", ".gif"): return "video"
    if suf in (".png", ".jpg", ".jpeg", ".webp"): return "image"
    if suf in (".mp3", ".wav", ".m4a"): return "audio"
    if suf == ".html": return "html"
    return "other"


def _scan_recursive(cat_dir):
    """递归扫描某分类目录：一级子目录作为 subcat（无子目录则记 '其他'）。"""
    items = []
    if not cat_dir.is_dir():
        return items
    for root, dirs, files in os.walk(cat_dir):
        rootp = pathlib.Path(root)
        rel_parts = rootp.relative_to(MAT_ROOT).parts
        category = rel_parts[0]
        subcat = rel_parts[1] if len(rel_parts) > 1 else "其他"
        for fn in sorted(files):
            if fn.startswith("."):
                continue
            f = rootp / fn
            suf = f.suffix.lower()
            kind = _media_ext(suf)
            if kind == "other":
                continue
            st = f.stat()
            rel = f.relative_to(MAT_ROOT).as_posix()
            items.append({
                "name": fn,
                "category": category,
                "subcat": subcat,
                "size_mb": round(st.st_size / 1e6, 2),
                "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                "kind": kind,
                "ext": suf,
                "url": "/materials/" + urllib.parse.quote(rel),
            })
    return items


# ---------- HTTP handler ----------
class Handler(http.server.BaseHTTPRequestHandler):
    # ---- low-level send helpers ----
    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, fp, ctype):
        try:
            size = fp.stat().st_size
            range_hdr = self.headers.get("Range")
        except Exception as e:
            return self._send_json(404, {"error": f"stat failed: {e}"})
        start, end = 0, size - 1
        status = 200
        if range_hdr and range_hdr.startswith("bytes="):
            try:
                spec = range_hdr[6:].split(",")[0].strip()
                if spec.startswith("-"):
                    # suffix range: last N bytes
                    n = int(spec[1:])
                    start = max(0, size - n)
                elif "-" in spec:
                    a, b = spec.split("-", 1)
                    start = int(a) if a else 0
                    end = int(b) if b else size - 1
                else:
                    start = int(spec)
                if start > end or start >= size:
                    return self._send_json(416, {"error": "range not satisfiable"})
                end = min(end, size - 1)
                status = 206
            except ValueError:
                pass
        length = end - start + 1
        try:
            with open(fp, "rb") as f:
                f.seek(start)
                chunk = f.read(length)
        except Exception as e:
            return self._send_json(404, {"error": f"read failed: {e}"})
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(chunk)))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(chunk)

    def _static(self, fp, ctype="application/octet-stream"):
        if fp.exists() and fp.is_file():
            self._send_file(fp, ctype)
        else:
            self._send_json(404, {"error": "not found", "path": str(fp)})

    # ---- routing ----
    def do_GET(self):
        try:
            self._do_GET_impl()
        except Exception as e:
            err = (SERVER_DIR / "errors.log")
            with open(err, "a", encoding="utf-8") as f:
                f.write(f"\n--- {_now()} {self.path} ---\n")
                f.write(traceback.format_exc())
            try:
                self._send_json(500, {"error": str(e)})
            except Exception:
                pass

    def _do_GET_impl(self):
        p = urllib.parse.urlparse(self.path)
        path = p.path
        if path in ("/", "/index.html"):
            return self._static(APP / "index.html", "text/html; charset=utf-8")
        if path.startswith("/static/"):
            fp = (APP / path[len("/static/"):])
            ctype = ("text/css; charset=utf-8" if fp.suffix == ".css"
                     else ("application/javascript; charset=utf-8" if fp.suffix == ".js"
                     else "application/octet-stream"))
            return self._static(fp, ctype)
        if path.startswith("/materials/"):
            rel = urllib.parse.unquote(path[len("/materials/"):])
            if not rel:
                return self._send_json(400, {"error": "missing path"})
            fp = MAT_ROOT / rel
            try:
                if fp.exists() and fp.is_file() and fp.is_relative_to(MAT_ROOT):
                    suf = fp.suffix.lower()
                    ctype = ("video/mp4" if suf in (".mp4", ".webm")
                             else ("image/png" if suf == ".png"
                             else ("image/jpeg" if suf in (".jpg", ".jpeg")
                             else ("audio/mpeg" if suf == ".mp3"
                             else ("text/html" if suf == ".html"
                             else "application/octet-stream")))))
                    return self._send_file(fp, ctype)
            except ValueError:
                pass
            return self._send_json(404, {"error": "material not found", "name": rel})
        if path.startswith("/thumbs/"):
            rel = urllib.parse.unquote(path[len("/thumbs/"):])
            if not rel:
                return self._send_json(400, {"error": "missing path"})
            fp = MAT_ROOT / ".thumbs" / rel
            try:
                if fp.exists() and fp.is_file() and fp.is_relative_to(MAT_ROOT):
                    return self._send_file(fp, "image/jpeg")
            except ValueError:
                pass
            return self._send_json(404, {"error": "thumb not found", "name": rel})
        if path == "/api/tools":
            return self._send_json(200, self.tools())
        if path == "/api/materials":
            return self._send_json(200, self.materials())
        if path == "/api/status":
            return self._send_json(200, self.status())
        if path == "/api/jobs":
            with JOBS_LOCK:
                return self._send_json(200, {"jobs": list(JOBS.values())})
        return self._send_json(404, {"error": "not found"})

    def do_POST(self):
        try:
            self._do_POST_impl()
        except Exception as e:
            err = (SERVER_DIR / "errors.log")
            with open(err, "a", encoding="utf-8") as f:
                f.write(f"\n--- POST {_now()} {self.path} ---\n")
                f.write(traceback.format_exc())
            try:
                self._send_json(500, {"error": str(e)})
            except Exception:
                pass

    def _do_POST_impl(self):
        p = urllib.parse.urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            data = json.loads(raw or b"{}")
        except Exception as e:
            return self._send_json(400, {"ok": False, "error": f"bad request: {e}"})
        if p.path == "/api/generate":
            return self._send_json(200, self.start_generate(data))
        if p.path == "/api/gen_fx":
            return self._send_json(200, self.start_fx(data))
        return self._send_json(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        return

    # ---- logic ----
    def tools(self):
        node = shutil.which("node") or (r"C:\Program Files\nodejs\node.exe"
                                        if os.path.exists(r"C:\Program Files\nodejs\node.exe") else None)
        tools = [
            {"id": "remotion", "name": "Remotion",
             "status": "available" if node else "missing-node",
             "desc": "程序化合成视频 (React + WebGL)",
             "integration": "npm run build 出 MP4（已有 12 条真实渲染素材）",
             "color": "#00e5ff"},
            {"id": "hyperframes", "name": "HyperFrames",
             "status": "not-installed",
             "desc": "Agent-native HTML → 视频 (HeyGen 开源)",
             "integration": "Phase 5：/hyperframes skill 安装后接入",
             "color": "#a855f7"},
            {"id": "h3", "name": "MiniMax H3 (NF4)",
             "status": "ready" if os.path.exists(H3ENV) else "missing-env",
             "desc": "DiffSynth-Studio 真实素材生成 (FL2VA / REF2VA)",
             "integration": "generate.py 调用，权重缓存于 MODELSCOPE_CACHE",
             "color": "#ff2d75"},
        ]
        return {"tools": tools}

    def materials(self):
        categories = []
        all_items = []
        for cat in CATEGORIES:
            d = MAT_ROOT / cat
            meta = CATEGORY_META.get(cat, {"name": cat, "icon": "•"})
            items = _scan_recursive(d)
            categories.append({
                "id": cat, "name": meta["name"], "icon": meta["icon"],
                "desc": meta.get("desc", ""), "count": len(items),
            })
            all_items.extend(items)
        all_items.sort(key=lambda x: x["mtime"], reverse=True)
        return {
            "categories": categories,
            "count": len(all_items),
            "materials": all_items[:5000],
            "hub": str(MAT_ROOT),
        }

    def status(self):
        with JOBS_LOCK:
            running = sum(1 for j in JOBS.values() if j["status"] == "running")
        return {
            "h3_env": os.path.exists(H3ENV),
            "h3_script": os.path.exists(H3),
            "modelscope_cache": os.path.exists(MODELSCOPE_CACHE),
            "material_hub": str(MAT_ROOT),
            "jobs_running": running,
        }

    def start_generate(self, data):
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return {"ok": False, "error": "prompt is required"}
        mode = data.get("mode", "fl2va")
        if mode not in ("fl2va", "ref2va"):
            mode = "fl2va"
        try:
            nf = int(data.get("num_frames", 73))
            steps = int(data.get("steps", 25))
            seed = int(data.get("seed", 42))
        except ValueError:
            return {"ok": False, "error": "num_frames/steps/seed must be integers"}
        if not os.path.exists(H3ENV):
            return {"ok": False, "error": "H3 env missing at " + H3ENV}
        out_dir = MAT_ROOT / "assets" / "AI生成"
        out_dir.mkdir(parents=True, exist_ok=True)
        job_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = out_dir / f"h3_{job_id}.mp4"
        cmd = [H3ENV, str(H3),
               "--prompt", prompt,
               "--output", str(out),
               "--mode", mode,
               "--num_frames", str(nf),
               "--steps", str(steps),
               "--seed", str(seed)]
        env = dict(os.environ)
        env["MODELSCOPE_CACHE"] = MODELSCOPE_CACHE
        try:
            logf = open(LOG_DIR / f"h3_{job_id}.log", "w", encoding="utf-8")
            proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT,
                                    text=True, env=env, cwd=str(ROOT / "h3"))
        except Exception as e:
            return {"ok": False, "error": f"launch failed: {e}"}
        job = {
            "id": job_id, "pid": proc.pid, "prompt": prompt, "mode": mode,
            "num_frames": nf, "steps": steps, "seed": seed,
            "status": "running", "started": _now(),
            "output_file": str(out), "returncode": None,
        }
        with JOBS_LOCK:
            JOBS[job_id] = job
        threading.Thread(target=self._watch, args=(job_id, proc), daemon=True).start()
        return {"ok": True, "job_id": job_id, "output": str(out), "status_url": "/api/jobs"}

    def start_fx(self, data):
        if not os.path.exists(FFMPEG):
            return {"ok": False, "error": "ffmpeg not found at " + FFMPEG}
        try:
            duration = int(data.get("duration", 5))
        except ValueError:
            duration = 5
        duration = max(2, min(15, duration))
        out_dir = MAT_ROOT / "assets" / "动态纹理"
        out_dir.mkdir(parents=True, exist_ok=True)
        job_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = out_dir / f"fx_{job_id}.mp4"
        vf = (
            "drawbox=x='mod(t*300,iw)':y=0:w=6:h=ih:color=0x00e5ff@0.55,"
            "drawbox=x='mod(t*180+420,iw)':y=0:w=3:h=ih:color=0xff2d75@0.40,"
            "drawtext=text='VIDEOFORGE SUITE':fontfile='C\\:/Windows/Fonts/arial.ttf':"
            "fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:"
            "shadowcolor=0x00e5ff:shadowx=4:shadowy=4:alpha='if(lt(t,0.5),0,1)'"
        )
        cmd = [
            FFMPEG, "-y", "-f", "lavfi", "-i",
            f"gradients=s=1280x720:c0=0x06070a:c1=0x103a5c:x0=0:y0=0:x1=1280:y1=720:d={duration}:speed=0.04",
            "-vf", vf, "-t", str(duration), "-r", "30", "-pix_fmt", "yuv420p", str(out),
        ]
        try:
            logf = open(LOG_DIR / f"fx_{job_id}.log", "w", encoding="utf-8")
            proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, text=True)
        except Exception as e:
            return {"ok": False, "error": f"launch failed: {e}"}
        job = {
            "id": job_id, "pid": proc.pid, "kind": "procedural-ffmpeg",
            "duration": duration, "status": "running", "started": _now(),
            "output_file": str(out), "returncode": None,
        }
        with JOBS_LOCK:
            JOBS[job_id] = job
        threading.Thread(target=self._watch, args=(job_id, proc), daemon=True).start()
        return {"ok": True, "job_id": job_id, "output": str(out),
                "note": "procedural clip via ffmpeg (no model weights needed)"}

    def _watch(self, job_id, proc):
        try:
            proc.wait()
            rc = proc.returncode
        except Exception:
            rc = -1
        with JOBS_LOCK:
            if job_id in JOBS:
                JOBS[job_id]["status"] = "done" if rc == 0 else "failed"
                JOBS[job_id]["returncode"] = rc
                JOBS[job_id]["finished"] = _now()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def main():
    MAT_ROOT.mkdir(parents=True, exist_ok=True)
    srv = ThreadedHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[VideoForgeSuite] CTRL listening on http://localhost:{PORT}", flush=True)
    print(f"[VideoForgeSuite] material hub (L0): {MAT_ROOT}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()