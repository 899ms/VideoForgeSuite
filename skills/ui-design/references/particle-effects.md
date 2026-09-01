---
type: 技能
status: active
source: 抖音（清晨方白晓 + 蓝戈AI）
tags: [UI设计, VibeCoding, 动效, 粒子, 呼吸感, 环星]
date: 2026-08-30
---

# 环星呼吸粒子动效工作台

> VibeCoding大赏中热门的动效风格：环星旋转、呼吸光晕、粒子浮动。用于营造科技感、未来感、高级感的网页氛围。

## 第一层：目标层（所有 agent 必须达成）

### 效果目标
用代码实现环星旋转+呼吸光晕+粒子浮动的组合动效，营造高级科技感氛围。动效要自然流畅，不突兀，不抢内容风头。

### 验收标准
- [ ] 环星缓慢旋转（速度<10秒/圈，不眩晕）
- [ ] 光晕呼吸效果（亮度周期性变化，周期>3秒）
- [ ] 粒子缓慢浮动（速度慢，方向随机，不聚集）
- [ ] 三种动效组合协调，不互相干扰
- [ ] 背景动效不影响前景内容的可读性
- [ ] 性能流畅（60fps，不卡顿）

### 禁止事项
- 禁止动效速度过快（导致眩晕）
- 禁止光晕亮度过高（刺眼）
- 禁止粒子数量过多（影响性能和可读性）
- 禁止三种动效同时剧烈变化（视觉混乱）
- 禁止在内容区域上方有强烈动效（影响阅读）

## 第二层：实现层（参考，不强制）

### 原理
- **环星旋转**：用CSS `@keyframes rotate` 或SVG `<animateTransform>` 实现圆环的缓慢旋转
- **呼吸光晕**：用CSS `@keyframes pulse` 改变 `box-shadow` 或 `opacity` 实现光晕的呼吸效果
- **粒子浮动**：用Canvas或多个绝对定位的div，通过JS或CSS动画实现粒子的随机缓慢浮动

### 参考实现（CSS+SVG）

```html
<!-- 环星 -->
<div class="ring-star">
  <svg viewBox="0 0 400 400">
    <circle cx="200" cy="200" r="150" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1" stroke-dasharray="10 20"/>
    <circle cx="200" cy="200" r="120" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="5 15"/>
  </svg>
</div>

<!-- 呼吸光晕 -->
<div class="glow-orb"></div>

<!-- 粒子容器 -->
<div class="particles" id="particles"></div>

<style>
.ring-star {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation: rotate 60s linear infinite;
}
@keyframes rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.glow-orb {
  position: absolute;
  top: 50%; left: 50%;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(100,150,255,0.15) 0%, transparent 70%);
  animation: breathe 6s ease-in-out infinite;
}
@keyframes breathe {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
}

.particles { position: absolute; inset: 0; overflow: hidden; }
.particle {
  position: absolute;
  width: 3px; height: 3px;
  background: rgba(255,255,255,0.3);
  border-radius: 50%;
  animation: float 20s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(20px, -30px); }
  50% { transform: translate(-10px, -50px); }
  75% { transform: translate(-30px, -20px); }
}
</style>

<script>
// 生成粒子
const container = document.getElementById('particles');
for (let i = 0; i < 30; i++) {
  const p = document.createElement('div');
  p.className = 'particle';
  p.style.left = Math.random() * 100 + '%';
  p.style.top = Math.random() * 100 + '%';
  p.style.animationDelay = Math.random() * 20 + 's';
  p.style.animationDuration = (15 + Math.random() * 15) + 's';
  container.appendChild(p);
}
</script>
```

### 参考实现（Canvas高性能版）

```javascript
// Canvas粒子系统，性能更好，适合大量粒子
class ParticleSystem {
  constructor(canvas, count = 50) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 2 + 1,
        alpha: Math.random() * 0.3 + 0.1
      });
    }
  }
  update() {
    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;
    });
  }
  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.particles.forEach(p => {
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(255,255,255,${p.alpha})`;
      this.ctx.fill();
    });
  }
  animate() {
    this.update();
    this.draw();
    requestAnimationFrame(() => this.animate());
  }
}
```

## 第三层：替代思路（鼓励创新）

### 其他实现方式
- **Three.js**：用3D粒子系统实现更真实的空间感粒子
- **GSAP**：用GSAP的时间线精确控制三种动效的节奏
- **SVG滤镜**：用SVG的feTurbulence实现更有机的粒子效果

### 适用场景
- 简单背景动效 → CSS+SVG（轻量，性能好）
- 大量粒子/复杂效果 → Canvas（性能更好）
- 3D空间感粒子 → Three.js（效果最炫）
- 需要精确时间控制 → GSAP（节奏可控）

## 使用方法

1. **触发时机**：需要营造科技感、未来感、高级感氛围的网页背景
2. **操作步骤**：
   - 确定主色调（环星、光晕、粒子的颜色要和整体配色协调）
   - 选择实现方式（CSS/Canvas/Three.js，根据性能需求）
   - 调整参数（旋转速度、呼吸周期、粒子数量、浮动速度）
   - 确保前景内容可读（动效强度不能影响内容）
3. **输入输出**：
   - 输入：主色调、动效强度、性能要求
   - 输出：可直接使用的环星呼吸粒子动效背景代码

## 应用场景

- 科技公司官网背景
- AI产品落地页
- 创意作品集网站
- VibeCoding风格网页
- 视频制作中的动态背景（HTML背景层）

## 常用组合

- [[交互动效术语集]] + 本技能 = 理解动效术语后实现对应效果
- [[6种高级图片交互动效]] + 本技能 = 背景动效+前景图片交互
- [[配色方案库]] + 本技能 = 确定配色后调整动效颜色
- [[视频制作大师SKILL]] + 本技能 = 做视频时用HTML做动态背景

## 验证状态

active（CSS+SVG实现已验证；Canvas/Three.js实现待验证）

## 关联

- 相关：[[呼吸感粒子动效工作台]]（Obsidian UI中的应用）
- 相关：[[交互动效术语集]]
- 扩展：[[VibeCoding宝藏网站合集]]（更多动效参考）

## 来源

- 抖音《「VibeCoding大赏」环星 呼吸 粒子动效工...》清晨方白晓 https://v.douyin.com/uYuG5Zo5ujs/
- 抖音《vibecoding大赏》蓝戈AI https://v.douyin.com/dk_t927ZgNA/
- 整理时间：2026-08-30
