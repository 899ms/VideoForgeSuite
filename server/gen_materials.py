#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoForgeSuite - 批量生成动效/字幕素材（ffmpeg lavfi 程序化出片）
每条素材 1280x720 / 30fps / 5s，落进 materials/generated
零模型权重依赖，秒级出片。
"""
import subprocess, os, pathlib, sys

FFMPEG = r"C:\ffmpeg\ffmpeg.exe"
OUT = pathlib.Path(r"D:\VideoForgeSuite\materials\generated")
TXT = pathlib.Path(r"D:\VideoForgeSuite\server\txt")
TXT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# drawtext 字体（中英），filter 内盘符冒号需转义
FONT = r"C\:/Windows/Fonts/simhei.ttf"

def wtext(name, content):
    p = TXT / name
    p.write_text(content, encoding="utf-8")
    return str(p).replace("\\", "/").replace(":", "\\:")

def run(name, args, dur=5):
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error"] + args + \
          ["-t", str(dur), "-r", "30", "-pix_fmt", "yuv420p", str(OUT / name)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT {name}"); return False
    p = OUT / name
    ok = p.exists() and p.stat().st_size > 5000
    if ok:
        print(f"  OK  {name}  {p.stat().st_size//1024}KB")
    else:
        print(f"  FAIL {name}")
        if r.stderr: print("      " + r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")
    return ok

def main():
    jobs = []

    # ============ 动效类 ============
    # 1 辉光粒子
    jobs.append(("fx_glow_particles.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x07070d:c1=0x10102a:c2=0x1a1a3e:d=5:speed=0.05",
        "-f", "lavfi", "-i", "nullsrc=s=1280x720,noise=alls=18:allf=t+u",
        "-filter_complex", "[0:v][1:v]blend=screen,eq=brightness=0.06:saturation=1.4,gblur=sigma=1.2",
    ]))

    # 2 扫描线扫过
    jobs.append(("fx_scanline_sweep.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x06070a:c1=0x103a5c:x0=0:y0=0:x1=1280:y1=720:d=5:speed=0.04",
        "-vf", "drawbox=x='mod(t*400,iw)':y=0:w=2:h=ih:color=0x00e5ff@0.6,"
               "drawbox=x='mod(t*400+60,iw)':y=0:w=1:h=ih:color=0xff2d75@0.35,"
               "drawgrid=w=160:h=90:t=1:color=white@0.03,eq=brightness=0.02",
    ]))

    # 3 RGB 分离（rgbashift 不支持表达式，用静态偏移+亮度脉动）
    jobs.append(("fx_rgb_split.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x0a0a16:c1=0x2a1a4a:c2=0x16304a:d=5:speed=0.05",
        "-vf", "format=gbrp,rgbashift=rh=16:bh=-16,format=yuv420p,"
               "eq=brightness='0.03+0.04*sin(2*PI*t*1.2)':saturation=1.4",
    ]))

    # 4 霓虹边框
    jobs.append(("fx_neon_border.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x06070a:c1=0x0e1020:d=5:speed=0.03",
        "-filter_complex",
        "[0:v]split[a][b];"
        "[a]drawbox=x=44:y=44:w=iw-88:h=ih-88:color=0x00e5ff@0.9:t=3,"
        "drawbox=x=40:y=40:w=iw-80:h=ih-80:color=0x00e5ff@0.25:t=10,"
        "drawbox=x=64:y=64:w=iw-128:h=ih-128:color=0xff2d75@0.35:t=2[aa];"
        "[b]gblur=sigma=14[bb];"
        "[aa][bb]blend=screen",
    ]))

    # 5 VHS 噪点
    jobs.append(("fx_vhs_noise.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x0a0a12:c1=0x2a2a3e:d=5:speed=0.04",
        "-vf", "noise=alls=24:allf=t+u,hue=H='8*sin(2*PI*t*1.5)',vignette=PI/5,"
               "drawbox=x='mod(t*500,iw)':y=0:w=10:h=ih:color=white@0.12,eq=saturation=0.85",
    ]))

    # 6 极光
    jobs.append(("fx_aurora.mp4", [
        "-f", "lavfi", "-i",
        "gradients=s=1280x720:c0=0x001f3f:c1=0x00e5ff:c2=0x2d0075:c3=0x06070a:nb_colors=4:d=5:speed=0.05",
        "-vf", "gblur=sigma=22,eq=saturation=1.6:brightness=0.03,noise=alls=6",
    ]))

    # 7 网格脉冲
    jobs.append(("fx_grid_pulse.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x06070a:c1=0x0e1230:d=5:speed=0.02",
        "-vf", "drawgrid=w=80:h=80:t=1:color=0x00e5ff@0.22,"
               "drawgrid=w=16:h=16:t=1:color=white@0.04,"
               "eq=brightness='0.04+0.05*sin(2*PI*t*1.5)':saturation=1.3",
    ]))

    # 8 故障闪烁
    jobs.append(("fx_glitch.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x0a0a14:c1=0x1a1024:d=5:speed=0.06",
        "-vf", "noise=alls=28:allf=t+u,"
               "format=gbrp,rgbashift=rh='10*random(1)':bh='10*random(1)',format=yuv420p,"
               "eq=contrast=1.25",
    ]))

    # 9 光斑
    jobs.append(("fx_bokeh.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x0a0a14:c1=0x3a1a5a:c2=0x0a2a3a:d=5:speed=0.04",
        "-filter_complex", "[0:v]split[a][b];[b]gblur=sigma=18[bb];[a][bb]blend=screen,eq=brightness=0.08",
    ]))

    # 10 缩放脉冲
    jobs.append(("fx_zoom_pulse.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1920x1080:c0=0x06070a:c1=0x14203a:d=5:speed=0.02",
        "-vf", "zoompan=z='1+0.12*sin(2*PI*on/150)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30",
    ]))

    # ============ 字幕类 ============
    t1 = wtext("s1.txt", "这里是口播字幕，逐字出现的效果")
    jobs.append(("sub_typewriter.mp4", [
        "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
        "-vf",
        "drawbox=x=0:y=h-200:w=iw:h=200:color=0x101018@0.88:t=fill,"
        "drawbox=x=0:y=h-200:w=6:h=200:color=0x00e5ff:t=fill,"
        f"drawtext=textfile='{t1}':fontfile='{FONT}':fontcolor=white:fontsize=46:"
        "x=80:y=h-130:alpha='if(lt(t,0.4),0,1)',"
        "drawbox=x=460:y=h-140:w=24:h=52:color=0x00e5ff@0.9:t=fill:enable='lt(mod(t,0.7),0.35)'",
    ]))

    t2 = wtext("s2.txt", "每一个瞬间都值得被看见")
    jobs.append(("sub_glowing_caption.mp4", [
        "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
        "-filter_complex",
        "[0:v]split[a][b];"
        f"[b]drawtext=textfile='{t2}':fontfile='{FONT}':fontcolor=white:fontsize=64:"
        "x=(w-text_w)/2:y=h-180:alpha='if(lt(t,0.6),0,min(t/0.6,1))',gblur=sigma=6,eq=brightness=0.4[bg];"
        f"[a]drawtext=textfile='{t2}':fontfile='{FONT}':fontcolor=white:fontsize=64:"
        "x=(w-text_w)/2:y=h-180:alpha='if(lt(t,0.6),0,min(t/0.6,1))'[fg];"
        "[bg][fg]blend=screen",
    ]))

    t3 = wtext("s3.txt", "张小明")
    t4 = wtext("s4.txt", "高级视觉设计师")
    jobs.append(("sub_lower_third.mp4", [
        "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
        "-vf",
        "drawbox=x=80:y='h-170+120*pow(max(0,1-min(t*1.5,1)),2)':w=560:h=110:color=0x0e1626@0.92:t=fill,"
        "drawbox=x=80:y='h-170+120*pow(max(0,1-min(t*1.5,1)),2)':w=8:h=110:color=0x00e5ff:t=fill,"
        f"drawtext=textfile='{t3}':fontfile='{FONT}':fontcolor=white:fontsize=44:"
        "x=110:y='h-150+120*pow(max(0,1-min(t*1.5,1)),2)':alpha='if(lt(t,0.5),0,1)',"
        f"drawtext=textfile='{t4}':fontfile='{FONT}':fontcolor=0x00e5ff:fontsize=30:"
        "x=112:y='h-90+120*pow(max(0,1-min(t*1.5,1)),2)':alpha='if(lt(t,0.8),0,1)'",
    ]))

    t5 = wtext("s5.txt", "制片人 | 导演 | 后期总监")
    jobs.append(("sub_rolling_credits.mp4", [
        "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
        "-vf",
        f"drawtext=textfile='{t5}':fontfile='{FONT}':fontcolor=white:fontsize=52:"
        "x=(w-text_w)/2:y='h+80-t*140':alpha=1,"
        "drawbox=x=0:y=0:w=iw:h=120:color=black@0.5:t=fill:enable='lt(t,0.3)'",
    ]))

    t6 = wtext("s6.txt", "VIDEOFORGE")
    jobs.append(("sub_title_zoom.mp4", [
        "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
        "-vf",
        f"drawtext=textfile='{t6}':fontfile='{FONT}':fontcolor=white:fontsize=120:"
        "x=(w-text_w)/2:y='(h-text_h)/2-40+40*pow(max(0,1-min(t/1.2,1)),2)':"
        "alpha='if(lt(t,0.3),0,min((t-0.3)/0.5,1))':"
        "shadowcolor=0x00e5ff:shadowx=0:shadowy=8",
    ]))

    t7 = wtext("s7.txt", "设计之美，在于克制")
    jobs.append(("sub_quote.mp4", [
        "-f", "lavfi", "-i", "color=black:s=1280x720:d=5",
        "-vf",
        "drawbox=x=0:y=h-260:w=10:h=180:color=0x00e5ff:t=fill,"
        f"drawtext=textfile='{t7}':fontfile='{FONT}':fontcolor=white:fontsize=56:"
        "x=70:y=h-220:alpha='if(lt(t,1),t/1,if(gt(t,4),(5-t)/1,1))'",
    ]))

    # ============ 转场类（lavfi 合成） ============
    jobs.append(("tr_crosszoom.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x00e5ff:c1=0x06070a:x0=0:y0=0:x1=1280:y1=720:d=5:speed=0.1",
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x06070a:c1=0xff2d75:x0=1280:y0=0:x1=0:y1=720:d=5:speed=0.1",
        "-filter_complex",
        "[0:v]scale=1280:720,zoompan=z='1+min(on/25,1)*0.6':d=1:s=1280x720:fps=30[a];"
        "[1:v]scale=1280:720,zoompan=z='1.6-min(on/25,1)*0.6':d=1:s=1280x720:fps=30[b];"
        "[a][b]xfade=transition=fade:duration=1:offset=2",
    ]))

    jobs.append(("tr_swirl.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x00e5ff:c1=0x06070a:d=5",
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x06070a:c1=0xff2d75:d=5",
        "-filter_complex", "[0:v][1:v]xfade=transition=circleopen:duration=1:offset=2",
    ]))

    jobs.append(("tr_slide.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x06070a:c1=0x00e5ff:d=5",
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0xff2d75:c1=0x06070a:d=5",
        "-filter_complex", "[0:v][1:v]xfade=transition=slideleft:duration=1:offset=2",
    ]))

    jobs.append(("tr_zoomblur.mp4", [
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x0a0a16:c1=0x103a5c:d=5",
        "-f", "lavfi", "-i", "gradients=s=1280x720:c0=0x3a1a5a:c1=0x0a0a16:d=5",
        "-filter_complex", "[0:v][1:v]xfade=transition=fadewhite:duration=1:offset=2",
    ]))

    ok = 0
    for name, args in jobs:
        if run(name, args): ok += 1
    print(f"\n===== 完成：{ok}/{len(jobs)} 条生成成功 =====")

if __name__ == "__main__":
    main()
