# -*- coding: utf-8 -*-
"""
生成"框架组件"素材：真实的 React(CDN+htm, 无需构建) 与 Vue3(CDN global) 自包含 HTML。
放在 materials/widgets/fw_react 与 materials/widgets/fw_vue 下。
每个文件零外部图片依赖，背景为明亮辉光（缩略图清晰可见），可在 iframe/浏览器直接运行。
"""
import pathlib, math, random

OUT = pathlib.Path(r"D:\VideoForgeSuite\materials")
REACT_DIR = OUT / "widgets" / "fw_react"
VUE_DIR = OUT / "widgets" / "fw_vue"
REACT_DIR.mkdir(parents=True, exist_ok=True)
VUE_DIR.mkdir(parents=True, exist_ok=True)

# 内联第三方库（离线可用 / 不依赖 CDN，避免国内网络问题；也加快缩略图截图）
LIB_DIR = pathlib.Path(r"D:\VideoForgeSuite\server\_libs")
def _lib(name):
    return (LIB_DIR / name).read_text(encoding="utf-8").replace("</script>", "<\\/script>")
REACT_LIBS = ("<script>" + _lib("react.js") + "</script>\n"
              + "<script>" + _lib("react-dom.js") + "</script>\n"
              + "<script>" + _lib("htm.js") + "</script>")
VUE_LIBS = "<script>" + _lib("vue.js") + "</script>"

THEMES = {
    "neon":   ("#7C6CF5", "#29D3E6", "#FF5C8A"),
    "aurora": ("#5B8CFF", "#7C6CF5", "#29D3E6"),
    "sunset": ("#FF6B6B", "#FFA552", "#FFD166"),
    "matrix": ("#2ECC71", "#23D5AB", "#A8FF60"),
    "cyber":  ("#00E5FF", "#FF00E5", "#7C4DFF"),
    "gold":   ("#FFD24A", "#FFA000", "#FFF176"),
    "ice":    ("#80D8FF", "#00B0FF", "#E1F5FE"),
    "rose":   ("#FF80AB", "#FF4081", "#F8BBD0"),
}

def bg_grad(a, b, c):
    return (f"radial-gradient(120% 120% at 18% 8%, {a}cc 0%, transparent 55%),"
            f"radial-gradient(120% 120% at 86% 92%, {b}bb 0%, transparent 55%),"
            f"radial-gradient(120% 120% at 50% 50%, {c}99 0%, transparent 62%),"
            f"linear-gradient(135deg,#1b1830,#241f3d)")

# ---- 公共 keyframes（所有组件复用） ----
KEYS = """
@keyframes spin {to{transform:rotate(360deg)}}
@keyframes floaty {0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
@keyframes pulseGlow {0%,100%{filter:drop-shadow(0 0 10px #fff6)}50%{filter:drop-shadow(0 0 26px #fff)}}
@keyframes riseIn {from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes swirl {to{transform:rotate(360deg)}}
@keyframes shimmer {0%{background-position:-200% 0}100%{background-position:200% 0}}
"""

# ====================== REACT 组件模板 ======================
# 每个 inner 引用变量 A/B/C（由 const A=__A__ 注入）。使用 htm 的 html`...` 语法。

REACT_BTN = """
function App(){
  const [h,setH]=React.useState(false);
  return html`<button onMouseEnter=${()=>setH(true)} onMouseLeave=${()=>setH(false)}
    style=${{padding:'20px 48px',fontSize:'24px',fontWeight:800,color:'#fff',border:'none',borderRadius:'18px',
      background:`linear-gradient(135deg, ${A}, ${B})`,
      boxShadow: h?`0 0 46px ${A}`:`0 0 20px ${B}66`,
      transform: h?'scale(1.08)':'scale(1)', transition:'all .3s cubic-bezier(.2,.8,.2,1)', cursor:'pointer',
      letterSpacing:'1px'}}>✦ Get Started</button>`;
}"""

