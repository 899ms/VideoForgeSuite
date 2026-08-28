// 稳健版 HTML 动效缩略图生成：为每个 .html 生成 materials/.thumbs/effects_html/<basename>.html.jpg
// 关键修复：用 taskkill /T 杀掉整个 Edge 进程树（之前只杀顶层进程，子进程堆积导致卡死）。
// 固定 8s 硬超时 + 3 路并发；输出路径扁平化，与 app.js /thumbs/effects_html/<name>.jpg 一致。
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const ROOT = "D:\\VideoForgeSuite\\materials";
const THUMB = path.join(ROOT, ".thumbs", "effects_html");
const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PER_FILE_MS = 8000;
const CONCURRENCY = 3;
const BUDGET = 3000;

function listHtml(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith(".") || e.name.startsWith("_")) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) listHtml(p, out);
    else if (e.name.toLowerCase().endsWith(".html")) out.push(p);
  }
  return out;
}

function killTree(pid) {
  try { spawn("taskkill", ["/T", "/F", "/PID", String(pid)], { stdio: "ignore" }); } catch {}
}

function shotOnce(htmlPath, out) {
  return new Promise((resolve) => {
    const prof = path.join(os.tmpdir(), "vf_shot_" + Math.random().toString(36).slice(2));
    fs.mkdirSync(prof, { recursive: true });
    let child;
    try {
      child = spawn(EDGE, [
        `--user-data-dir=${prof}`, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--no-first-run", "--hide-scrollbars", "--force-color-profile=srgb",
        "--window-size=480,300", `--virtual-time-budget=${BUDGET}`,
        `--screenshot=${out}`, "file://" + htmlPath,
      ], { stdio: "ignore" });
    } catch (e) { resolve(0); return; }
    const pid = child.pid;
    let done = false;
    const finish = () => {
      if (done) return; done = true;
      try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
      if (pid) killTree(pid);
      resolve();
    };
    child.on("close", finish);
    child.on("error", finish);
    setTimeout(finish, PER_FILE_MS);
  });
}

async function runChunk(files) {
  return await Promise.all(files.map(f => {
    const name = path.basename(f);
    const out = path.join(THUMB, name + ".jpg");
    return shotOnce(f, out).then(() =>
      (fs.existsSync(out) && fs.statSync(out).size > 800) ? 1 : 0);
  }));
}

async function main() {
  fs.mkdirSync(THUMB, { recursive: true });
  const files = listHtml(ROOT);
  console.log(`html files: ${files.length}`);
  let ok = 0, fail = 0;
  for (let i = 0; i < files.length; i += CONCURRENCY) {
    const chunk = files.slice(i, i + CONCURRENCY);
    const res = await runChunk(chunk);
    ok += res.reduce((a, b) => a + b, 0);
    fail += chunk.length - res.reduce((a, b) => a + b, 0);
    console.log(`progress ${Math.min(i + CONCURRENCY, files.length)}/${files.length} ok=${ok} fail=${fail}`);
  }
  console.log(`html thumbs done ok=${ok} fail=${fail}`);
}
main().catch(e => { console.error(e); process.exit(1); });
