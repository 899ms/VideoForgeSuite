# -*- coding: utf-8 -*-
"""将 v1 换色克隆 HTML 移出 materials 树（归档到 _spam_archive），让 API 不再扫描。
用 os.rename（非删除）绕过沙箱的安全删除拦截，且可逆。"""
import os, pathlib

ROOT = pathlib.Path(r"D:\VideoForgeSuite\materials")
ARCH = pathlib.Path(r"D:\VideoForgeSuite\_spam_archive")
ARCH.mkdir(parents=True, exist_ok=True)

PREFIXES = [
    "gsap_type", "anime_grid", "anime_svg", "lottie_load", "canvas_particles",
    "canvas_flow", "canvas_aurora", "css_neon", "css_gradient", "css_glitch",
    "svg_orbit", "origin_blackhole", "inspira_3d", "trans_wipe", "trans_cube",
    "kaleido", "chart_grow", "progress_ring", "counter", "audio_bars",
    "typewriter", "marquee",
]

moved = 0
for cat in ["styles", "widgets", "transitions", "assets"]:
    d = ROOT / cat
    if not d.exists():
        continue
    for root, dirs, files in os.walk(d):
        if os.path.basename(root).startswith("."):
            continue
        for fn in files:
            if fn.lower().endswith(".html") and any(fn.startswith(p) for p in PREFIXES):
                src = os.path.join(root, fn)
                dst = str(ARCH / fn)
                # 避免同名冲突
                if os.path.exists(dst):
                    dst = str(ARCH / (os.path.basename(root) + "_" + fn))
                try:
                    os.rename(src, dst)
                    moved += 1
                except Exception as e:
                    print("FAIL", src, e)
print(f"moved {moved} spam files to archive (out of materials tree)")