REACT_CARD3D = """
function App(){
  const ref=React.useRef(null); const [t,setT]=React.useState({x:0,y:0});
  const onMove=e=>{const r=ref.current.getBoundingClientRect();
    const px=(e.clientX-r.left)/r.width-0.5, py=(e.clientY-r.top)/r.height-0.5;
    setT({x:py*-16,y:px*16});};
  const reset=()=>setT({x:0,y:0});
  return html`<div ref=${ref} onMouseMove=${onMove} onMouseLeave=${reset}
    style=${{width:'300px',height:'200px',borderRadius:'22px',transform:`perspective(800px) rotateX(${t.x}deg) rotateY(${t.y}deg)`,
      transition:'transform .12s ease',background:`linear-gradient(135deg, ${A}, ${B})`,
      boxShadow:`0 24px 60px ${A}55`,display:'flex',alignItems:'center',justifyContent:'center',
      color:'#fff',fontSize:'26px',fontWeight:800,textShadow:'0 2px 12px #0006'}}>
    3D Tilt Card</div>`;
}"""

REACT_BLACKHOLE = """
function App(){
  const rings=[]; for(let i=0;i<5;i++){const s=40+i*34;
    rings.push(html`<div key=${i} style=${{position:'absolute',width:s+'px',height:s+'px',borderRadius:'50%',
      border:`2px solid ${C}`,opacity:0.8-i*0.12,
      animation:`swirl ${6+i*2}s linear infinite`,boxShadow:`0 0 24px ${C}88`}}/>`);}
  return html`<div style=${{position:'relative',width:'260px',height:'260px',display:'flex',alignItems:'center',justifyContent:'center'}}>
    ${rings}
    <div style=${{width:'46px',height:'46px',borderRadius:'50%',background:`radial-gradient(circle,${A},#000)`,boxShadow:`0 0 40px ${A}`}}/>
  </div>`;
}"""

REACT_DNA = """
function App(){
  const n=22, cols=[];
  for(let i=0;i<n;i++){const ang=i*0.5; const x=Math.cos(ang)*70; const y=(i-n/2)*9;
    const r=Math.sin(ang)*70;
    cols.push(html`<div key=${'l'+i} style=${{position:'absolute',left:`calc(50% + ${x}px)`,top:`calc(50% + ${y}px)`,
      width:'14px',height:'14px',borderRadius:'50%',background:${A},transform:`translate(-50%,-50%)`,boxShadow:`0 0 12px ${A}`,animation:`floaty ${3+ (i%3)}s ease-in-out ${i*0.05}s infinite`}}/>`);
    cols.push(html`<div key=${'r'+i} style=${{position:'absolute',left:`calc(50% + ${-x}px)`,top:`calc(50% + ${y}px)`,
      width:'14px',height:'14px',borderRadius:'50%',background:${B},transform:`translate(-50%,-50%)`,boxShadow:`0 0 12px ${B}`,animation:`floaty ${3+(i%3)}s ease-in-out ${i*0.05}s infinite`}}/>`);
    cols.push(html`<div key=${'b'+i} style=${{position:'absolute',left:`calc(50% + ${x}px)`,top:`calc(50% + ${y}px)`,width:'2px',height:'2px'}}/>`);}
  return html`<div style=${{position:'relative',width:'220px',height:'260px',animation:'spin 18s linear infinite'}}>${cols}</div>`;
}"""

REACT_TORNADO = """
function App(){
  const segs=[]; for(let i=0;i<10;i++){const w=30+i*22; const y=i*22;
    segs.push(html`<div key=${i} style=${{position:'absolute',left:'50%',top:y+'px',width:w+'px',height:'14px',
      marginLeft:(-w/2)+'px',borderRadius:'12px',background:`linear-gradient(90deg,${A},${B})`,
      opacity:0.85-i*0.05,animation:`swirl ${5+(i%3)}s linear infinite`,boxShadow:`0 0 18px ${A}77`}}/>`);}
  return html`<div style=${{position:'relative',width:'260px',height:'240px'}}>${segs}</div>`;
}"""

