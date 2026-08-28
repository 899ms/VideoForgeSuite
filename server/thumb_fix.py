#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""串行补缩略图：对缺失的 txt_*.html 逐个截图（独立 Edge 进程，20s 超时兜底）
单线程串行，避免 html_thumb.py 并发在 Windows 上的卡死问题。
"""
import subprocess, pathlib, time, shutil, os

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
THUMB = pathlib.Path(r"D:/VideoForgeSuite/materials/.thumbs/effects_html")
SRC = pathlib.Path(r"D:/VideoForgeSuite/materials/styles/文字入场")

def shot(f):
    out = THUMB / (f.name + ".jpg")
    if out.exists() and out.stat().st_size > 800:
        return "skip"
    prof = pathlib.Path(os.environ["TMP"]) / ("vff_" + str(os.getpid()) + "_" + str(time.time_ns()))
    prof.mkdir(parents=True, exist_ok=True)
    uri = "file:///" + str(f).replace("\\", "/")
    args = [EDGE, f"--user-data-dir={prof}", "--headless=new", "--no-sandbox",
            "--disable-gpu", "--no-first-run", "--hide-scrollbars",
            "--window-size=480,300", "--virtual-time-budget=1500", f"--screenshot={out}", uri]
    try:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            p.wait(timeout=20)
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                p.kill()
            except Exception:
                pass
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    if out.exists() and out.stat().st_size > 800:
        return "ok"
    # 兜底：纯色占位
    try:
        from PIL import Image
        Image.new("RGB", (480, 300), (40, 36, 64)).save(out)
        return "fallback"
    except Exception:
        return "fail"

missing = [f for f in sorted(SRC.glob("txt_*.html"))
           if not (THUMB / (f.name + ".jpg")).exists() or (THUMB / (f.name + ".jpg")).stat().st_size <= 800]
print(f"to fix: {len(missing)}")
for f in missing:
    t0 = time.time()
    r = shot(f)
    print(f"  {r}: {f.name} ({time.time()-t0:.1f}s)")
# 清理可能残留的 edge
subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("done")
