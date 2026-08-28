// render_diverse.mjs — 多样化动效渲染：不同文字×颜色×动画类 + 自写 Canvas 图形动效
// 产出真正有区分度的素材，避免"全都一样"
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9226;
const FPS = 20, FRAMES = 60, INTERVAL = 90, LOAD_WAIT = 600;
const FX = "D:\\VideoForgeSuite\\external_fx";
const OUTDIR = "D:\\VideoForgeSuite\\materials\\generated";
const TMP = "D:\\VideoForgeSuite\\server\\frames";
const FFMPEG = "C:\\ffmpeg\\ffmpeg.exe";

const animCss = fs.readFileSync(FX + "\\animate.css\\animate.css", "utf8");
const magicCss = fs.readFileSync(FX + "\\magic\\dist\\magic.css", "utf8");

// 风格主题（不同配色）
const THEMES = {
  cyan:   { bg: "#0a0a14", color: "#ffffff", glow: "#00e5ff" },
  pink:   { bg: "#140a0f", color: "#ffffff", glow: "#ff2d75" },
  gold:   { bg: "#14100a", color: "#fff8e1", glow: "#ffd700" },
  purple: { bg: "#0f0a16", color: "#ffffff", glow: "#a855f7" },
  green:  { bg: "#0a140a", color: "#eaffea", glow: "#00ff88" },
};

// 文字动画组合：动画类 x 中文词 x 主题（全部中文）
const TEXT_JOBS = [
  // animate.css 精选 6 类（区分度高）× 词/色变化
  ["animate", "backInDown",  "聚焦",   "cyan"],
  ["animate", "backInDown",  "能量",   "gold"],
  ["animate", "zoomIn",      "视觉",   "purple"],
  ["animate", "zoomIn",      "创意",   "pink"],
  ["animate", "flipInX",     "脉动",   "pink"],
  ["animate", "flipInX",     "灵感",   "cyan"],
  ["animate", "heartBeat",   "直播",   "green"],
  ["animate", "heartBeat",   "心跳",   "pink"],
  ["animate", "jackInTheBox","冲击",   "gold"],
  ["animate", "jackInTheBox","爆炸",   "cyan"],
  ["animate", "hinge",       "崩解",   "purple"],
  ["animate", "hinge",       "坠落",   "green"],
  // magic.css 精选 6 类
  ["magic", "twisterInDown", "扭转",   "cyan"],
  ["magic", "twisterInDown", "旋风",   "purple"],
  ["magic", "boingInUp",     "弹跃",   "pink"],
  ["magic", "boingInUp",     "弹跳",   "gold"],
  ["magic", "vanishIn",      "淡出",   "green"],
  ["magic", "vanishIn",      "消散",   "cyan"],
  ["magic", "puffIn",        "爆发",   "gold"],
  ["magic", "puffIn",        "膨胀",   "pink"],
  ["magic", "holeOut",       "漩涡",   "purple"],
  ["magic", "holeOut",       "黑洞",   "green"],
  ["magic", "perspectiveUp", "升维",   "cyan"],
  ["magic", "perspectiveUp", "透视",   "pink"],
];

// 自写 Canvas 图形动效（id = 模板名_颜色，去掉颜色后缀即模板 key）
const CANVAS_JOBS = [
  ["ring_rotate_cyan",     "旋转光环",     "#00e5ff"],
  ["ring_rotate_pink",     "旋转光环",     "#ff2d75"],
  ["grid_pulse_purple",    "方块矩阵脉冲", "#a855f7"],
  ["progress_grow_gold",   "进度条增长",   "#ffd700"],
  ["countdown_green",      "数字滚动",     "#00ff88"],
  ["waveform_cyan",        "音频波形",     "#00e5ff"],
  ["starfield_white",      "粒子星空",     "#ffffff"],
  ["spiral_gold",          "螺旋流动",     "#ffd700"],
  ["neon_frame_pink",      "霓虹边框脉冲", "#ff2d75"],
  ["aurora_wave_cyan",     "极光波浪",     "#00e5ff"],
  ["glitch_bars_red",      "故障彩条",     "#ff3333"],
  ["scan_sweep_green",     "扫描线UI",     "#00ff88"],
];