REACT_GLOBE = """
function App(){
  const lines=[]; for(let i=0;i<10;i++){const r=110-i*8;
    lines.push(html`<div key=${i} style=${{position:'absolute',left:'50%',top:'50%',width:r*2+'px',height:r*2+'px',
      marginLeft:(-r)+'px',marginTop:(-r)+'px',borderRadius:'50%',border:`1.5px solid ${B}`,opacity:0.5,
      transform:'rotateX(70deg)'}}/>`);}
  const dots=[]; for(let i=0;i<14;i++){const a=i/14*Math.PI*2; const x=Math.cos(a)*90; const z=Math.sin(a)*90;
    dots.push(html`<div key=${'d'+i} style=${{position:'absolute',left:`calc(50% + ${x}px)`,top:`calc(50% + ${z*0.4}px)`,
      width:'10px',height:'10px',borderRadius:'50%',background:${C},boxShadow:`0 0 12px ${C}`,transform:'translate(-50%,-50%)'}}/>`);}
  return html`<div style=${{position:'relative',width:'240px',height:'240px',animation:'spin 14s linear infinite'}}>
    ${lines}${dots}</div>`;
}"""

REACT_TEXTREVEAL = """
function App(){
  const txt="FRAMEWORK"; const ch=txt.split('').map((c,i)=>html`<span key=${i} style=${{display:'inline-block',
    animation:`riseIn .6s cubic-bezier(.2,.8,.2,1) ${i*0.06}s both`,color:i%2?${A}:${B},
    fontSize:'46px',fontWeight:900,textShadow:`0 0 18px ${A}88`}}>${c}</span>`);
  return html`<div style=${{display:'flex',gap:'4px'}}>${ch}</div>`;
}"""

REACT_GRID = """
function App(){
  const cells=[]; for(let i=0;i<25;i++){cells.push(html`<div key=${i} style=${{width:'34px',height:'34px',borderRadius:'9px',
    background:`linear-gradient(135deg,${A},${B})`,animation:`pulseGlow 2s ease-in-out ${(i%5)*0.12}s infinite`,
    boxShadow:`0 0 14px ${A}55`}}/>`);}
  return html`<div style=${{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:'10px'}}>${cells}</div>`;
}"""

REACT_PARTICLES = """
function App(){
  const ps=[]; random.seed=1; for(let i=0;i<28;i++){const x=random()*100,y=random()*100,s=4+random()*10,d=2+random()*3;
    ps.push(html`<div key=${i} style=${{position:'absolute',left:x+'%',top:y+'%',width:s+'px',height:s+'px',borderRadius:'50%',
      background:i%2?${A}:${C},animation:`floaty ${d}s ease-in-out ${i*0.07}s infinite`,boxShadow:`0 0 12px ${A}88`,opacity:0.9}}/>`);}
  return html`<div style=${{position:'relative',width:'280px',height:'220px'}}>${ps}</div>`;
}"""
import random as _r
REACT_PARTICLES = REACT_PARTICLES.replace("random.seed=1;","_r.seed(7);").replace("random()","_r.random()")

REACT_ACCORDION = """
function App(){
  const [open,setOpen]=React.useState(0);
  const items=[['智能编排','把 Remotion / HyperFrames / H3 三引擎统一调度'],
              ['实时预览','右侧抽屉静音自动播放，HTML 用 iframe 内嵌'],
              ['批量导出','支持 4K / 竖屏 / 横屏多规格输出']];
  return html`<div style=${{width:'320px',display:'flex',flexDirection:'column',gap:'10px'}}>
    ${items.map((it,i)=>html`<div key=${i} style=${{borderRadius:'14px',overflow:'hidden',
      background:`linear-gradient(135deg,${A}22,${B}22)`,border:`1px solid ${A}55`}}>
      <button onClick=${()=>setOpen(open===i?-1:i)} style=${{width:'100%',padding:'14px 18px',background:'transparent',
        border:'none',color:'#fff',fontSize:'16px',fontWeight:700,cursor:'pointer',textAlign:'left'}}>${it[0]}</button>
      ${open===i?html`<div style=${{padding:'0 18px 16px',color:'#fff9',fontSize:'14px'}}>${it[1]}</div>`:null}
    </div>`)}
  </div>`;
}"""

