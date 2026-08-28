// render_ext_fx.mjs — 将开源 CSS 动效库（animate.css / magic.css）渲染成视频
// 每个动画生成自包含 HTML（CSS 内联）→ Edge headless 截帧 → ffmpeg 合成 → 入库
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9225;
const FPS = 20, FRAMES = 60, INTERVAL = 90, LOAD_WAIT = 700;
const FX = "D:\\VideoForgeSuite\\external_fx";
const OUTDIR = "D:\\VideoForgeSuite\\materials\\generated";
const TMP = "D:\\VideoForgeSuite\\server\\frames";
const FFMPEG = "C:\\ffmpeg\\ffmpeg.exe";

// animate.css 挑选（有代表性 + 全方向覆盖）
const ANIMATE = ["bounce","flash","pulse","rubberBand","shakeX","swing","tada","wobble",
  "heartBeat","backInDown","bounceIn","bounceInUp","fadeIn","fadeInUp","flipInX",
  "lightSpeedInRight","rotateIn","rollIn","zoomIn","slideInUp","hinge","jackInTheBox"];
// magic.css 挑选
const MAGIC = ["twisterInDown","vanishIn","boingInUp","spaceOutUp","perspectiveUp",
  "swap","tinDownIn","foolishIn","puffIn","openDownLeft","bombRightOut","holeOut"];

const animCss = fs.readFileSync(FX + "\\animate.css\\animate.css", "utf8");
const magicCss = fs.readFileSync(FX + "\\magic\\dist\\magic.css", "utf8");

function htmlFor(kind, cls) {
  const css = kind === "animate" ? animCss : magicCss;
  const clsAttr = kind === "animate"
    ? `class="box animate__animated animate__${cls}"`
    : `class="box magictime ${cls}"`;
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0}body{background:#0a0a14;display:flex;align-items:center;justify-content:center;height:100vh;overflow:hidden}
.box{font:bold 110px "Arial Black",Arial,sans-serif;color:#fff;text-shadow:0 0 24px #00e5ff,0 0 60px #00e5ff,0 0 90px #00e5ff;letter-spacing:6px}
${css}
.box{animation-duration:2.8s;animation-fill-mode:both}
</style></head><body>
<div ${clsAttr}>MOTION</div>
</body></html>`;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let edge = null;

function startEdge() {
  fs.rmSync(TMP + "\\fxprofile", { recursive: true, force: true });
  fs.mkdirSync(TMP + "\\fxprofile", { recursive: true });
  edge = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`,
    "--user-data-dir=" + TMP + "\\fxprofile",
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
  for (const c of ANIMATE) jobs.push(["animate", c]);
  for (const c of MAGIC) jobs.push(["magic", c]);
  console.log(`== 共 ${jobs.length} 个动画 ==`);

  let ok = 0;
  for (const [kind, cls] of jobs) {
    const htmlFile = `${TMP}\\ext_${kind}_${cls}.html`;
    fs.writeFileSync(htmlFile, htmlFor(kind, cls), "utf8");
    const tag = `ext_${kind}_${cls}`;
    const outFile = `fx_${kind}_${cls}.mp4`;
    if (fs.existsSync(OUTDIR + "\\" + outFile) && fs.statSync(OUTDIR + "\\" + outFile).size > 10000) {
      console.log(`  KEEP ${outFile}（已存在）`); ok++; continue;
    }
    try {
      const ws = await connect(await openTab("file:///" + htmlFile.replace(/\\/g, "/")));
      await captureFrames(ws, tag);
      ws.close();
      if (assemble(tag, outFile)) ok++;
    } catch (e) {
      console.log(`  FAIL ${cls}: ${e.message}`);
    }
  }
  console.log(`\n== 完成: ${ok}/${jobs.length} ==`);
  try { edge.kill(); } catch {}
}
main();