function cssTextJob(kind, cls, theme, word) {
  const css = kind === "animate" ? animCss : magicCss;
  const t = THEMES[theme];
  const clsAttr = kind === "animate" ? `animate__animated animate__${cls}` : `magictime ${cls}`;
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0}body{background:${t.bg};display:flex;align-items:center;justify-content:center;height:100vh;overflow:hidden}
.box{font:bold 100px "Microsoft YaHei","PingFang SC",sans-serif;color:${t.color};text-shadow:0 0 22px ${t.glow},0 0 55px ${t.glow};letter-spacing:8px}
${css}
.box{animation-duration:2.8s;animation-fill-mode:both}
</style></head><body><div class="${clsAttr}">${word}</div></body></html>`;
}

// 词与类对应（保留兼容，实际用 TEXT_JOBS 的 word 直接渲染）
function textOf(cls) {
  const map = {
    "FOCUS": "FOCUS", "能量": "能量", "VISION": "VISION", "创意": "创意",
    "PULSE": "PULSE", "灵感": "灵感", "LIVE": "LIVE", "心跳": "心跳",
    "BOOM": "BOOM", "爆炸": "爆炸", "DROP": "DROP", "坠落": "坠落",
    "TWIST": "TWIST", "旋风": "旋风", "BOING": "BOING", "弹跳": "弹跳",
    "FADE": "FADE", "消散": "消散", "PUFF": "PUFF", "膨胀": "膨胀",
    "HOLE": "HOLE", "黑洞": "黑洞", "3D UP": "3D UP", "透视": "透视",
    "聚焦": "聚焦", "视觉": "视觉", "脉动": "脉动", "直播": "直播",
    "冲击": "冲击", "崩解": "崩解", "扭转": "扭转", "弹跃": "弹跃",
    "淡出": "淡出", "爆发": "爆发", "漩涡": "漩涡", "升维": "升维",
  };
  return map[cls] || "MOTION";
}

const canvasTemplates = {
  ring_rotate: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a14;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0a14';x.fillRect(0,0,W,H);
  for(let i=0;i<3;i++){
    const r=100+i*70+Math.sin(t*2+i)*20;
    x.strokeStyle='${color}';x.globalAlpha=0.4+i*0.2;x.lineWidth=6-i;
    x.shadowColor='${color}';x.shadowBlur=25;
    x.beginPath();x.arc(W/2,H/2,r,t*1.5+i*2,t*1.5+i*2+Math.PI*1.4);x.stroke();
  }
  x.shadowBlur=0;x.globalAlpha=1;
  x.fillStyle='${color}';x.font='bold 40px monospace';x.textAlign='center';
  x.shadowColor='${color}';x.shadowBlur=20;x.fillText('●',W/2,H/2+14);
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  grid_pulse: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a16;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0a16';x.fillRect(0,0,W,H);
  const cols=8,rows=5,cw=W/cols,ch=H/rows;
  for(let i=0;i<cols;i++)for(let j=0;j<rows;j++){
    const d=Math.hypot(i-cols/2,j-rows/2);
    const pulse=Math.sin(t*3-d*0.7);
    const size=cw*0.3*(0.5+pulse*0.5)+4;
    x.fillStyle='${color}';x.globalAlpha=0.25+pulse*0.4;
    x.shadowColor='${color}';x.shadowBlur=15;
    x.fillRect(i*cw+cw/2-size/2,j*ch+ch/2-size/2,size,size);
  }
  x.shadowBlur=0;x.globalAlpha=1;
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  progress_grow: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a14;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0a14';x.fillRect(0,0,W,H);
  const p=Math.min(t/4,1);
  const w=900,h=36,cx=(W-w)/2,cy=H/2;
  x.strokeStyle='#333';x.lineWidth=4;x.strokeRect(cx,cy,w,h);
  x.fillStyle='${color}';x.shadowColor='${color}';x.shadowBlur=20;
  x.fillRect(cx+4,cy+4,(w-8)*p,h-8);
  x.shadowBlur=0;x.fillStyle='#fff';x.font='bold 42px monospace';x.textAlign='center';
  x.fillText(Math.floor(p*100)+'%',W/2,cy+h+50);
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  countdown: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0f0a;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0f0a';x.fillRect(0,0,W,H);
  const n=Math.floor(t*10)%100;
  x.fillStyle='${color}';x.font='bold 180px monospace';x.textAlign='center';x.textBaseline='middle';
  x.shadowColor='${color}';x.shadowBlur=40;
  x.fillText(n,W/2,H/2-20);
  x.font='bold 30px monospace';x.fillStyle='#8a9';x.shadowBlur=0;
  x.fillText('COUNTING',W/2,H/2+110);
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  waveform: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a18;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0a18';x.fillRect(0,0,W,H);
  x.strokeStyle='${color}';x.lineWidth=3;x.shadowColor='${color}';x.shadowBlur=15;
  x.beginPath();
  for(let i=0;i<=W;i+=4){
    const y=H/2+Math.sin(i*0.02+t*5)*50+Math.sin(i*0.007-t*2.2)*120;
    i===0?x.moveTo(i,y):x.lineTo(i,y);
  }
  x.stroke();
  for(let b=0;b<64;b++){
    const bh=Math.abs(Math.sin(b*0.3+t*4))*140;
    x.fillStyle='${color}';x.globalAlpha=0.6;
    x.fillRect(b*20+10,H/2+160-bh,10,bh);
  }
  x.shadowBlur=0;x.globalAlpha=1;
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  starfield: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#000;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
const stars=[];
for(let i=0;i<220;i++)stars.push({x:Math.random()*W,y:Math.random()*H,z:Math.random()});
function draw(t){
  x.fillStyle='rgba(0,0,0,0.25)';x.fillRect(0,0,W,H);
  x.fillStyle='${color}';
  for(const st of stars){
    const sx=W/2+(st.x-W/2)*st.z, sy=H/2+(st.y-H/2)*st.z;
    const sz=st.z*3;
    x.globalAlpha=st.z;
    x.shadowColor='${color}';x.shadowBlur=10*st.z;
    x.fillRect(sx,sy,sz,sz);
    st.z-=0.008;
    if(st.z<0.05){st.z=1;st.x=Math.random()*W;st.y=Math.random()*H;}
  }
  x.shadowBlur=0;x.globalAlpha=1;
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  spiral: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0d0a06;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='rgba(13,10,6,0.3)';x.fillRect(0,0,W,H);
  for(let i=0;i<900;i++){
    const a=i*0.05+t*3;
    const r=i*0.35;
    const px=W/2+Math.cos(a)*r, py=H/2+Math.sin(a)*r;
    x.fillStyle='${color}';x.globalAlpha=1-i/900;
    x.fillRect(px,py,3,3);
  }
  x.globalAlpha=1;
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  neon_frame: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a14;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0a14';x.fillRect(0,0,W,H);
  const m=60+Math.sin(t*2)*15;
  x.strokeStyle='${color}';x.lineWidth=5;x.shadowColor='${color}';x.shadowBlur=30;
  x.strokeRect(m,m,W-m*2,H-m*2);
  x.lineWidth=3;x.shadowBlur=50;
  x.strokeRect(m+20,m+20,W-(m+20)*2,H-(m+20)*2);
  x.shadowBlur=0;
  x.fillStyle='${color}';x.font='bold 30px monospace';x.textAlign='center';
  x.fillText('REC ●',W/2,m+70);
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  aurora_wave: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#04101f;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='rgba(4,16,31,0.25)';x.fillRect(0,0,W,H);
  for(let layer=0;layer<3;layer++){
    x.strokeStyle='${color}';x.globalAlpha=0.35-layer*0.08;x.lineWidth=18-layer*5;
    x.shadowColor='${color}';x.shadowBlur=40;
    x.beginPath();
    for(let i=0;i<=W;i+=8){
      const y=H*0.4+Math.sin(i*0.005+t*1.5+layer)*90+Math.sin(i*0.013-t*2.5+layer*2)*40;
      i===0?x.moveTo(i,y):x.lineTo(i,y);
    }
    x.stroke();
  }
  x.shadowBlur=0;x.globalAlpha=1;
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  glitch_bars: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a0f;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#0a0a0f';x.fillRect(0,0,W,H);
  for(let i=0;i<60;i++){
    const y=Math.floor(Math.random()*H);
    const h=4+Math.random()*26;
    const off=(Math.random()-0.5)*80;
    x.fillStyle=i%2? '#ff3333':'#00e5ff';
    x.globalAlpha=0.25+Math.random()*0.4;
    x.fillRect(W/2+off-300,y,300,h);
    x.fillStyle='${color}';
    x.fillRect(W/2-300,y,300,h);
  }
  x.globalAlpha=1;
  x.fillStyle='#fff';x.font='bold 90px monospace';x.textAlign='center';
  x.shadowColor='${color}';x.shadowBlur=30;
  x.fillText('GLITCH',W/2,H/2+30);
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,

  scan_sweep: (color) => `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#060a0f;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head>