REACT_TEMPLATES = [
    ("btn", REACT_BTN), ("card3d", REACT_CARD3D), ("blackhole", REACT_BLACKHOLE),
    ("dna", REACT_DNA), ("tornado", REACT_TORNADO), ("globe", REACT_GLOBE),
    ("text", REACT_TEXTREVEAL), ("grid", REACT_GRID), ("particles", REACT_PARTICLES),
    ("accordion", REACT_ACCORDION),
]

REACT_WRAP = """<!doctype html><html lang=zh><head><meta charset=utf-8>
<style>html,body{margin:0;height:100%}body{background:__BG__;display:flex;align-items:center;justify-content:center;
font-family:'Segoe UI',system-ui,-apple-system,sans-serif;overflow:hidden}
#app{width:100%;height:100%;display:flex;align-items:center;justify-content:center}__KEYS__</style></head>
<body><div id=app></div>
__REACT_LIBS__
<script>
const html=htm.bind(React.createElement);
const A=__A__,B=__B__,C=__C__;
__INNER__
const root=ReactDOM.createRoot(document.getElementById('app'));
root.render(html`<${App}/>`);
</script></body></html>"""

def react_file(name, inner, a, b, c):
    s = REACT_WRAP
    s = s.replace("__REACT_LIBS__", REACT_LIBS)
    s = s.replace("__BG__", bg_grad(a, b, c)).replace("__KEYS__", KEYS)
    s = s.replace("__INNER__", inner)
    s = s.replace("__A__", a).replace("__B__", b).replace("__C__", c)
    return s

# ====================== VUE 组件模板 ======================
VUE_COUNTER = """
const {createApp,ref,onMounted}=Vue;
createApp({
  setup(){const n=ref(0); onMounted(()=>{let i=0;const t=setInterval(()=>{n.value=i++;if(i>60)clearInterval(t);},35);});
    return {n};},
  template:`<div style="color:#fff;font-size:72px;font-weight:900;text-shadow:0 0 24px __C__">__CUR__{{n}}</div>`
}).mount('#app');"""

VUE_TILT = """
const {createApp,ref,onMounted}=Vue;
createApp({
  setup(){const t=ref({x:0,y:0});const onMove=e=>{const el=e.currentTarget.getBoundingClientRect();
    t.value={x:((e.clientX-el.left)/el.width-0.5)*-16,y:((e.clientY-el.top)/el.height-0.5)*16};};
    const reset=()=>t.value={x:0,y:0};return {t,onMove,reset};},
  template:`<div @mousemove="onMove" @mouseleave="reset"
    :style="{width:'300px',height:'200px',borderRadius:'22px',transform:`perspective(800px) rotateX(${t.x}deg) rotateY(${t.y}deg)`,
      transition:'transform .12s ease',background:'linear-gradient(135deg, __A__, __B__)',
      boxShadow:'0 24px 60px __A__55',display:'flex',alignItems:'center',justifyContent:'center',
      color:'#fff',fontSize:'26px',fontWeight:800}">Vue 3D Tilt</div>`
}).mount('#app');"""

VUE_RING = """
const {createApp,ref,onMounted}=Vue;
createApp({
  setup(){const p=ref(0);onMounted(()=>{let i=0;const t=setInterval(()=>{p.value=i;i++;if(i>100)clearInterval(t);},25);});return {p};},
  template:`<div style="position:relative;width:180px;height:180px;display:flex;align-items:center;justify-content:center">
    <svg width="180" height="180" viewBox="0 0 180 180" style="transform:rotate(-90deg)">
      <circle cx="90" cy="90" r="78" fill="none" stroke="#ffffff22" stroke-width="14"/>
      <circle cx="90" cy="90" r="78" fill="none" stroke="__B__" stroke-width="14" stroke-linecap="round"
        :stroke-dasharray="490" :stroke-dashoffset="490-(490*p/100)"/>
    </svg>
    <div style="position:absolute;color:#fff;font-size:40px;font-weight:900">{{p}}%</div></div>`
}).mount('#app');"""

