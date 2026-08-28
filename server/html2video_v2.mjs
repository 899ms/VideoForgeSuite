// html2video_v2.mjs — 重截6个HTML动效（简化干净版）+ ffmpeg合成（带scale修偶宽）
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9224;
const FPS = 20, FRAMES = 100, INTERVAL = 90, LOAD_WAIT = 1200;
const SRC = "D:\\VideoForgeSuite\\server\\html_video_src";
const OUTDIR = "D:\\VideoForgeSuite\\materials\\generated";
const TMP = "D:\\VideoForgeSuite\\server\\frames";
const FFMPEG = "C:\\ffmpeg\\ffmpeg.exe";

const TARGETS = [
  ["impact_v5_401_kinetic_type.html",       "hfx_kinetic_type.mp4"],
  ["impact_v5_403_text_scramble.html",      "hfx_text_scramble.mp4"],
  ["impact_v5_407_volumetric_rays.html",    "hfx_volumetric_rays.mp4"],
  ["ui_501_typewriter_subtitle.html",       "hfx_typewriter_sub.mp4"],
  ["ui_502_glowing_caption.html",           "hfx_glowing_caption.mp4"],
  ["trans_t08_swirl.html",                  "hfx_swirl_transition.mp4"],
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let edge = null;

function startEdge() {
  fs.rmSync(TMP + "\\v2profile", { recursive: true, force: true });
  fs.mkdirSync(TMP + "\\v2profile", { recursive: true });
  edge = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`,
    "--user-data-dir=" + TMP + "\\v2profile",
    "--disable-gpu", "--no-first-run", "--disable-extensions",
    "--window-size=1920,1080", "about:blank",
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
    const shot = await ws.send("Page.captureScreenshot", {
      format: "png",
      clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 0.6667 },
    });
    fs.writeFileSync(`${dir}\\f${String(i).padStart(4, "0")}.png`, Buffer.from(shot.data, "base64"));
    if (i % 25 === 0) process.stdout.write(`  ${tag}: ${i}/${FRAMES}\r`);
    await sleep(INTERVAL);
  }
  process.stdout.write(`  ${tag}: 100/${FRAMES} 帧\n`);
}

function assemble(tag, outFile) {
  const dir = `${TMP}\\${tag}`;
  const out = OUTDIR + "\\" + outFile;
  try {
    execFileSync(FFMPEG, [
      "-y", "-hide_banner", "-loglevel", "error",
      "-framerate", String(FPS), "-i", `${dir}\\f%04d.png`,
      "-vf", "scale=1280:720", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out,
    ], { timeout: 180000 });
    const sz = fs.statSync(out).size;
    console.log(`  ✅ ${outFile}  ${(sz / 1024).toFixed(0)}KB`);
    return true;
  } catch (e) {
    console.log(`  ❌ ${outFile}: ${e.message.split("\n").slice(-1)[0]}`);
    return false;
  }
}

async function main() {
  console.log("== 启动 Edge headless ==");
  startEdge(); await sleep(3000);

  let ok = 0;
  for (const [htmlFile, outFile] of TARGETS) {
    const src = SRC + "\\" + htmlFile;
    if (!fs.existsSync(src)) { console.log("跳过: " + htmlFile); continue; }
    console.log(`\n== 渲染 ${htmlFile} -> ${outFile}`);
    try {
      const ws = await connect(await openTab("file:///" + src.replace(/\\/g, "/")));
      await captureFrames(ws, htmlFile.replace(".html", ""));
      ws.close();
      if (assemble(htmlFile.replace(".html", ""), outFile)) ok++;
    } catch (e) {
      console.log(`  ❌ ${htmlFile}: ${e.message}`);
    }
  }
  console.log(`\n== 完成: ${ok}/${TARGETS.length} ==`);
  try { edge.kill(); } catch {}
}
main();