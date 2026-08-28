#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, pathlib, re, glob, json, shutil
ROOT = pathlib.Path(r"D:\VideoForgeSuite\materials\.thumbs")
FF = shutil.which("ffmpeg") or r"C:\ffmpeg\ffmpeg.exe"
files = []
for p in ROOT.rglob("*.jpg"):
    if "effects_html" in p.parts:
        continue
    files.append(p)
rows = []
for p in files:
    cmd = [FF, "-hide_banner", "-loglevel", "info", "-i", str(p),
           "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
           "-frames:v", "1", "-f", "null", "-"]
    try:
        o = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stderr
        v = re.findall(r"YAVG=([\d.]+)", o)
        y = float(v[-1]) if v else None
    except Exception:
        y = None
    rows.append((str(p.relative_to(ROOT)), y))
dark = [r for r in rows if r[1] is not None and r[1] < 50]
vis  = [r for r in rows if r[1] is not None and 50 <= r[1] < 160]
br   = [r for r in rows if r[1] is not None and r[1] >= 160]
none = [r for r in rows if r[1] is None]
vals = [r[1] for r in rows if r[1] is not None]
out = {
    "total": len(rows),
    "dark_lt50": len(dark),
    "visible_50_160": len(vis),
    "bright_ge160": len(br),
    "unmeasured": len(none),
    "min": min(vals) if vals else None, "max": max(vals) if vals else None,
    "avg": round(sum(vals)/len(vals), 1) if vals else None,
    "darkest_5": sorted([(round(y,1),n) for n,y in dark], key=lambda x:x[0])[:5],
}
print(json.dumps(out, ensure_ascii=False, indent=2))
