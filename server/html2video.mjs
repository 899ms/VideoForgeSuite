// html2video.mjs — 用 Edge headless + CDP 将 HTML Canvas 动效渲染成视频
// 用法: node html2video.mjs
import { spawn, execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9222;
const FPS = 20;          // 输出帧率（采样率）
const FRAMES = 100;      // 总帧数 → 5s
const INTERVAL = 90;     // 帧间隔 ms（真实时间，动画会慢放约 2.7 倍）
const LOAD_WAIT = 900;   // 页面加载等待 ms
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
  fs.rmSync(TMP + "\\profile", { recursive: true, force: true });
  fs.mkdirSync(TMP + "\\profile", { recursive: true });
  edge = spawn(EDGE, [
    "--headless=new", `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${TMP}\\profile`,
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
    const pending = new Map();
    let seq = 0;
    ws.onopen = () => resolve({
      send(method, params = {}) {
        return new Promise((res, rej) => {
          const id = ++seq;
          pending.set(id, { res, rej });
          ws.send(JSON.stringify({ id, method, params }));
        });
      },
      close() { try { ws.close(); } catch {} },
    });
    ws.onerror = (e) => reject(new Error("ws error"));
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && pending.has(msg.id)) {
        const { res, rej } = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
      }
    };
  });
}

async function captureFrames(ws, htmlFile, tag) {
  const dir = `${TMP}\\${tag}`;
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  await ws.send("Page.enable");
  await sleep(LOAD_WAIT);
  for (let i = 0; i < FRAMES; i++) {
    const shot = await ws.send("Page.captureScreenshot", {
      format: "png",
      clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 0.667 }, // 1280x720
    });
    fs.writeFileSync(`${dir}\\f${String(i).padStart(4, "0")}.png`, Buffer.from(shot.data, "base64"));
    if (i % 20 === 0) process.stdout.write(`  ${tag}: ${i}/${FRAMES} 帧\r`);
    await sleep(INTERVAL);
  }
  process.stdout.write(`  ${tag}: 完成 ${FRAMES} 帧\n`);
}

function assemble(name, outFile) {
  const tag = name.replace(".html", "");
  const dir = `${TMP}\\${tag}`;
  const out = path.join(OUTDIR, outFile);
  try {
    execFileSync(FFMPEG, [
      "-y", "-hide_banner", "-loglevel", "error",
      "-framerate", String(FPS), "-i", `${dir}\\f%04d.png`,
      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out,
    ], { timeout: 120000 });
    const size = fs.statSync(out).size;
    console.log(`  ✅ ${outFile}  ${(size / 1024).toFixed(0)}KB`);
    return true;
  } catch (e) {
    console.log(`  ❌ ${outFile}: ${e.message.split("\n").slice(-2).join(" ")}`);
    return false;
  }
}

async function main() {
  console.log("== 启动 Edge headless ==");
  startEdge();
  await sleep(2500);

  let okCount = 0;
  for (const [htmlFile, outFile] of TARGETS) {
    const src = path.join(SRC, htmlFile);
    if (!fs.existsSync(src)) { console.log(`  跳过(不存在): ${htmlFile}`); continue; }
    console.log(`== 渲染 ${htmlFile} → ${outFile}`);
    try {
      const wsUrl = await openTab("file:///" + src.replace(/\\/g, "/"));
      const ws = await connect(wsUrl);
      await captureFrames(ws, htmlFile, htmlFile.replace(".html", ""));
      ws.close();
      if (assemble(htmlFile, outFile)) okCount++;
    } catch (e) {
      console.log(`  ❌ ${htmlFile}: ${e.message}`);
    }
  }
  console.log(`\n== 完成: ${okCount}/${TARGETS.length} ==`);
  try { edge.kill(); } catch {}
}

main();