VUE_BURST = """
const {createApp,ref}=Vue;
createApp({
  setup(){const burst=ref(false);const go=()=>{burst.value=true;setTimeout(()=>burst.value=false,600);};return {burst,go};},
  template:`<div style="position:relative;display:flex;align-items:center;justify-content:center">
    <button @click="go" style="padding:18px 44px;font-size:22px;font-weight:800;color:#fff;border:none;border-radius:16px;
      background:'linear-gradient(135deg, __A__, __C__)',cursor:pointer;box-shadow:'0 0 30px __A__'">点击迸发 ✦</button>
    <div v-if="burst" v-for="n in 12" :key="n"
      :style="{position:'absolute',width:'10px',height:'10px',borderRadius:'50%',background:'__C__',
        animation:'floaty 0.6s ease-out forwards',transform:`rotate(${n*30}deg) translateY(-60px)`}"></div>
  </div>`
}).mount('#app');"""

VUE_TEMPLATES = [
    ("counter", VUE_COUNTER), ("tilt", VUE_TILT), ("ring", VUE_RING), ("burst", VUE_BURST),
]

VUE_WRAP = """<!doctype html><html lang=zh><head><meta charset=utf-8>
<style>html,body{margin:0;height:100%}body{background:__BG__;display:flex;align-items:center;justify-content:center;
font-family:'Segoe UI',system-ui,sans-serif;overflow:hidden}
#app{width:100%;height:100%;display:flex;align-items:center;justify-content:center}__KEYS__</style></head>
<body><div id=app></div>
__VUE_LIB__
<script>
__INNER__
</script></body></html>"""

def vue_file(name, inner, a, b, c):
    s = VUE_WRAP
    s = s.replace("__VUE_LIB__", VUE_LIBS)
    s = s.replace("__BG__", bg_grad(a, b, c)).replace("__KEYS__", KEYS)
    # inner 中 __A__/__B__/__C__ 注入
    inner2 = inner.replace("__A__", a).replace("__B__", b).replace("__C__", c)
    s = s.replace("__INNER__", inner2)
    return s

# ====================== 生成 ======================
# 去重：每种组件只生成 1 个文件（不再 8 配色克隆），并按模板轮换配色，保证彼此不重复。
ARCH = pathlib.Path(r"D:\VideoForgeSuite\_spam_archive")
ARCH.mkdir(parents=True, exist_ok=True)
def _archive_dir(d):
    if not d.exists():
        return
    for f in d.iterdir():
        if f.is_file() and f.suffix.lower() == ".html":
            try:
                f.rename(ARCH / (d.name + "_" + f.name))
            except Exception:
                pass
_archive_dir(REACT_DIR)
_archive_dir(VUE_DIR)

count = 0
theme_items = list(THEMES.items())
for i, (tname, inner) in enumerate(REACT_TEMPLATES):
    th, (a, b, c) = theme_items[i % len(theme_items)]
    fp = REACT_DIR / f"react_{tname}.html"
    fp.write_text(react_file(tname, inner, a, b, c), encoding="utf-8")
    count += 1
for i, (tname, inner) in enumerate(VUE_TEMPLATES):
    th, (a, b, c) = theme_items[i % len(theme_items)]
    fp = VUE_DIR / f"vue_{tname}.html"
    fp.write_text(vue_file(tname, inner, a, b, c), encoding="utf-8")
    count += 1

print(f"generated framework components (deduped, 1 per template): {count}")
print("react:", REACT_DIR, "vue:", VUE_DIR)
