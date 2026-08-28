// VideoForge Suite — 前端逻辑 (UI/UX Pro Max 设计系统)
const API = "";
const $ = (s, r = document) => r.querySelector(s);

async function getJSON(path){ const r = await fetch(API+path,{cache:"no-store"}); if(!r.ok) throw new Error(await r.text()); return r.json(); }
async function postJSON(path,body){ const r = await fetch(API+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}); return r.json(); }

// ---------- 状态 ----------
let cachedMats = [];
let categories = [];
let currentCat = "all";
let currentSub = "all";
let query = "";

const KIND_ICON = { video:"▶", image:"🖼", audio:"🔊", html:"✨", other:"◆" };
const KIND_LABEL = { video:"视频", image:"图片", audio:"音频", html:"HTML 动效", other:"其他" };
const CAT_NAME = { styles:"风格", widgets:"组件·插件", transitions:"转场", assets:"素材" };

// ---------- 引擎 ----------
function renderEngines(tools){
  const el = $("#engine-list");
  if(!tools || !tools.length){ el.innerHTML = `<div class="loading">无引擎数据</div>`; return; }
  el.innerHTML = tools.map(t => `
    <div class="engine-card" style="--c:${t.color}">
      <span class="ec-dot" style="color:${t.color};background:${t.color}"></span>
      <div class="ec-body">
        <div class="ec-name">${t.name}</div>
        <div class="ec-desc" title="${t.integration||''}">${t.integration||t.desc||''}</div>
      </div>
      <span class="ec-status ${t.status}">${t.status==='ready'||t.status==='available'?'就绪':(t.status||'未知')}</span>
    </div>`).join("");
}

// ---------- 分类 tab ----------
function renderCats(){
  const bar = $("#cat-tabs");
  const total = cachedMats.length;
  const all = `<button class="cat-tab ${currentCat==='all'?'on':''}" data-id="all">全部 <span class="ct-count">${total}</span></button>`;
  const tabs = categories.map(c => `<button class="cat-tab ${currentCat===c.id?'on':''}" data-id="${c.id}" title="${c.desc||''}">${c.icon||''} ${c.name} <span class="ct-count">${c.count}</span></button>`).join("");
  bar.innerHTML = all + tabs;
  bar.querySelectorAll(".cat-tab").forEach(b => b.addEventListener("click", () => {
    currentCat = b.dataset.id; currentSub = "all";
    renderCats(); renderSubcats(); renderGrid();
  }));
}

function renderSubcats(){
  const list = currentCat==="all" ? cachedMats : cachedMats.filter(m => m.category===currentCat);
  const counts = {};
  list.forEach(m => { counts[m.subcat] = (counts[m.subcat]||0)+1; });
  const keys = Object.keys(counts).sort();
  const bar = $("#subcat-bar");
  if(keys.length <= 1){ bar.innerHTML = ""; return; }
  bar.innerHTML = `<button class="subcat-chip ${currentSub==='all'?'on':''}" data-id="all">全部 ${list.length}</button>`
    + keys.map(k => `<button class="subcat-chip ${currentSub===k?'on':''}" data-id="${k}">${k} ${counts[k]}</button>`).join("");
  bar.querySelectorAll(".subcat-chip").forEach(b => b.addEventListener("click", () => {
    currentSub = b.dataset.id; renderSubcats(); renderGrid();
  }));
}

// ---------- 网格 ----------
// 多框预览模式：true = 卡片直接嵌入 iframe/video/img（动效在网格里就活起来）
//                false = 只显示缩略图，点击才打开抽屉预览
let multiPreview = (localStorage.getItem("vf_multiPreview") ?? "1") !== "0";

function previewToggleBtn(){
  return `<button class="preview-toggle" title="切换预览模式">${multiPreview?'🖼 切换为缩略图':'▶ 切换为多框预览'}</button>`;
}
function bindPreviewToggle(){
  document.querySelectorAll(".preview-toggle").forEach(b => b.addEventListener("click", (e) => {
    e.stopPropagation();
    multiPreview = !multiPreview;
    localStorage.setItem("vf_multiPreview", multiPreview ? "1" : "0");
    renderGrid();
  }));
}

function matCard(m, i){
  const isVideo = m.kind === "video";
  const thumb = m.kind === "html"
    ? `/thumbs/effects_html/${encodeURIComponent(m.name)}.jpg`
    : `/thumbs/${encodeURIComponent(m.category)}/${encodeURIComponent(m.name)}.jpg`;
  const icon = KIND_ICON[m.kind] || KIND_ICON.other;
  const play = isVideo ? `<span class="play-badge">▶</span>` : "";
  // 多框预览占位: 卡片进入视口时由 IntersectionObserver 注入 iframe/video/img
  const slot = multiPreview
    ? `<div class="preview-slot" data-url="${m.url}" data-kind="${m.kind}"></div>`
    : "";
  return `<article class="mat-card ${multiPreview?'preview-on':''}" style="animation-delay:${Math.min(i*0.025,0.4)}s" data-url="${m.url}" data-name="${m.name}" data-cat="${m.category}" data-sub="${m.subcat}" data-kind="${m.kind}" data-size="${m.size_mb}">
    <div class="thumb">
      <img class="thumb-img ${multiPreview?'hide-when-ready':''}" src="${thumb}" alt="" loading="lazy" onerror="this.style.display='none'">
      ${slot}
      <div class="thumb-fallback"><span class="fb-icon">${icon}</span></div>
      ${play}
    </div>
    <div class="card-foot">
      <span class="card-name" title="${m.name}">${m.name}</span>
      <span class="card-sub">${m.subcat}</span>
    </div>
  </article>`;
}

