#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 4 大分类下的 MP4/WebM 生成 poster 缩略图到 materials/.thumbs/<category>/<name>.jpg

关键修复：源视频亮度差异极大（YAVG 3 ~ 172）。单一全局提亮无法兼顾：
  - 普通 brightness=0.20 对最暗的 fx_glitch(YAVG3) 只到 27，仍接近黑屏；
  - gamma 反而把暗视频变得更黑。
因此改为【逐文件自适应亮度】：先测量源帧平均亮度，再按 (目标-实测) 计算提亮量，
封顶 0.7，避免亮视频过曝。目标亮度 ~85（约 1/3 灰阶，清晰可见但不过曝）。
"""
import subprocess, pathlib, os, re, sys, shutil

ROOT = pathlib.Path(r"D:\VideoForgeSuite\materials")
THUMB = ROOT / ".thumbs"
CATS = ["styles", "widgets", "transitions", "assets"]
TARGET_YAVG = 85.0          # 目标平均亮度（0-255）
LIFT_PER_Y = 0.00833        # 实测：brightness 每 +0.01 ≈ +1.2 YAVG
MAX_OFFSET = 0.7            # 提亮上限，防止暗视频过曝边带
FFMPEG = shutil.which("ffmpeg") or r"C:\ffmpeg\ffmpeg.exe"


def measure_yavg(src: pathlib.Path) -> float | None:
    """测量源视频在 1.2s 处的平均亮度 YAVG（0-255），失败返回 None。"""
    cmd = [
        FFMPEG, "-hide_banner", "-loglevel", "info",
        "-ss", "00:00:01.200", "-i", str(src),
        "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
        "-frames:v", "1", "-f", "null", "-"
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stderr
        vals = re.findall(r"lavfi\.signalstats\.YAVG=([\d.]+)", out)
        if vals:
            return float(vals[-1])
    except Exception:
        pass
    return None


def gen(src: pathlib.Path):
    category = src.relative_to(ROOT).parts[0]
    out = THUMB / category / (src.name + ".jpg")
    out.parent.mkdir(parents=True, exist_ok=True)

    y0 = measure_yavg(src)
    if y0 is None:
        offset = 0.35          # 测量失败兜底
    else:
        offset = max(0.0, min(MAX_OFFSET, (TARGET_YAVG - y0) * LIFT_PER_Y))

    vf = (f"scale=400:-2:flags=lanczos,"
          f"eq=contrast=1.05:brightness={offset:.3f}:saturation=1.22,"
          f"format=yuv420p")
    cmd = [
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", "00:00:01.200", "-i", str(src),
        "-vf", vf,
        "-frames:v", "1", "-update", "1", "-q:v", "2", str(out)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if out.exists() and out.stat().st_size > 500:
            return True, offset
        return False, offset
    except Exception as e:
        print(f"FAIL {src}: {e}")
        return False, offset


def main():
    ok = fail = 0
    details = []
    for cat in CATS:
        d = ROOT / cat
        if not d.exists():
            continue
        for root, _, files in os.walk(d):
            for fn in files:
                if fn.lower().endswith((".mp4", ".webm")):
                    good, off = gen(pathlib.Path(root) / fn)
                    if good:
                        ok += 1
                        details.append(f"  + {cat}/{fn}  lift={off:.3f}")
                    else:
                        fail += 1
                        details.append(f"  - {cat}/{fn}  FAILED")
    log = "\n".join(details)
    print(f"thumbs done: ok={ok} fail={fail}\n{log}")


if __name__ == "__main__":
    main()
