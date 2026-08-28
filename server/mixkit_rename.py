# -*- coding: utf-8 -*-
"""解析 mixkit 分类页 HTML，构建 id->标题 映射，重命名已下载素材"""
import re, os, pathlib, html as htmllib

SRV = pathlib.Path(r"D:\VideoForgeSuite\server")
GEN = pathlib.Path(r"D:\VideoForgeSuite\materials\generated")

id2title = {}
for page in SRV.glob("mixkit_*.html"):
    txt = page.read_text(encoding="utf-8", errors="ignore")
    alts = re.findall(r'alt="([^"]{3,90})"', txt)
    vids = re.findall(r'https://assets\.mixkit\.co/videos/(\d+)/\d+-720\.mp4', txt)
    # img alt 通常与 video id 顺序对应；保守起见：把 alt 关联到最近的下一个 vid 前的 id
    # 简化：vid 顺序与 alt 顺序基本一致（每个视频卡片一个 alt 一个 video）
    for alt, vid in zip(alts, vids):
        alt = htmllib.unescape(alt).strip()
        if vid not in id2title:
            id2title[vid] = alt
        else:
            if len(alt) < len(id2title[vid]):
                id2title[vid] = alt

def slug(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:60]

renamed = 0
for f in sorted(GEN.glob("mixkit_*.mp4")):
    vid = f.stem.replace("mixkit_", "")
    if vid not in id2title:
        continue
    title = id2title[vid]
    newname = f"mixkit_{slug(title)}_{vid}.mp4"
    newpath = GEN / newname
    if f.name == newname:
        continue
    if not newpath.exists():
        f.rename(newpath)
    else:
        f.unlink()
    print(f"  {f.name} -> {newname}")
    renamed += 1

print(f"== 重命名 {renamed} 个 ==")
print("== 已映射标题 ==")
for vid, t in sorted(id2title.items()):
    print(f"  {vid}: {t}")
