#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""素材库整理：去重 + 归类重构（第五轮）
1) 归档重复：fx_txt_* 每动画保留1配色、fx_cv_* 同款双色保留1、字幕条 hfx_* 归档、Remotion 有正片的 *_preview 归档
2) 只有 preview 无正片的 → 重命名去掉 _preview
3) 归类移动：HTML 动效统一到 styles/精选动效；文字 mp4 进 styles/文字入场；体积光进 assets/动态纹理；swirl 进 transitions/视频转场
"""
import shutil, re
from pathlib import Path

MAT = Path(r"D:/VideoForgeSuite/materials")
ARCHIVE = Path(r"D:/VideoForgeSuite/_spam_archive/dup")

def move(f, dst_dir, name=None):
    """移动（归档/归类），自动建目录，冲突加后缀"""
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / (name or f.name)
    i = 1
    while dst.exists():
        dst = dst_dir / (f"{dst.stem}_{i}{dst.suffix}")
        i += 1
    shutil.move(str(f), str(dst))
    return dst

moved = []
renamed = []

# ---------- 1) 字幕条：归档 hfx_*（保留 sub_*） ----------
for f in (MAT / "widgets/字幕条").glob("hfx_*"):
    moved.append(("dup-subtitle", f, move(f, ARCHIVE / "subtitle")))

# ---------- 2) fx_txt_* 文字入场：每动画保留 1 配色 ----------
txt_dir = MAT / "styles/文字入场"
keep = set()
for f in sorted(txt_dir.glob("fx_txt_*.mp4")):
    m = re.match(r"(fx_txt_[A-Za-z]+)_", f.name)
    anim = m.group(1) if m else f.name
    if anim in keep:
        moved.append(("dup-txt-color", f, move(f, ARCHIVE / "txt_color")))
    else:
        keep.add(anim)

# ---------- 3) fx_cv_* Canvas 同款双色：保留 1 ----------
cv_dir = MAT / "widgets/Canvas图形"
cv_keep = set()
for f in sorted(cv_dir.glob("fx_cv_*.mp4")):
    m = re.match(r"(fx_cv_[a-z_]+?)_(cyan|pink|purple|green|gold|red|white|blue|orange|magenta)\.mp4$", f.name)
    if m:
        anim = m.group(1)
        if anim in cv_keep:
            moved.append(("dup-cv-color", f, move(f, ARCHIVE / "cv_color")))
        else:
            cv_keep.add(anim)

# ---------- 4) Remotion 样片：有正片的 *_preview 归档；只有 preview 的重命名 ----------
rm_dir = MAT / "styles/Remotion样片"
bases = {}
for f in rm_dir.glob("*.mp4"):
    stem = f.name[:-4]
    if stem.endswith("_preview"):
        bases.setdefault(stem[:-8], []).append(f)
    else:
        bases.setdefault(stem, []).append(f)
for base, files in bases.items():
    has_main = any(not x.name[:-4].endswith("_preview") for x in files)
    for f in files:
        if f.name[:-4].endswith("_preview"):
            if has_main:
                moved.append(("dup-preview", f, move(f, ARCHIVE / "preview")))
            else:
                new_name = f.name[:-8] + ".mp4"  # 去掉 _preview
                dst = move(f, rm_dir, name=new_name)
                renamed.append((f.name, dst.name))
                print(f"  renamed: {f.name} -> {dst.name}")

# ---------- 5) 归类：HTML 动效统一到 styles/精选动效 ----------
src_html = MAT / "assets/精选素材"
dst_fx = MAT / "styles/精选动效"
if src_html.exists():
    for f in src_html.glob("*.html"):
        dst = move(f, dst_fx)
        moved.append(("html->styles/精选动效", f, dst))
    try:
        src_html.rmdir()  # 清空后移除空目录
    except OSError:
        pass

# ---------- 6) styles/HTML风格渲染：文字 mp4 -> 文字入场；体积光 -> 动态纹理 ----------
hfx_dir = MAT / "styles/HTML风格渲染"
if hfx_dir.exists():
    for f in hfx_dir.glob("*.mp4"):
        if "kinetic" in f.name or "scramble" in f.name:
            dst = move(f, MAT / "styles/文字入场")
            moved.append(("text mp4->styles/文字入场", f, dst))
        elif "volumetric" in f.name:
            dst = move(f, MAT / "assets/动态纹理")
            moved.append(("volumetric->assets/动态纹理", f, dst))
    try:
        hfx_dir.rmdir()
    except OSError:
        pass

# ---------- 7) transitions/HTML转视频转场：swirl -> 视频转场 ----------
swirl_dir = MAT / "transitions/HTML转视频转场"
if swirl_dir.exists():
    for f in swirl_dir.glob("*.mp4"):
        dst = move(f, MAT / "transitions/视频转场")
        moved.append(("swirl->transitions/视频转场", f, dst))
    try:
        swirl_dir.rmdir()
    except OSError:
        pass

print(f"\n=== 归档 {len([m for m in moved if 'dup' in m[0]])} 个重复素材 ===")
print(f"=== 移动 {len([m for m in moved if 'dup' not in m[0]])} 个归类素材 ===")
print(f"=== 重命名 {len(renamed)} 个 preview-only ===")
for kind, f, dst in moved:
    if "dup" in kind:
        print(f"  [归档] {f.name} -> {dst.parent.name}/{dst.name}")
