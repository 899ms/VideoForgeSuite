// rerun2.mjs — 补渲染 starfield + glitch 两条动效
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9227, TMP = "D:\\VideoForgeSuite\\server\\frames", OUT = "D:\\VideoForgeSuite\\materials\\generated", FF = "C:\\ffmpeg\\ffmpeg.exe";
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const edge = spawn(EDGE, ["--headless=new", `--remote-debugging-port=${PORT}`, "--user-data-dir=" + TMP + "\\r2p", "--disable-gpu", "--window-size=1280,720", "about:blank"], { stdio: "ignore" });
await sleep(3000);

async function openTab(u) {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent(u)}`, { method: "PUT" });
      if (r.ok) return (await r.json()).webSocketDebuggerUrl;
    } catch {}
    await sleep(400);
  }
  throw new Error("no devtools");
}
function conn(u) {
  return new Promise((res, rej) => {
    const ws = new WebSocket(u), p = new Map(); let seq = 0;
    ws.onopen = () => res({
      send: (m, pa = {}) => new Promise((r, j) => { const id = ++seq; p.set(id, { r, j }); ws.send(JSON.stringify({ id, method: m, params: pa })); }),
      close: () => { try { ws.close(); } catch {} },
    });
    ws.onerror = () => rej(new Error("ws"));
    ws.onmessage = (ev) => { const m = JSON.parse(ev.data); if (m.id && p.has(m.id)) { const { r, j } = p.get(m.id); p.delete(m.id); m.error ? j(new Error(m.error.message)) : r(m.result); } };
  });
}
async function run(html, tag, out) {
  const f = `${TMP}\\${tag}.html`;
  fs.writeFileSync(f, html, "utf8");
  const ws = await conn(await openTab("file:///" + f.replace(/\\/g, "/")));
  await ws.send("Page.enable");
  await sleep(600);
  fs.mkdirSync(`${TMP}\\${tag}`, { recursive: true });
  for (let i = 0; i < 60; i++) {
    const s = await ws.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(`${TMP}\\${tag}\\f${String(i).padStart(4, "0")}.png`, Buffer.from(s.data, "base64"));
    await sleep(90);
  }
  ws.close();
  try {
    execFileSync(FF, ["-y", "-loglevel", "error", "-framerate", "20", "-i", `${TMP}\\${tag}\\f%04d.png`, "-vf", "scale=1280:720", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", OUT + "\\" + out], { timeout: 120000 });
    console.log("OK", out, Math.round(fs.statSync(OUT + "\\" + out).size / 1024) + "KB");
  } catch (e) { console.log("FAIL", out, e.message.slice(0, 120)); }
}

const star = `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#000;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head><body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
const stars=[];for(let i=0;i<220;i++)stars.push({x:Math.random()*W,y:Math.random()*H,z:Math.random()});
function draw(t){x.fillStyle='rgba(0,0,0,0.25)';x.fillRect(0,0,W,H);x.fillStyle='#ffffff';
for(const st of stars){const sx=W/2+(st.x-W/2)*st.z,sy=H/2+(st.y-H/2)*st.z,sz=st.z*3;
x.globalAlpha=st.z;x.shadowColor='#ffffff';x.shadowBlur=10*st.z;x.fillRect(sx,sy,sz,sz);
st.z-=0.008;if(st.z<0.05){st.z=1;st.x=Math.random()*W;st.y=Math.random()*H;}}
x.shadowBlur=0;x.globalAlpha=1;}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);</script></body></html>`;

const glitch = `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>*{margin:0;padding:0}body{background:#0a0a0f;overflow:hidden}canvas{display:block;width:100vw;height:100vh}</style></head><body><canvas id="c" width="1280" height="720"></canvas><script>
const cv=document.getElementById('c'),x=cv.getContext('2d'),W=1280,H=720,T=5;let s=null;
function draw(t){x.fillStyle='#0a0a0f';x.fillRect(0,0,W,H);
for(let i=0;i<60;i++){const y=Math.floor(Math.random()*H),h=4+Math.random()*26,off=(Math.random()-0.5)*80;
x.fillStyle=i%2?'#ff3333':'#00e5ff';x.globalAlpha=0.25+Math.random()*0.4;
x.fillRect(W/2+off-300,y,300,h);x.fillStyle='#ff3333';x.fillRect(W/2-300,y,300,h);}
x.globalAlpha=1;x.fillStyle='#fff';x.font='bold 90px monospace';x.textAlign='center';x.shadowColor='#ff3333';x.shadowBlur=30;x.fillText('GLITCH',W/2,H/2+30);}
function loop(ts){if(!s)s=ts;const t=(ts-s)/1000;draw(t);if(t<T+0.3)requestAnimationFrame(loop);}
requestAnimationFrame(loop);</script></body></html>`;

await run(star, "dv_starfield_white", "fx_cv_starfield_white.mp4");
await run(glitch, "dv_glitch_bars_red", "fx_cv_glitch_bars_red.mp4");
try { edge.kill(); } catch {}