<body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){
  x.fillStyle='#060a0f';x.fillRect(0,0,W,H);
  const sy=Math.floor((t%1)*H);
  const grad=x.createLinearGradient(0,sy-60,0,sy+60);
  grad.addColorStop(0,'rgba(0,255,136,0)');grad.addColorStop(0.5,'rgba(0,255,136,0.35)');grad.addColorStop(1,'rgba(0,255,136,0)');
  x.fillStyle=grad;x.fillRect(0,sy-60,W,120);
  x.fillStyle='${color}';x.font='bold 26px monospace';
  for(let i=0;i<30;i++){
    x.globalAlpha=0.3+Math.random()*0.7;
    x.fillText('0x'+Math.floor(Math.random()*65535).toString(16).toUpperCase(),10+i*44,40+Math.floor(Math.random()*8)*30);
  }
  x.globalAlpha=1;
  x.fillStyle='${color}';x.shadowColor='${color}';x.shadowBlur=20;
  x.font='bold 56px monospace';x.textAlign='center';
  x.fillText('SYS.SCAN',W/2,H-90);
}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);
</script></body></html>`,
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let edge = null;

function startEdge() {
  fs.rmSync(TMP + "\\dvprofile", { recursive: true, force: true });
  fs.mkdirSync(TMP + "\\dvprofile", { recursive: true });
  edge = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`,
    "--user-data-dir=" + TMP + "\\dvprofile",
    "--disable-gpu", "--no-first-run", "--disable-extensions",
    "--window-size=1280,720", "about:blank",
  ], { stdio: "ignore" });
}

