// check_js.mjs — 提取 HTML 里 <script> 块并用 new Function 验证语法
import fs from "node:fs";
const file = process.argv[2];
const html = fs.readFileSync(file, "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.log("NO_SCRIPT"); process.exit(1); }
const js = m[1];
try { new Function(js); console.log("JS_OK " + file); }
catch (e) {
  console.log("JS_ERR " + file + " : " + e.message);
  const lines = js.split("\n");
  const ln = (e.lineNumber ?? 0) - 1;
  console.log("--- around line " + (ln + 1) + " ---");
  for (let i = Math.max(0, ln - 2); i < Math.min(lines.length, ln + 3); i++) {
    console.log((i === ln ? ">>> " : "    ") + (i + 1) + ": " + lines[i]);
  }
}