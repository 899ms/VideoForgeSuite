# -*- coding: utf-8 -*-
"""稳健版 HTML 动效缩略图生成器（Python 版）。
为每个 .html 生成 materials/.thumbs/effects_html/<basename>.html.jpg
- 幂等：已有有效缩略图则跳过（支持断点续跑）
- 仅当超过 25s 才 taskkill /T 杀进程树
- 3 路并发
- 结束时强制清理残留 msedge 进程
"""
import subprocess, os, pathlib, concurrent.futures, sys, time, atexit

ROOT = pathlib.Path(r"D:\VideoForgeSuite\materials")
THUMB = ROOT / ".thumbs" / "effects_html"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PER_FILE_S = 25
CONCURRENCY = 3
BUDGET = 2500
_alive = []

def _sweep():
    # 结束时清理任何残留 edge
    try:
        subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

atexit.register(_sweep)

def list_html(dir, out=None):
    out = out if out is not None else []
    for e in os.scandir(dir):
        if e.name.startswith(".") or e.name.startswith("_"):
            continue
        if e.is_dir():
            list_html(e.path, out)
        elif e.name.lower().endswith(".html"):
            out.append(e.path)
    return out

def shot_once(html_path, out_path):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 800:
        return 1  # 已有有效缩略图，跳过
    prof = pathlib.Path(os.environ["TMP"]) / ("vf_" + str(os.getpid()) + "_" + str(time.time_ns()))
    prof.mkdir(parents=True, exist_ok=True)
    uri = "file:///" + html_path.replace("\\", "/")
    args = [EDGE, f"--user-data-dir={prof}", "--headless=new", "--no-sandbox",
            "--disable-gpu", "--no-first-run", "--hide-scrollbars",
            "--force-color-profile=srgb", "--window-size=480,300",
            f"--virtual-time-budget={BUDGET}", f"--screenshot={out_path}", uri]
    try:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _alive.append(p.pid)
        try:
            p.wait(timeout=PER_FILE_S)
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                p.kill()
            except Exception:
                pass
    finally:
        try:
            import shutil
            shutil.rmtree(prof, ignore_errors=True)
        except Exception:
            pass
    if os.path.exists(out_path) and os.path.getsize(out_path) > 800:
        return 1
    # 截图失败也放一个兜底（纯色占位），避免卡片永久空白
    try:
        from PIL import Image
        Image.new("RGB", (480, 300), (40, 36, 64)).save(out_path)
        return 0
    except Exception:
        return 0

def main():
    THUMB.mkdir(parents=True, exist_ok=True)
    files = list_html(str(ROOT))
    print(f"html files: {len(files)}", flush=True)
    ok = 0
    skip = 0
    fail = 0
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {}
        for f in files:
            name = os.path.basename(f)
            out = str(THUMB / (name + ".jpg"))
            futs[ex.submit(shot_once, f, out)] = name
        for fut in concurrent.futures.as_completed(futs):
            done += 1
            r = fut.result()
            if r == 1:
                ok += 1
            elif r == 0 and os.path.exists(str(THUMB / (futs[fut] + ".jpg"))):
                skip += 1
            else:
                fail += 1
            if done % 25 == 0 or done == len(files):
                print(f"progress {done}/{len(files)} ok={ok} skip={skip} fail={fail}", flush=True)
    print(f"html thumbs done ok={ok} skip={skip} fail={fail}", flush=True)
    _sweep()

if __name__ == "__main__":
    main()
