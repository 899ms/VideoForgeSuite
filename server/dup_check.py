#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""动效视频重复度检测：ffmpeg 抽 16x16 灰度中间帧 → 感知哈希 → 汉明距离分组"""
import subprocess, pathlib, struct

GEN = pathlib.Path(r"D:\VideoForgeSuite\materials\generated")
FFMPEG = r"C:\ffmpeg\ffmpeg.exe"

def frame_hashes(path, frames=(2, 3, 4)):
    """抽指定秒数位置的帧，scale 16x16 gray raw，返回感知哈希列表"""
    hashes = []
    for sec in frames:
        cmd = [FFMPEG, "-v", "error", "-i", str(path),
               "-ss", str(sec), "-frames:v", "1",
               "-vf", "scale=16:16,format=gray",
               "-f", "rawvideo", "-pix_fmt", "gray", "-"]
        try:
            raw = subprocess.run(cmd, capture_output=True, timeout=15).stdout
        except Exception:
            continue
        if len(raw) < 256:
            continue
        px = list(raw[:256])
        avg = sum(px) / len(px)
        bits = 0
        for i, v in enumerate(px):
            if v > avg:
                bits |= (1 << (i % 64))
        hashes.append(bits)
    return hashes

def hamming(a, b):
    return bin(a ^ b).count("1")

def main():
    vids = sorted(GEN.glob("fx_animate_*.mp4")) + sorted(GEN.glob("fx_magic_*.mp4"))
    print(f"待检测: {len(vids)} 条\n")

    sigs = {}
    for v in vids:
        sigs[v.name] = frame_hashes(v)
        print(f"  {v.name}: {len(sigs[v.name])} 帧指纹")

    # 两两比较（取所有帧对的最小汉明距离均值）
    pairs = []
    names = list(sigs.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = sigs[names[i]], sigs[names[j]]
            if not a or not b:
                continue
            dists = [hamming(x, y) for x in a for y in b]
            if not dists:
                continue
            avg = sum(dists) / len(dists)
            pairs.append((avg, names[i], names[j]))
    pairs.sort()

    print("\n=== 最相似的 20 对（距离越小越像，<20 视为高度重复）===")
    for d, a, b in pairs[:20]:
        flag = " ⚠️高度重复" if d < 20 else (" 🔸相近" if d < 30 else "")
        print(f"  {d:5.1f}  {a}  <->  {b}{flag}")

    print("\n=== 重复分组（距离<22 的连通组）===")
    groups = []
    used = set()
    for d, a, b in pairs:
        if d >= 22:
            break
        ga = next((g for g in groups if a in g), None)
        gb = next((g for g in groups if b in g), None)
        if ga is None and gb is None:
            groups.append({a, b})
        elif ga is not None and gb is None:
            ga.add(b)
        elif ga is None and gb is not None:
            gb.add(a)
        elif ga is not gb:
            ga |= gb
            groups.remove(gb)
    for g in groups:
        print("  组: " + " | ".join(sorted(g)))

if __name__ == "__main__":
    main()
