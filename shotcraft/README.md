# Shotcraft · 镜头语言参考卡库

> VideoForgeSuite 的「镜头语言层」：152 张电影感镜头配方卡 + 可复用运镜组件 + 声音设计规范。
> 它回答的问题是：**每句口播/每个段落，画面应该怎么"拍"。**

## 它在 VideoForgeSuite 里的位置

```
文案定段落 ──► 素材库点单（风格/组件/转场） ──► 镜头卡点运镜（本库） ──► 引擎出片
                    ↑ 素材决定"长什么样"           ↑ 本库决定"怎么动"
```

- **镜头卡**（`references/shots/`）：10 大类 152 张——运镜 / 转场 / 文字 / 开场 / 收尾 / 节奏 / 数据 / 交互 / UI 入场 / 特效。每张卡 = 一句话 + 适用场景 + 动效核心 + 参数表 + 已知坑 + demo 路径。素材库「风格 → 镜头卡」分类下可浏览。
- **运镜组件**（`assets/lib/`）：PageCam（2.5D 页面运镜）/ ClipCard（实拍片段包裹）/ Caption / FlashCut / DigitRoll / VerticalTicker + motion/rand/shake 工具函数。已集成进 Remotion 引擎（`hermes-remotion/src/shotcraft/lib`）。
- **声音设计**（素材库「素材 → 音效/BGM」）：149 个 SFX 按事件分类（图章/警告/标签/转场…），配 `references/sound-design.md`、`references/music-beat-sync.md`。
- **制作流程**：`references/pipeline.md` 六阶段——产品理解 → 视觉方向 → 镜头映射 → 分镜 → 素材采集 → 制作+终检。
- **Demo 源码**（`demos/`）：每张卡都有可跑的 Remotion 实现，直接抄参数。

## 使用方式（AI 工作流）

1. 读口播稿，按句子/段落切分功能（hook / 讲解 / 强调 / 转折 / CTA）
2. 每段查镜头卡：功能段名 → 候选卡 → 按能量与节奏选型，登记运镜预算（1 动作 + 1 运镜 + 1 环境）
3. 素材、镜头、声音三者对齐到同一时间轴（timings）
4. 出片后按 video-aesthetics 技能的 pre-flight 矩阵抽帧自审

## 来源与致谢（Attribution）

本卡库的镜头配方体系参考并收录自社区开源项目 **[video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)**（原作者 Vincent Wei），在此致谢。收录内容（`references/`、`demos/`、`assets/lib/`、`gallery/`）保留原作署名，详见 [references/shots/ATTRIBUTION.md](references/shots/ATTRIBUTION.md) 与根目录 LICENSE。

VideoForgeSuite 在其上做了**本地化工程**：
- 摄取为素材库可浏览分类（镜头卡 HTML 化、SFX/BGM 入库）
- 运镜组件改造集成（PageCam → ClipCam 视频片段版，接入 Remotion 渲染管线）
- 与 video-aesthetics 审美技能（三旋钮/禁令/自审）和三引擎架构打通，形成完整制作闭环

License：原收录部分遵循其原许可；VideoForgeSuite 本地化部分 MIT。