async function openTab(url) {
  for (let i = 0; i < 40; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
      if (res.ok) return (await res.json()).webSocketDebuggerUrl;
    } catch {}
    await sleep(400);
  }
  throw new Error("devtools not ready");
}

function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    const pending = new Map(); let seq = 0;
    ws.onopen = () => resolve({
      send(method, params = {}) {
        return new Promise((res, rej) => {
          const id = ++seq; pending.set(id, { res, rej });
          ws.send(JSON.stringify({ id, method, params }));
        });
      },
      close() { try { ws.close(); } catch {} },
    });
    ws.onerror = () => reject(new Error("ws err"));
    ws.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && pending.has(m.id)) {
        const { res, rej } = pending.get(m.id); pending.delete(m.id);
        m.error ? rej(new Error(m.error.message)) : res(m.result);
      }
    };
  });
}

async function captureFrames(ws, tag) {
  const dir = `${TMP}\\${tag}`;
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  await ws.send("Page.enable");
  await sleep(LOAD_WAIT);
  for (let i = 0; i < FRAMES; i++) {
    const shot = await ws.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(`${dir}\\f${String(i).padStart(4, "0")}.png`, Buffer.from(shot.data, "base64"));
    await sleep(INTERVAL);
  }
}

function assemble(tag, outFile) {
  const dir = `${TMP}\\${tag}`;
  const out = OUTDIR + "\\" + outFile;
  try {
    execFileSync(FFMPEG, [
      "-y", "-hide_banner", "-loglevel", "error",
      "-framerate", String(FPS), "-i", `${dir}\\f%04d.png`,
      "-vf", "scale=1280:720", "-c:v", "libx264", "-pix_fmt", "yuv420p",
      "-movflags", "+faststart", "-crf", "26", out,
    ], { timeout: 120000 });
    const sz = fs.statSync(out).size;
    console.log(`  OK ${outFile}  ${(sz / 1024).toFixed(0)}KB`);
    return true;
  } catch (e) {
    console.log(`  FAIL ${outFile}: ${e.message.split("\n").slice(-1)[0]}`);
    return false;
  }
}

async function main() {
  console.log("== 启动 Edge headless ==");
  startEdge(); await sleep(3000);

  const jobs = [];
  // 文字动效（24 条：12 组合 × 词/色变化已含）
  for (const [kind, cls, word, theme] of TEXT_JOBS) {
    const tag = `dv_${kind}_${cls}_${theme}`;
    const outFile = `fx_txt_${cls}_${theme}.mp4`;
    const html = cssTextJob(kind, cls, theme, word);
    jobs.push([tag, outFile, html]);
  }
  // Canvas 图形动效（12 条）
  for (const [id, label, color] of CANVAS_JOBS) {
    const baseId = id.replace(/_(cyan|pink|gold|purple|green)$/, "");
    let tpl = canvasTemplates[baseId];
    if (!tpl) { console.log("skip tpl " + id); continue; }
    const html = tpl(color);
    const outFile = `fx_cv_${id}.mp4`;
    jobs.push([`dv_${id}`, outFile, html]);
  }
  console.log(`== 共 ${jobs.length} 条（文字动效 ${TEXT_JOBS.length} + Canvas 图形 ${CANVAS_JOBS.length}）==`);

  let ok = 0;
  for (const [tag, outFile, html] of jobs) {
    if (fs.existsSync(OUTDIR + "\\" + outFile) && fs.statSync(OUTDIR + "\\" + outFile).size > 10000) {
      console.log(`  KEEP ${outFile}`); ok++; continue;
    }
    const htmlFile = `${TMP}\\${tag}.html`;
    fs.writeFileSync(htmlFile, html, "utf8");
    try {
      const ws = await connect(await openTab("file:///" + htmlFile.replace(/\\/g, "/")));
      await captureFrames(ws, tag);
      ws.close();
      if (assemble(tag, outFile)) ok++;
    } catch (e) {
      console.log(`  FAIL ${outFile}: ${e.message}`);
    }
  }
  console.log(`\n== 完成: ${ok}/${jobs.length} ==`);
  try { edge.kill(); } catch {}
}
main();