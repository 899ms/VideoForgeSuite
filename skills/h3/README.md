# H3 导演技能包 · L3 引擎提示词层

> VideoForgeSuite L3 引擎（MiniMax H3 本地视频生成）的**导演大脑**：
> 1 个结构化提示词技能 + 8 个风格化整片生成流程，让"一句话 → 分镜 → 成片"可控、可复现。

## 它在工作台里的位置

```
文案 ──► 素材库点单 ──► 镜头卡点运镜 ──► ★ 本包：按 H3 提示词语法写分镜 ──► L3 引擎出片
                                            (h3-prompt-writing + 风格生成器)
```

## 技能清单

| 技能 | 用途 |
|---|---|
| **h3-prompt-writing** | 核心。把任何需求改写成 H3 结构化提示词（`integrated_multimodal_description` + `overall_soundscape` + `non_diegetic_music`），覆盖全部 5 种生成模式（文生视频 / 首帧 / 首尾帧 / 尾帧 / 全参考 Ref2VA），含 5 模式提示词指南 |
| 3d-animation-short-generator | 3D 风格动画短片全流程 |
| brand-promo-video-generator | 品牌宣传片（产品图 + brief） |
| co-op-game-intro-generator | 联机游戏开场 |
| handdrawn-live-video-generator | 手绘+实拍混合口播 |
| minimalist-product-ad-generator | 极简产品广告（卡点字幕） |
| music-video-subtitle-generator | 带字幕音乐视频 |
| paper-collage-explainer-generator | 纸片拼贴风科普 |
| papercraft-stop-motion-explainer | 定格动画科普（角色/场景连续性） |

每个风格技能都是完整制作流程：**brief → 大纲 → 角色卡 → 分镜规划 → 逐镜头生成 → 拼装 → 审查**，自带角色一致性与场景连续性保障，与工作台的"点单式"理念天然契合。

## 工作台集成约定

1. **分镜提示词一律走 h3-prompt-writing 的结构化格式**——`vf_storyboard.py` 生成的 storyboard.json 在送入 L3 引擎前按此格式组装
2. **角色一致性**：Ref2VA 模式最多 9 张参考图（角色设定图由素材库/生图管线提供），配合首尾帧锚定实现"角色锁 + 镜头接"双保险
3. **帧数规范**：H3 训练帧区间 96–360 帧（4–15 秒），分镜单段应落在此区间内（17n+5 对齐）
4. 风格技能与素材库风格分类对位：选了"手绘白板"风格 → 按对应生成器的流程走

## 许可说明

本技能包收录自 MiniMax H3 官方模型仓库（随开源权重分发），遵循 [MiniMax H3 Community License]；VideoForgeSuite 的集成约定与管线打通部分为原创。