// IntersectionObserver 懒加载：只有进入视口 ±200px 才注入预览元素
const _previewIO = ("IntersectionObserver" in window) ? new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if(!e.isIntersecting) return;
    const slot = e.target;
    if(slot.dataset.mounted) return;
    slot.dataset.mounted = "1";
    const kind = slot.dataset.kind, url = slot.dataset.url;
    let el;
    if(kind === "html"){ el = document.createElement("iframe"); el.setAttribute("sandbox","allow-scripts allow-same-origin"); }
    else if(kind === "video"){ el = document.createElement("video"); el.muted = el.loop = el.autoplay = true; el.playsInline = true; el.preload = "metadata"; }
    else if(kind === "image"){ el = document.createElement("img"); el.alt = ""; }
    else return;
    el.className = "preview-el";
    el.src = url;
    slot.appendChild(el);
    el.addEventListener("load", () => { const th = slot.parentElement && slot.parentElement.querySelector(".thumb-img"); if(th) th.classList.add("hidden"); });
    el.addEventListener("error", () => { /* 静默：保留缩略图 */ });
    if(kind === "video") el.play().catch(()=>{});
    _previewIO.unobserve(slot);
  });
}, { rootMargin: "200px" }) : null;

function setupLazyPreviews(){
  if(!_previewIO) return;
  document.querySelectorAll(".preview-slot:not([data-mounted])").forEach(s => _previewIO.observe(s));
}

function renderGrid(){
  const grid = $("#mat-grid");
  let list = currentCat==="all" ? cachedMats : cachedMats.filter(m => m.category===currentCat);
  if(currentSub!=="all") list = list.filter(m => m.subcat===currentSub);
  if(query){
    const q = query.toLowerCase();
    list = list.filter(m => m.name.toLowerCase().includes(q) || (m.subcat||"").toLowerCase().includes(q) || (CAT_NAME[m.category]||m.category).toLowerCase().includes(q));
  }
  // 注入预览模式切换按钮到 subcat-bar 旁边
  const bar = $("#subcat-bar");
  if(bar && !bar.querySelector(".preview-toggle")){
    bar.insertAdjacentHTML("beforeend", previewToggleBtn());
    bindPreviewToggle();
  }
  if(!list.length){
    grid.innerHTML = `<div class="empty-state"><span class="es-ico">🗂️</span>没有匹配的素材${query?`：<b>${query}</b>`:""}<br>试试切换分类或清空搜索</div>`;
    return;
  }
  grid.innerHTML = list.map((m,i) => matCard(m,i)).join("");
  grid.querySelectorAll(".mat-card").forEach(card => card.addEventListener("click", (ev) => {
    // 多框预览模式下不打开抽屉（除非点击的是名称/分类标签）
    if(multiPreview && !ev.target.closest(".card-foot")) return;
    openDrawer(card.dataset);
  }));
  setupLazyPreviews();
}

function showSkeleton(){
  const grid = $("#mat-grid");
  grid.innerHTML = Array.from({length:12}).map(()=>`
    <div class="skeleton"><div class="sk-thumb"></div><div class="sk-line"></div><div class="sk-line" style="width:60%"></div></div>`).join("");
}

