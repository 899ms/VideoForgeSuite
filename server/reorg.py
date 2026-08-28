#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VideoForgeSuite — 素材库重构：按功能重新分类（dry-run / 执行）。"""
import os, shutil, sys, json

MAT = r"D:\VideoForgeSuite\materials"
DRY = "--go" not in sys.argv

# 具体文件名 -> (大类, 子类)
TRANS_SAMPLE = {
    "pro_transition_showcase_v5_preview.mp4": ("transitions", "转场样片"),
    "hand_flower_plus_transitions_v4_preview.mp4": ("transitions", "转场样片"),
}
HFX_STYLE = {
    "hfx_kinetic_type.mp4": ("styles", "HTML风格渲染"),
    "hfx_volumetric_rays.mp4": ("styles", "HTML风格渲染"),
    "hfx_text_scramble.mp4": ("styles", "HTML风格渲染"),
}
HFX_WIDGET = {
    "hfx_glowing_caption.mp4": ("widgets", "字幕条"),
    "hfx_typewriter_sub.mp4": ("widgets", "字幕条"),
    "hfx_swirl_transition.mp4": ("transitions", "HTML转视频转场"),
}

WIDGET_SUB = {
    "ui_501_typewriter_subtitle.html": "字幕条",
    "ui_502_glowing_caption.html": "字幕条",
    "ui_503_host_intro_box.html": "标题组件",
    "ui_504_quote_bubble.html": "标题组件",
    "ui_505_audio_bars.html": "音频可视化",
    "ui_506_data_chart_grow.html": "仪表盘数据",
    "ui_507_radar_scan.html": "HUD雷达",
    "ui_508_sonar_wave.html": "HUD雷达",
    "ui_509_speed_gauge.html": "仪表盘数据",
    "ui_510_circular_progress.html": "仪表盘数据",
    "ui_511_tech_hud_frame.html": "HUD边框",
    "ui_512_counting_numbers.html": "仪表盘数据",
}

IMPACT_SUB = {
    "impact_v5_401_kinetic_type.html": "文字动效",
    "impact_v5_402_ui_grid_scan.html": "赛博科技",
    "impact_v5_403_text_scramble.html": "文字动效",
    "impact_v5_404_impossible_shape.html": "极简几何",
    "impact_v5_405_tessellation_zoom.html": "极简几何",
    "impact_v5_406_wireframe_terrain.html": "赛博科技",
    "impact_v5_407_volumetric_rays.html": "赛博科技",
    "impact_v5_408_anamorphic_flare.html": "赛博科技",
    "impact_v5_409_bold_lightning.html": "赛博科技",
    "impact_v5_410_reaction_diffusion.html": "自然流体",
    "impact_v5_411_flow_field.html": "自然流体",
    "impact_v5_412_noise_landscape.html": "自然流体",
    "impact_v5_413_ink_splash.html": "国风金辉",
    "impact_v5_414_fire_vortex.html": "自然流体",
    "impact_v5_415_ocean_storm.html": "自然流体",
    "impact_v5_416_glass_fracture.html": "极简几何",
    "impact_v5_417_golden_bagua.html": "国风金辉",
    "impact_v5_418_flower_scatter_gather.html": "国风金辉",
    "impact_v5_419_flower_3d_bloom.html": "国风金辉",
    "impact_v5_420_flower_morph.html": "国风金辉",
}


def classify(top, name):
    n = name.lower()
    if top == "effects_html" and n.startswith("trans_t"):
        return ("transitions", "HTML转场")
    if top == "generated" and n.startswith("tr_"):
        return ("transitions", "视频转场")
    if name in TRANS_SAMPLE:
        return TRANS_SAMPLE[name]
    if name in HFX_WIDGET:
        return HFX_WIDGET[name]
    if top == "effects_html" and n.startswith("ui_"):
        return ("widgets", WIDGET_SUB.get(name, "UI组件"))
    if top == "generated" and n.startswith("fx_cv_"):
        # glitch_bars 归背景纹理，其余归组件图形
        if "glitch_bars" in n:
            return ("assets", "动态纹理")
        return ("widgets", "Canvas图形")
    if top == "generated" and n.startswith("sub_"):
        return ("widgets", "字幕条")
    if top == "effects_html" and n.startswith("impact_v5_"):
        return ("styles", IMPACT_SUB.get(name, "视觉冲击"))
    if name in HFX_STYLE:
        return HFX_STYLE[name]
    if top == "video":
        return ("styles", "Remotion样片")
    if top == "generated" and n.startswith("fx_txt_"):
        return ("styles", "文字入场")
    if top == "generated" and n.startswith("mixkit_"):
        return ("assets", "实拍素材")
    if "greenscreen" in n:
        return ("assets", "绿幕")
    if top == "generated":
        return ("assets", "动态纹理")
    return ("assets", "其他")


def main():
    src_roots = ["video", "effects_html", "generated"]
    plan = []
    for top in src_roots:
        d = os.path.join(MAT, top)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            fp = os.path.join(d, fn)
            if not os.path.isfile(fp):
                continue
            if fn.startswith("."):
                continue
            cat, sub = classify(top, fn)
            plan.append((fp, os.path.join(MAT, cat, sub, fn), cat, sub))
    # 打印计划
    by_cat = {}
    for _, dst, cat, sub in plan:
        by_cat.setdefault(cat, 0)
        by_cat[cat] += 1
    print("=== 迁移计划（%d 个文件）===" % len(plan))
    for c in ["styles", "widgets", "transitions", "assets"]:
        print(f"  {c}: {by_cat.get(c,0)}")
    print("\n--- 明细 ---")
    for fp, dst, cat, sub in plan:
        print(f"[{cat}/{sub}] {os.path.basename(fp)}  ->  {os.path.relpath(dst, MAT)}")

    if DRY:
        print("\n[DRY-RUN] 未执行移动。确认无误后加 --go 参数运行。")
        return

    # 执行
    moved = 0
    for fp, dst, cat, sub in plan:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.abspath(fp) != os.path.abspath(dst):
            shutil.move(fp, dst)
            moved += 1
    # 清理空目录
    for top in src_roots:
        d = os.path.join(MAT, top)
        try:
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
                print(f"已删除空目录: {top}")
        except OSError:
            pass
    print(f"\n[完成] 已移动 {moved} 个文件。")
    # 输出统计供核对
    print(json.dumps(by_cat, ensure_ascii=False))


if __name__ == "__main__":
    main()
