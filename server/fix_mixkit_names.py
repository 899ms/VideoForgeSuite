#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 mixkit 文件命名（tr 删字符事故）：按原始 URL 列表重新下载正确 id 命名的文件，
删除被破坏命名的残留。"""
import os, re, pathlib, urllib.request, hashlib

GEN = pathlib.Path(r"D:\VideoForgeSuite\materials\generated")
SRV = pathlib.Path(r"D:\VideoForgeSuite\server")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"

# 1) 收集原始 URL（完整 id）
urls = []
for f in ("mixkit_urls.txt", "mixkit_urls2.txt"):
    p = SRV / f
    if p.exists():
        urls += p.read_text(encoding="utf-8").splitlines()
urls = sorted(set(u.strip() for u in urls if u.strip()))
print(f"原始 URL 总数: {len(urls)}")

# 2) 本地现有 mixkit 文件
local = sorted(GEN.glob("mixkit_*.mp4"))
print(f"本地 mixkit 文件: {len(local)}")

# 3) 被破坏命名（ID 里丢了 4/m/p）→ 特征：ID 很短且无法在原始 URL 中找到
bad = []
ok_keep = []
for f in local:
    stem = f.stem  # mixkit_xxx
    if "test" in stem:
        f.unlink()
        print(f"删除残留: {f.name}")
        continue
    if stem.startswith("mixkit_") and re.fullmatch(r"mixkit_[0-9]+", stem):
        vid = stem[len("mixkit_"):]
        if any(f"/{vid}/" in u for u in urls):
            ok_keep.append(f)
        else:
            bad.append(f)
    else:
        ok_keep.append(f)  # 真实标题命名的保留

print(f"命名正确保留: {len(ok_keep)}")
print(f"命名被破坏待重下: {len(bad)}")
for f in bad:
    print("  BAD:", f.name)

# 4) 按大小+md5 匹配原始 URL，重新下载
def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if len(data) < 200000:
        return False
    dest.write_bytes(data)
    return True

fixed = 0
for f in bad:
    size = f.stat().st_size
    h = hashlib.md5(f.read_bytes()).hexdigest()
    target = None
    for u in urls:
        vid = re.search(r"/(\d+)/\d+-720\.mp4$", u).group(1)
        tmp = GEN / f"__probe_{vid}.mp4"
        if tmp.exists():
            tmp.unlink()
        if not download(u, tmp):
            continue
        if tmp.stat().st_size == size and hashlib.md5(tmp.read_bytes()).hexdigest() == h:
            target = vid
            tmp.unlink()
            break
        tmp.unlink()
    if target:
        newname = GEN / f"mixkit_{target}.mp4"
        if not newname.exists():
            f.rename(newname)
            print(f"  修复: {f.name} -> {newname.name}")
        else:
            f.unlink()
            print(f"  去重: {f.name} (已存在 {newname.name})")
        fixed += 1
    else:
        print(f"  !! 无法匹配: {f.name}")

print(f"== 修复完成: {fixed}/{len(bad)} ==")
final = sorted(GEN.glob("mixkit_*.mp4"))
print(f"== 最终 mixkit 文件: {len(final)} ==")
for f in final:
    print("  ", f.name)
