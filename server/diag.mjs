// diag.mjs — 诊断单个 HTML 在 headless 下的渲染与 console 错误
import { spawn } from "node:child_process";
import fs from "node:fs";

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const PORT = 9223;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const file = process.argv[2];
const tag = process.argv[3] || "diag";

const edge = spawn(EDGE, [
  "--headless=new", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=D:\\VideoForgeSuite\\server\\frames\\${tag}_profile`,
  "--disable-gpu", "--no-first-run", "--disable-extensions", "about:blank",
], { stdio: "ignore" });

await sleep(2500);

let wsUrl = null;
for (let i = 0; i < 30; i++) {
  try {
    const res = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent("file:///" + file.replace(/\\/g, "/"))}`, { method: "PUT" });
    if (res.ok) { wsUrl = (await res.json()).webSocketDebuggerUrl; break; }
  } catch {}
  await sleep(400);
}
if (!wsUrl) { console.log("devtools fail"); edge.kill(); process.exit(1); }

const ws = new WebSocket(wsUrl);
const pending = new Map();
let seq = 0;
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params }));
});
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id).res(m.result); pending.delete(m.id); }
  if (m.method === "Runtime.consoleAPICalled") {
    console.log("CONSOLE:", JSON.stringify(m.params.args?.map(a => a.value ?? a.description)));
  }
  if (m.method === "Runtime.exceptionThrown") {
    console.log("EXCEPTION:", JSON.stringify(m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails?.text));
  }
};
await new Promise((r) => (ws.onopen = r));

await send("Runtime.enable");
await send("Page.enable");
await sleep(1500);

// 抓全局错误
const err = await send("Runtime.evaluate", { expression: "window.__errs ? window.__errs.join('\\n') : '(no js error capture)'", returnByValue: true });
console.log("JS-ERR-CAPTURE:", err.result?.value);

// 截图
const shot = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 0.667 } });
fs.writeFileSync(`D:\\VideoForgeSuite\\server\\frames\\${tag}_diag.png`, Buffer.from(shot.data, "base64"));
console.log("SHOT saved");

// canvas 状态
const cs = await send("Runtime.evaluate", {
  expression: "(()=>{const c=document.getElementById('cv'); if(!c) return 'no canvas'; const ctx=c.getContext('2d'); const d=ctx.getImageData(0,0,100,100).data; let sum=0; for(let i=0;i<d.length;i+=4) sum+=d[i]; return 'canvas '+c.width+'x'+c.height+' brightness@(0,0)-100x100='+(sum/(100*100*3)).toFixed(1);})()",
  returnByValue: true
});
console.log("CANVAS:", cs.result?.value);

ws.close(); edge.kill();