// ---------- 预览抽屉 ----------
const drawer = $("#preview-drawer");
const backdrop = $("#drawer-backdrop");
function mediaForDrawer(m){
  const thumb = `/thumbs/${encodeURIComponent(m.category)}/${encodeURIComponent(m.name)}.jpg`;
  if(m.kind === "video") return `<video src="${m.url}" poster="${thumb}" controls autoplay muted loop playsinline preload="metadata"></video>`;
  if(m.kind === "html") return `<div class="dm-loading">HTML 动效加载中…</div><iframe src="${m.url}" sandbox="allow-scripts allow-same-origin" style="display:block" onload="this.previousElementSibling&&this.previousElementSibling.remove()"></iframe>`;
  if(m.kind === "image") return `<img src="${m.url}" alt="${m.name}">`;
  if(m.kind === "audio") return `<audio src="${m.url}" controls></audio>`;
  return `<div class="dm-loading">暂不支持预览：${m.ext||m.kind}</div>`;
}
function openDrawer(d){
  const m = cachedMats.find(x => x.url===d.url) || {name:d.name,url:d.url,category:d.cat,subcat:d.sub,size_mb:d.size,kind:d.kind||"other",ext:""};
  $("#drawer-title").textContent = CAT_NAME[m.category] || m.category;
  $("#drawer-media").innerHTML = mediaForDrawer(m);
  const big = $("#drawer-media").querySelector("video");
  if(big){ big.play().catch(()=>{}); }
  const kindLabel = KIND_LABEL[m.kind] || m.ext || "其他";
  const catLabel = CAT_NAME[m.category] || m.category;
  $("#drawer-info").innerHTML = `
    <div class="di-name">${m.name}</div>
    <div class="di-row">
      <span class="di-tag">大类 · ${catLabel}</span>
      <span class="di-tag">子类 · ${m.subcat}</span>
      <span class="di-tag">${kindLabel}</span>
      <span class="di-tag">${m.size_mb} MB</span>
    </div>
    <div class="di-meta">
      <div><b>路径</b> · <code>${m.url}</code></div>
      <div><b>类型</b> · ${m.kind}${m.ext?` (${m.ext})`:""}</div>
    </div>
    <a class="di-link" href="${m.url}" target="_blank" rel="noopener">⬇ 打开原始文件</a>`;
  drawer.classList.add("show"); backdrop.classList.add("show");
  drawer.setAttribute("aria-hidden","false");
}
function closeDrawer(){ drawer.classList.remove("show"); backdrop.classList.remove("show"); $("#drawer-media").innerHTML=""; drawer.setAttribute("aria-hidden","true"); }
$("#drawer-close").addEventListener("click", closeDrawer);
backdrop.addEventListener("click", closeDrawer);
document.addEventListener("keydown", e => { if(e.key==="Escape") closeDrawer(); });

// ---------- 环境状态 ----------
function renderEnv(st){
  const pill = $("#env-pill");
  const ok = st && st.h3_env && st.h3_script;
  pill.textContent = ok ? `H3 就绪 · 运行任务 ${st.jobs_running||0}` : "H3 未就绪";
  pill.style.color = ok ? "var(--accent-2)" : "var(--warn)";
}

// ---------- 队列 ----------
function renderJobs(jobs){
  const el = $("#job-list");
  if(!jobs || !jobs.length){ el.innerHTML = `<div class="loading">暂无任务</div>`; return; }
  el.innerHTML = jobs.slice(0,8).map(j => `
    <div class="job-item ${j.status}">
      <div class="ji-top"><span class="ji-state">${j.status==='running'?'生成中':j.status==='done'?'完成':'失败'}</span><span>${j.id||''}</span></div>
      <div class="ji-prompt" title="${(j.prompt||'')}">${ (j.prompt||'(无描述)').slice(0,40) }</div>
    </div>`).join("");
}

// ---------- 生成 ----------
let polling = null;
$("#gen-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = $("#gen-btn"), st = $("#gen-status");
  const payload = {
    prompt: $("#prompt").value, mode: $("#mode").value,
    num_frames: +$("#num_frames").value, steps: +$("#steps").value, seed: +$("#seed").value
  };
  if(!payload.prompt.trim()){ st.innerHTML = `<span class="err">请输入画面描述</span>`; return; }
  btn.disabled = true; st.textContent = "⏳ 提交任务…";
  try{
    const res = await postJSON("/api/generate", payload);
    st.textContent = res.ok ? `✅ 已提交 job ${res.job_id}，后台生成中…` : `❌ ${res.error}`;
  }catch(err){ st.innerHTML = `<span class="err">❌ ${err.message}</span>`; }
  finally{
    btn.disabled = false;
    if(polling) clearInterval(polling);
    polling = setInterval(pollJobs, 2500);
  }
});

async function pollJobs(){
  try{
    const { jobs } = await getJSON("/api/jobs");
    renderJobs(jobs);
    const last = jobs[jobs.length-1];
    if(last && last.status==="done"){ await refreshMaterials(); }
  }catch(e){}
}

// ---------- 初始化 ----------
async function refreshMaterials(){
  const m = await getJSON("/api/materials");
  cachedMats = m.materials || [];
  categories = m.categories || [];
  $("#mat-count").textContent = m.count ?? cachedMats.length;
  renderCats(); renderSubcats(); renderGrid();
}
async function refreshAll(){
  try{
    const [t,s,j] = await Promise.all([getJSON("/api/tools"), getJSON("/api/status"), getJSON("/api/jobs")]);
    renderEngines(t.tools); renderEnv(s); renderJobs(j.jobs);
  }catch(e){
    $("#env-pill").textContent = "连接失败"; $("#env-pill").style.color = "var(--danger)";
  }
}

showSkeleton();
refreshMaterials();
refreshAll();
setInterval(refreshAll, 10000);
setInterval(pollJobs, 4000);

// 搜索
$("#search").addEventListener("input", (e) => { query = e.target.value.trim(); renderGrid(); });
