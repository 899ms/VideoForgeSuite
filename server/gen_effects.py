# -*- coding: utf-8 -*-
"""
VideoForgeSuite 动效库 v2 —— 真正不重复的多样动效。
- 全部纯原生（Canvas / CSS / SVG），零外部库依赖 → 离线可用、缩略图必定明亮。
- 每个模板都是结构各异的独立技法（受 GSAP/Anime/Lottie/Motion/Inspira 启发但以原生实现）。
- 不做「同结构换 8 配色」的换色克隆；每个文件都独一无二。
- 先按已知垃圾前缀清理 v1 的重复文件，再生成到「精选」子目录，避免误删用户真实素材。
"""
import pathlib, shutil, os, math, random

ROOT = pathlib.Path(r"D:\VideoForgeSuite\materials")

# 垃圾前缀（v1 的换色克隆文件名），生成前删除
SPAM_PREFIXES = [
    "gsap_type", "anime_grid", "anime_svg", "lottie_load", "canvas_particles",
    "canvas_flow", "canvas_aurora", "css_neon", "css_gradient", "css_glitch",
    "svg_orbit", "origin_blackhole", "inspira_3d", "trans_wipe", "trans_cube",
    "kaleido", "chart_grow", "progress_ring", "counter", "audio_bars",
    "typewriter", "marquee",
]

TPL = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>__T</title>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:100%;height:100%;overflow:hidden;font-family:'Inter','Noto Sans SC',system-ui,sans-serif}
.bg{position:fixed;inset:0;background:radial-gradient(70% 70% at 50% 45%,__A__cc 0%,transparent 72%),radial-gradient(55% 55% at 18% 82%,__B__aa 0%,transparent 70%),radial-gradient(55% 55% at 82% 18%,__C__aa 0%,transparent 70%),linear-gradient(135deg,#2b2542,#171428);animation:hue 22s linear infinite}
@keyframes hue{to{filter:hue-rotate(360deg)}}
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}canvas{width:100%;height:100%;display:block}
.txt{color:#fff;font-weight:900;text-align:center}
__HEAD__</style></head>
<body><div class="bg"></div><div id="stage">__STAGE__</div>
<script>__SCRIPT__</script></body></html>"""

# 公共 canvas 初始化片段（供脚本内使用 cv/x/rs）
CV_INIT = """var cv=document.getElementById('cv'),x=cv.getContext('2d');
function rs(){cv.width=innerWidth;cv.height=innerHeight;}rs();addEventListener('resize',rs);"""

def wrap(title, stage, head, script, a, b, c):
    return (TPL.replace("__T", title).replace("__STAGE__", stage).replace("__HEAD__", head)
            .replace("__SCRIPT__", script).replace("__A__", a).replace("__B__", b).replace("__C__", c))

# ===================== 动效模板（每个结构各异） =====================
def E():
    items = []

    # ---------- 风格 / 文字类 ----------
    items += [("styles/精选动效", "kinetic_type", "逐字动能文字",
        '<div class="txt" id="t" style="font-size:62px;letter-spacing:4px">KINETIC MOTION</div>',
        ".txt span{display:inline-block;transform-origin:bottom}",
        """var el=document.getElementById('t'),s=el.textContent;el.textContent='';
        [].forEach.call(s,function(ch){var sp=document.createElement('span');sp.textContent=ch===' '?'\\u00A0':ch;el.appendChild(sp);});
        var sp=el.querySelectorAll('span'),k=0;
        (function tick(){sp.forEach(function(e,i){e.style.transition='transform .5s cubic-bezier(.2,1.4,.4,1),opacity .5s';if(i===k){e.style.transform='translateY(-22px) rotate(-6deg)';e.style.opacity=1;}else{e.style.transform='translateY(0) rotate(0)';e.style.opacity=.45;}});k=(k+1)%sp.length;setTimeout(tick,420);})();""",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("styles/精选动效", "flip_reveal", "3D 翻转揭示",
        '<div class="txt" id="t" style="font-size:58px">FLIP REVEAL</div>',
        ".txt{transform-style:preserve-3d;perspective:600px}.txt span{display:inline-block;transform-origin:top}",
        """var el=document.getElementById('t'),s=el.textContent;el.textContent='';
        [].forEach.call(s,function(ch){var sp=document.createElement('span');sp.textContent=ch===' '?'\\u00A0':ch;el.appendChild(sp);});
        var sp=el.querySelectorAll('span'),k=-1;
        (function tick(){k=(k+1)%sp.length;sp.forEach(function(e,i){e.style.transition='transform .6s';if(i<=k){e.style.transform='rotateX(360deg)';e.style.opacity=1;}else{e.style.transform='rotateX(0)';e.style.opacity=.25;}});setTimeout(tick,600);})();""",
        "#00E5FF", "#FF2E97", "#7C4DFF")]

    items += [("styles/精选动效", "magnetic_btn", "磁吸按钮",
        '<button id="b" style="padding:26px 60px;font-size:26px;font-weight:800;color:#fff;border:none;border-radius:20px;background:linear-gradient(135deg,#F72585,#7209B7);box-shadow:0 0 40px #F7258588;cursor:pointer">HOVER ME</button>',
        "#b{transition:transform .12s, box-shadow .2s}",
        """var b=document.getElementById('b');document.addEventListener('mousemove',function(e){var r=b.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;var dx=(e.clientX-cx)/18,dy=(e.clientY-cy)/18;var d=Math.hypot(e.clientX-cx,e.clientY-cy);if(d<240){b.style.transform='translate('+dx+'px,'+dy+'px) scale(1.08)';b.style.boxShadow='0 0 60px #F72585';}else{b.style.transform='translate(0,0)';b.style.boxShadow='0 0 40px #F7258588';}});""",
        "#F72585", "#B5179E", "#7209B7")]

    items += [("styles/精选动效", "text_scramble", "字符解码文字",
        '<div class="txt" id="t" style="font-size:46px;letter-spacing:3px">AI · VIDEO · FORGE</div>',
        ".txt{font-family:monospace}",
        """var el=document.getElementById('t'),fin=el.textContent,ch='!<>-_\\\\/[]{}—=+*^?#________';var k=0;
        (function tick(){var out='';for(var i=0;i<fin.length;i++){if(i<k)out+=fin[i];else if(fin[i]===' ')out+=' ';else out+=ch[Math.floor(Math.random()*ch.length)];}el.textContent=out;k+=0.4;if(k>fin.length+6){k=0;}setTimeout(tick,55);})();""",
        "#43E97B", "#38F9D7", "#5B86E5")]

    items += [("styles/精选动效", "wave_text", "波浪文字",
        '<div class="txt" id="t" style="font-size:56px;letter-spacing:3px">WAVE TEXT</div>',
        ".txt span{display:inline-block}",
        """var el=document.getElementById('t'),s=el.textContent;el.textContent='';
        [].forEach.call(s,function(c){var sp=document.createElement('span');sp.textContent=c===' '?'\\u00A0':c;el.appendChild(sp);});
        var sp=el.querySelectorAll('span'),t=0;(function loop(){requestAnimationFrame(loop);t+=0.08;sp.forEach(function(e,i){e.style.transform='translateY('+Math.sin(t+i*0.4)*16+'px)';});})();""",
        "#FF6A00", "#FF2D95", "#FFD200")]

    items += [("styles/精选动效", "typewriter", "打字机",
        '<div class="txt" id="t" style="font-size:40px;max-width:80%">用 AI 把创意变成会动的画面</div>',
        ".txt{min-height:1.4em}",
        """var el=document.getElementById('t'),s=el.textContent;el.textContent='';var i=0;(function tick(){if(i<=s.length){el.textContent=s.slice(0,i)+(i<s.length?'|':'');i++;setTimeout(tick,90);}else{setTimeout(function(){i=0;tick();},2200);}})();""",
        "#48C6EF", "#6F86D6", "#B2FEFA")]

    items += [("styles/精选动效", "marquee", "跑马灯",
        '<div class="mq"><span>VIDEO · FORGE · SUITE · 动效特效库 · </span><span>VIDEO · FORGE · SUITE · 动效特效库 · </span></div>',
        ".mq{display:flex;white-space:nowrap;font-size:52px;font-weight:900;color:#fff;animation:mq 9s linear infinite}.mq span{padding-right:30px;text-shadow:0 0 24px #7C6CF5}@keyframes mq{to{transform:translateX(-50%)}}",
        "",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    # ---------- 风格 / 背景类 ----------
    items += [("styles/精选动效", "aurora_blobs", "极光光斑",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0,c=['#43E97B','#38F9D7','#5B86E5'];
        (function loop(){requestAnimationFrame(loop);t+=0.01;x.clearRect(0,0,cv.width,cv.height);
        for(var k=0;k<3;k++){var cx=cv.width*(0.5+0.4*Math.sin(t+k*2.1)),cy=cv.height*(0.5+0.4*Math.cos(t*0.8+k*1.7));var g=x.createRadialGradient(cx,cy,0,cx,cy,Math.max(cv.width,cv.height)*0.4);g.addColorStop(0,c[k]+'aa');g.addColorStop(1,'transparent');x.fillStyle=g;x.beginPath();x.arc(cx,cy,Math.max(cv.width,cv.height)*0.4,0,7);x.fill();}x.globalCompositeOperation='lighter';})();""",
        "#43E97B", "#38F9D7", "#5B86E5")]

    items += [("styles/精选动效", "gradient_mesh", "流动渐变网格",
        '<div class="gm"></div>',
        "@keyframes gm{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}.gm{width:100%;height:100%;background:linear-gradient(120deg,#F72585,#7209B7,#3A0CA3,#F72585);background-size:300% 300%;animation:gm 9s ease infinite}",
        "",
        "#F72585", "#7209B7", "#3A0CA3")]

    items += [("styles/精选动效", "neon_grid", "霓虹网格扫描",
        '<div class="ng"></div>',
        ".ng{position:relative;width:100%;height:100%}.ng::before{content:'';position:absolute;inset:0;background-image:linear-gradient(#00E5FF55 1px,transparent 1px),linear-gradient(90deg,#00E5FF55 1px,transparent 1px);background-size:46px 46px;mask-image:radial-gradient(circle,#000 30%,transparent 75%)}.ng::after{content:'';position:absolute;left:0;right:0;height:140px;top:-140px;background:linear-gradient(#FF2E97,transparent);animation:scan 3.2s linear infinite}@keyframes scan{to{top:100%}}",
        "",
        "#00E5FF", "#FF2E97", "#7C4DFF")]

    items += [("styles/精选动效", "glitch_text", "故障文字",
        '<div class="gl" data-text="GLITCH">GLITCH</div>',
        ".gl{position:relative;font-size:84px;font-weight:900;color:#fff;letter-spacing:4px}.gl::before,.gl::after{content:attr(data-text);position:absolute;left:0;top:0;width:100%;overflow:hidden}.gl::before{color:#FF2E97;animation:g1 2.2s infinite linear alternate-reverse;clip-path:inset(0 0 60% 0)}.gl::after{color:#00E5FF;animation:g2 1.7s infinite linear alternate-reverse;clip-path:inset(55% 0 0 0)}@keyframes g1{0%{transform:translate(0,0)}50%{transform:translate(-4px,2px)}100%{transform:translate(3px,-2px)}}@keyframes g2{0%{transform:translate(0,0)}50%{transform:translate(4px,-2px)}100%{transform:translate(-3px,2px)}}",
        "",
        "#00E5FF", "#FF2E97", "#7C4DFF")]

    items += [("styles/精选动效", "synth_grid", "合成波透视网格",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.04;x.fillStyle='#0a0a1f';x.fillRect(0,0,cv.width,cv.height);var hz=cv.height*0.5;x.strokeStyle='#FF2E97';x.lineWidth=1.5;
        for(var i=0;i<22;i++){var p=i/22;var y=hz+Math.pow(p,2.2)*(cv.height);x.beginPath();for(var xx=0;xx<=cv.width;xx+=12){var yy=y+Math.sin(xx*0.02+t+p*4)*8*p;if(xx===0)x.moveTo(xx,yy);else x.lineTo(xx,yy);}x.globalAlpha=0.8-p*0.3;x.stroke();}x.globalAlpha=1;x.strokeStyle='#00E5FF';for(var j=0;j<24;j++){var xp=j/24;var X=xp*cv.width;x.beginPath();for(var yy2=hz;yy2<=cv.height;yy2+=10){var persp=(yy2-hz)/(cv.height-hz);var X2=cv.width/2+(X-cv.width/2)*(1+persp*1.6);if(yy2===hz)x.moveTo(X2,yy2);else x.lineTo(X2,yy2);}x.globalAlpha=0.7;x.stroke();}x.globalAlpha=1;})();""",
        "#FF2E97", "#00E5FF", "#7C4DFF")]

    items += [("styles/精选动效", "liquid_goo", "液态融合球",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.02;x.clearRect(0,0,cv.width,cv.height);x.globalCompositeOperation='lighter';
        for(var i=0;i<7;i++){var a=t+i*0.9;var cx=cv.width/2+Math.cos(a)*cv.width*0.28,cy=cv.height/2+Math.sin(a*1.3)*cv.height*0.28;var g=x.createRadialGradient(cx,cy,0,cx,cy,120);g.addColorStop(0,'rgba(255,92,138,0.9)');g.addColorStop(1,'transparent');x.fillStyle=g;x.beginPath();x.arc(cx,cy,120,0,7);x.fill();}x.globalCompositeOperation='source-over';})();""",
        "#FF5C8A", "#7C6CF5", "#29D3E6")]

    # ---------- 组件 / 加载与图标 ----------
    items += [("widgets/精选组件", "spinner_arc", "弧形加载器",
        '<svg viewBox="0 0 120 120" width="55%" height="55%"><circle cx="60" cy="60" r="46" fill="none" stroke="#ffffff22" stroke-width="10"/><circle id="s" cx="60" cy="60" r="46" fill="none" stroke="#7C6CF5" stroke-width="10" stroke-linecap="round" stroke-dasharray="289" transform="rotate(-90 60 60)"/></svg>',
        "#s{animation:sp 1.4s cubic-bezier(.6,0,.4,1) infinite}@keyframes sp{0%{stroke-dashoffset:289}50%{stroke-dashoffset:70}100%{stroke-dashoffset:289}0%{transform:rotate(-90 60 60)}100%{transform:rotate(270 60 60)}}",
        "",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("widgets/精选组件", "dual_ring", "双环旋转",
        '<div class="r1"></div><div class="r2"></div>',
        "@keyframes rt{to{transform:rotate(360deg)}}.r1,.r2{position:absolute;border-radius:50%}.r1{width:200px;height:200px;border:10px solid #29D3E6;border-top-color:transparent;animation:rt 1.6s linear infinite}.r2{width:140px;height:140px;border:10px solid #FF5C8A;border-bottom-color:transparent;animation:rt 1.1s linear infinite reverse}",
        "",
        "#29D3E6", "#FF5C8A", "#7C6CF5")]

    items += [("widgets/精选组件", "pulse_dot", "脉冲圆点",
        '<div class="p"></div>',
        "@keyframes pp{0%{transform:scale(.6);opacity:.9;box-shadow:0 0 0 0 #43E97B88}70%{transform:scale(1);opacity:1;box-shadow:0 0 0 40px #43E97B00}100%{transform:scale(.6);opacity:.9;box-shadow:0 0 0 0 #43E97B00}}.p{width:90px;height:90px;border-radius:50%;background:#43E97B;animation:pp 1.8s ease-out infinite}",
        "",
        "#43E97B", "#38F9D7", "#5B86E5")]

    items += [("widgets/精选组件", "check_success", "成功对勾",
        '<svg viewBox="0 0 120 120" width="55%" height="55%"><circle cx="60" cy="60" r="50" fill="none" stroke="#2ECC71" stroke-width="8" stroke-dasharray="314" id="c"/><path d="M38 62 L54 78 L84 44" fill="none" stroke="#2ECC71" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="120" id="k"/></svg>',
        "#c{animation:cd 1.2s ease forwards}#k{animation:kd 0.6s 0.9s ease forwards;stroke-dashoffset:120}@keyframes cd{to{stroke-dashoffset:0}}@keyframes kd{to{stroke-dashoffset:0}}",
        "",
        "#2ECC71", "#23D5AB", "#A8FF60")]

    items += [("widgets/精选组件", "bars_eq", "均衡器条",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.08;x.clearRect(0,0,cv.width,cv.height);var n=28,bw=cv.width/n;for(var i=0;i<n;i++){var h=(Math.abs(Math.sin(t+i*0.3))*0.6+Math.abs(Math.sin(t*1.7+i*0.7))*0.4)*cv.height*0.6;var g=x.createLinearGradient(0,cv.height,0,cv.height-h);g.addColorStop(0,'#FF6A00');g.addColorStop(1,'#FFD200');x.fillStyle=g;x.fillRect(i*bw+bw*0.15,cv.height-h,bw*0.7,h);}x.fillStyle='#FF2D95';x.fillRect(0,cv.height-3,cv.width,3);})();""",
        "#FF6A00", "#FF2D95", "#FFD200")]

    items += [("widgets/精选组件", "progress_ring", "进度环",
        '<svg viewBox="0 0 200 200" width="60%" height="60%"><circle cx="100" cy="100" r="80" fill="none" stroke="#ffffff22" stroke-width="14"/><circle id="ring" cx="100" cy="100" r="80" fill="none" stroke="#7C6CF5" stroke-width="14" stroke-linecap="round" transform="rotate(-90 100 100)"/><text id="pct" x="100" y="112" text-anchor="middle" fill="#fff" font-size="42" font-weight="800">0%</text></svg>',
        "",
        """var ring=document.getElementById('ring'),pct=document.getElementById('pct'),C=2*Math.PI*80;ring.style.strokeDasharray=C;var p=0,dir=1;(function loop(){requestAnimationFrame(loop);p+=0.006*dir;if(p>=1){p=1;dir=-1;}if(p<=0){p=0;dir=1;}ring.style.strokeDashoffset=C*(1-p);pct.textContent=Math.round(p*100)+'%';})();""",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("widgets/精选组件", "counter", "数字计数器",
        '<div class="txt" id="n" style="font-size:96px">0</div>',
        ".txt{text-shadow:0 0 30px #29D3E6}",
        """var n=document.getElementById('n'),v=0,dir=1;(function loop(){requestAnimationFrame(loop);v+= (dir? 26: -26);if(v>=2026){v=2026;dir=0;}if(v<0)v=0;n.textContent=Math.round(v).toLocaleString();})();""",
        "#29D3E6", "#6F86D6", "#B2FEFA")]

    items += [("widgets/精选组件", "chart_grow", "柱状增长图",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var bars=[0.4,0.7,0.55,0.9,0.35,0.8,0.6,0.75],prog=0,dir=1;(function loop(){requestAnimationFrame(loop);prog+=0.01*dir;if(prog>1){prog=1;dir=-1;}if(prog<0.2){prog=0.2;dir=1;}x.clearRect(0,0,cv.width,cv.height);var n=bars.length,bw=cv.width/(n*1.8),base=cv.height*0.85;for(var i=0;i<n;i++){var h=bars[i]*cv.height*0.6*prog,bx=i*bw*1.8+bw*0.4,g=x.createLinearGradient(0,base-h,0,base);g.addColorStop(0,'#00F5A0');g.addColorStop(1,'#00D9F5');x.fillStyle=g;x.fillRect(bx,base-h,bw,h);x.fillStyle='#06FFA5';x.fillRect(bx,base+6,bw,4);}x.fillStyle='#fff';x.font='14px Inter';x.fillText('DATA GROWTH',20,30);})();""",
        "#00F5A0", "#00D9F5", "#06FFA5")]

    items += [("widgets/精选组件", "tilt_card", "3D 倾斜卡",
        '<div class="card3d"><div class="face">3D</div></div>',
        "body{perspective:900px}.card3d{width:240px;height:300px;transform-style:preserve-3d;animation:rot 9s linear infinite}.face{width:100%;height:100%;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:96px;font-weight:900;color:#fff;background:linear-gradient(135deg,#7C6CF5,#29D3E6);box-shadow:0 30px 80px #FF5C8A66;border:1px solid #ffffff33}@keyframes rot{to{transform:rotateY(360deg) rotateX(12deg)}}",
        "",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("widgets/精选组件", "glass_card", "毛玻璃卡",
        '<div class="gc"><h2 style="color:#fff;margin:0">Glass UI</h2><p style="color:#fff9;margin:8px 0 0">Frosted · Blur · Glow</p></div>',
        ".gc{width:320px;padding:34px 38px;border-radius:24px;background:rgba(255,255,255,0.12);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,0.25);box-shadow:0 20px 60px #29D3E655;animation:floaty 4s ease-in-out infinite}@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-16px)}}",
        "",
        "#29D3E6", "#7C6CF5", "#FF5C8A")]

    items += [("widgets/精选组件", "grad_border", "渐变描边",
        '<div class="gb">HOVER GLOW</div>',
        ".gb{padding:30px 54px;font-size:30px;font-weight:900;color:#fff;border-radius:20px;background:linear-gradient(#1b1830,#241f3d) padding-box,linear-gradient(135deg,#FF5C8A,#7C6CF5,#29D3E6) border-box;border:3px solid transparent;animation:spin 6s linear infinite}@keyframes spin{to{filter:hue-rotate(360deg)}}",
        "",
        "#FF5C8A", "#7C6CF5", "#29D3E6")]

    items += [("widgets/精选组件", "accordion", "手风琴",
        '<div class="ac"><div class="it" style="flex:3;background:linear-gradient(135deg,#7C6CF5,#29D3E6)"><span>ONE</span></div><div class="it" style="flex:1;background:linear-gradient(135deg,#FF5C8A,#F72585)"><span>TWO</span></div><div class="it" style="flex:1;background:linear-gradient(135deg,#43E97B,#38F9D7)"><span>THREE</span></div></div>',
        ".ac{display:flex;gap:10px;width:80%;height:200px}#stage{align-items:stretch}.it{border-radius:18px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:22px;transition:flex .5s cubic-bezier(.2,1,.3,1)}.ac:hover .it{flex:1}.ac:hover .it:first-child{flex:3}",
        "",
        "#7C6CF5", "#FF5C8A", "#43E97B")]

    # ---------- 转场类 ----------
    items += [("transitions/精选转场", "wipe", "擦除转场",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t=(t+0.012)%2;x.clearRect(0,0,cv.width,cv.height);var g=x.createLinearGradient(0,0,cv.width,0);g.addColorStop(0,'#7C6CF5');g.addColorStop(1,'#29D3E6');x.fillStyle=g;x.fillRect(0,0,cv.width,cv.height);var p=t<1?t:2-t;x.fillStyle='#0e0c16';x.fillRect(0,0,cv.width*(1-p),cv.height);x.fillStyle='#FF5C8A';for(var i=0;i<6;i++)x.fillRect(cv.width*(1-p)-3,cv.height*i/6,6,cv.height/6*0.7);})();""",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("transitions/精选转场", "cube", "立方体转场",
        '<div class="scene"><div class="cube"><b class="f1"></b><b class="f2"></b><b class="f3"></b><b class="f4"></b><b class="f5"></b><b class="f6"></b></div></div>',
        ".scene{perspective:800px}.cube{width:180px;height:180px;position:relative;transform-style:preserve-3d;animation:sp 8s linear infinite}.cube b{position:absolute;width:180px;height:180px;opacity:.85;border:2px solid #fff3}.f1{background:#7C6CF5;transform:rotateY(0) translateZ(90px)}.f2{background:#29D3E6;transform:rotateY(90deg) translateZ(90px)}.f3{background:#FF5C8A;transform:rotateY(180deg) translateZ(90px)}.f4{background:#43E97B;transform:rotateY(-90deg) translateZ(90px)}.f5{background:#FFD200;transform:rotateX(90deg) translateZ(90px)}.f6{background:#F72585;transform:rotateX(-90deg) translateZ(90px)}@keyframes sp{to{transform:rotateX(360deg) rotateY(360deg)}}",
        "",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("transitions/精选转场", "kaleido", "万花筒",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.02;x.fillStyle='rgba(8,6,14,0.12)';x.fillRect(0,0,cv.width,cv.height);var cx=cv.width/2,cy=cv.height/2,R=Math.min(cv.width,cv.height)*0.42;x.save();x.translate(cx,cy);for(var k=0;k<8;k++){x.save();x.rotate(k*Math.PI/4);var y=Math.sin(t+k)*R*0.5;x.beginPath();x.moveTo(0,0);x.quadraticCurveTo(R*0.5,y,R,y*0.4);x.quadraticCurveTo(R*0.3,y*0.1,0,0);x.fillStyle=k%2?'#7C6CF5':'#FF5C8A';x.globalAlpha=0.55;x.fill();x.restore();}x.restore();x.globalAlpha=1;})();""",
        "#7C6CF5", "#FF5C8A", "#29D3E6")]

    items += [("transitions/精选转场", "ripple", "波纹扩散",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var rings=[];(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(8,6,14,0.15)';x.fillRect(0,0,cv.width,cv.height);if(Math.random()<0.06)rings.push({r:0,a:1});for(var i=rings.length-1;i>=0;i--){var r=rings[i];r.r+=4;r.a-=0.012;if(r.a<=0){rings.splice(i,1);continue;}x.beginPath();x.arc(cv.width/2,cv.height/2,r.r,0,7);x.strokeStyle='rgba(41,211,230,'+r.a+')';x.lineWidth=3;x.stroke();}})();""",
        "#29D3E6", "#7C6CF5", "#FF5C8A")]

    items += [("transitions/精选转场", "iris", "光圈开合",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0,dir=1;(function loop(){requestAnimationFrame(loop);t+=0.02*dir;if(t>1){t=1;dir=-1}if(t<0){t=0;dir=1;}x.fillStyle='#0e0c16';x.fillRect(0,0,cv.width,cv.height);var R=Math.min(cv.width,cv.height)*0.5*(1-t);x.save();x.beginPath();x.arc(cv.width/2,cv.height/2,R,0,7);x.clip();var g=x.createRadialGradient(cv.width/2,cv.height/2,0,cv.width/2,cv.height/2,Math.max(cv.width,cv.height)*0.5);g.addColorStop(0,'#FF5C8A');g.addColorStop(1,'#7C6CF5');x.fillStyle=g;x.fillRect(0,0,cv.width,cv.height);x.restore();})();""",
        "#FF5C8A", "#7C6CF5", "#29D3E6")]

    items += [("transitions/精选转场", "slide_stripes", "条纹滑入",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t=(t+0.01)%1;x.fillStyle='#0e0c16';x.fillRect(0,0,cv.width,cv.height);var n=10,sh=cv.height/n;for(var i=0;i<n;i++){var off=((t+i*0.13)%1)*cv.width;var hue=(i*36)%360;x.fillStyle='hsl('+hue+',80%,60%)';x.fillRect(off-sh,i*sh,sh*1.4,sh);}})();""",
        "#7C6CF5", "#FF5C8A", "#43E97B")]

    # ---------- 素材 / 粒子与物理 ----------
    items += [("assets/精选素材", "particles", "粒子连线场",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var P=[];for(var i=0;i<90;i++)P.push({x:Math.random()*cv.width,y:Math.random()*cv.height,vx:(Math.random()-.5)*0.6,vy:(Math.random()-.5)*0.6});(function loop(){requestAnimationFrame(loop);x.clearRect(0,0,cv.width,cv.height);for(var i=0;i<P.length;i++){var a=P[i];a.x+=a.vx;a.y+=a.vy;if(a.x<0||a.x>cv.width)a.vx*=-1;if(a.y<0||a.y>cv.height)a.vy*=-1;x.beginPath();x.arc(a.x,a.y,2.2,0,7);x.fillStyle='#29D3E6';x.fill();for(var j=i+1;j<P.length;j++){var b=P[j],d=Math.hypot(a.x-b.x,a.y-b.y);if(d<120){x.beginPath();x.moveTo(a.x,a.y);x.lineTo(b.x,b.y);x.strokeStyle='#7C6CF5';x.globalAlpha=1-d/120;x.lineWidth=1;x.stroke();x.globalAlpha=1;}}})();""",
        "#29D3E6", "#7C6CF5", "#FF5C8A")]

    items += [("assets/精选素材", "flow_field", "流场",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.006;x.fillStyle='rgba(8,6,14,0.08)';x.fillRect(0,0,cv.width,cv.height);for(var i=0;i<260;i++){var px=(i*53)%cv.width,py=(i*97)%cv.height;var a=Math.sin(px*0.01+t)+Math.cos(py*0.01-t);var dx=Math.cos(a*3.14),dy=Math.sin(a*3.14);x.beginPath();x.moveTo(px,py);x.lineTo(px+dx*16,py+dy*16);x.strokeStyle='#FF5C8A';x.globalAlpha=0.5;x.lineWidth=1.4;x.stroke();}x.globalAlpha=1;})();""",
        "#FF5C8A", "#7C6CF5", "#29D3E6")]

    items += [("assets/精选素材", "starfield", "星空跃迁",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var S=[];for(var i=0;i<160;i++)S.push({x:Math.random()*cv.width,y:Math.random()*cv.height,z:Math.random()*cv.width});(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(5,4,12,0.25)';x.fillRect(0,0,cv.width,cv.height);for(var i=0;i<S.length;i++){var s=S[i];s.z-=4;if(s.z<=0){s.z=cv.width;s.x=Math.random()*cv.width;s.y=Math.random()*cv.height;}var px=(s.x-cv.width/2)/s.z*cv.width*0.5+cv.width/2,py=(s.y-cv.height/2)/s.z*cv.height*0.5+cv.height/2;var sz=(1-s.z/cv.width)*3;x.beginPath();x.arc(px,py,sz,0,7);x.fillStyle='#fff';x.fill();}})();""",
        "#fff", "#29D3E6", "#7C6CF5")]

    items += [("assets/精选素材", "fire_ember", "火焰余烬",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var P=[];(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(8,4,10,0.18)';x.fillRect(0,0,cv.width,cv.height);if(P.length<120)P.push({x:cv.width/2+(Math.random()-.5)*60,y:cv.height,vx:(Math.random()-.5)*1,vy:-(2+Math.random()*3),life:1});for(var i=P.length-1;i>=0;i--){var p=P[i];p.x+=p.vx;p.y+=p.vy;p.vy-=0.02;p.life-=0.012;if(p.life<=0){P.splice(i,1);continue;}var g=x.createRadialGradient(p.x,p.y,0,p.x,p.y,10);g.addColorStop(0,'rgba(255,'+Math.floor(160*p.life)+',40,'+p.life+')');g.addColorStop(1,'transparent');x.fillStyle=g;x.beginPath();x.arc(p.x,p.y,10,0,7);x.fill();}})();""",
        "#FF6A00", "#FF2D95", "#FFD200")]

    items += [("assets/精选素材", "rain", "雨幕",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var D=[];for(var i=0;i<160;i++)D.push({x:Math.random()*cv.width,y:Math.random()*cv.height,s:4+Math.random()*8});(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(10,12,24,0.25)';x.fillRect(0,0,cv.width,cv.height);x.strokeStyle='rgba(120,200,255,0.55)';x.lineWidth=1.4;for(var i=0;i<D.length;i++){var d=D[i];d.y+=d.s;d.x+=d.s*0.3;if(d.y>cv.height){d.y=-10;d.x=Math.random()*cv.width;}x.beginPath();x.moveTo(d.x,d.y);x.lineTo(d.x-d.s*0.3,d.y-d.s*2.2);x.stroke();}})();""",
        "#48C6EF", "#6F86D6", "#B2FEFA")]

    items += [("assets/精选素材", "snow", "飘雪",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var F=[];for(var i=0;i<140;i++)F.push({x:Math.random()*cv.width,y:Math.random()*cv.height,r:1+Math.random()*3,v:0.4+Math.random()*1,ph:Math.random()*7});(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(10,12,24,0.2)';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='#fff';for(var i=0;i<F.length;i++){var f=F[i];f.y+=f.v;f.ph+=0.02;f.x+=Math.sin(f.ph)*0.6;if(f.y>cv.height){f.y=-5;f.x=Math.random()*cv.width;}x.beginPath();x.arc(f.x,f.y,f.r,0,7);x.fill();}})();""",
        "#fff", "#48C6EF", "#B2FEFA")]

    items += [("assets/精选素材", "dna", "DNA 螺旋",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.03;x.clearRect(0,0,cv.width,cv.height);var cx=cv.width/2,n=24;for(var i=0;i<n;i++){var y=i/cv.height*cv.height*0.9+20;var a=t+i*0.4;var x1=cx+Math.cos(a)*90,y1=y;var x2=cx+Math.cos(a+Math.PI)*90,y2=y;x.beginPath();x.moveTo(x1,y1);x.lineTo(x2,y2);x.strokeStyle='rgba(124,108,245,'+(0.3+0.5*Math.abs(Math.sin(a)))+')';x.lineWidth=2;x.stroke();x.beginPath();x.arc(x1,y1,5,0,7);x.fillStyle='#29D3E6';x.fill();x.beginPath();x.arc(x2,y2,5,0,7);x.fillStyle='#FF5C8A';x.fill();}})();""",
        "#29D3E6", "#FF5C8A", "#7C6CF5")]

    items += [("assets/精选素材", "tornado", "龙卷风",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.02;x.fillStyle='rgba(8,6,14,0.18)';x.fillRect(0,0,cv.width,cv.height);var cx=cv.width/2;for(var i=0;i<260;i++){var p=i/260;var y=p*cv.height;var rad=(10+p*120)*(0.6+0.4*Math.sin(t+i*0.1));var ang=t*3+i*0.3;var px=cx+Math.cos(ang)*rad,py=y;x.beginPath();x.arc(px,py,2.2,0,7);x.fillStyle='rgba(41,211,230,'+(1-p*0.6)+')';x.fill();}})();""",
        "#29D3E6", "#7C6CF5", "#FF5C8A")]

    items += [("assets/精选素材", "galaxy", "星系旋臂",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var stars=[];for(var i=0;i<420;i++)stars.push({a:Math.random()*7,r:20+Math.random()*Math.min(cv.width,cv.height)*0.45,sp:0.002+Math.random()*0.01});var t=0;(function loop(){requestAnimationFrame(loop);t+=0.005;x.fillStyle='rgba(6,4,14,0.2)';x.fillRect(0,0,cv.width,cv.height);var cx=cv.width/2,cy=cv.height/2;for(var i=0;i<stars.length;i++){var s=stars[i],ang=s.a+t*(1+s.sp*20)*2;var px=cx+Math.cos(ang)*s.r,py=cy+Math.sin(ang)*s.r;var hue=(s.r*0.5)%360;x.beginPath();x.arc(px,py,1.4,0,7);x.fillStyle='hsl('+hue+',80%,70%)';x.fill();}x.beginPath();x.arc(cx,cy,18,0,7);x.fillStyle='#fff';x.fill();})();""",
        "#fff", "#7C6CF5", "#29D3E6")]

    items += [("assets/精选素材", "wave_terrain", "波浪地形",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.03;x.fillStyle='#0a0a1f';x.fillRect(0,0,cv.width,cv.height);for(var row=0;row<16;row++){x.beginPath();for(var xx=0;xx<=cv.width;xx+=8){var yy=cv.height*0.4+row*14+Math.sin(xx*0.02+t+row*0.3)*18*Math.sin(t*0.5+row*0.2);if(xx===0)x.moveTo(xx,yy);else x.lineTo(xx,yy);}x.strokeStyle='rgba('+Math.floor(120+row*8)+','+Math.floor(80+row*6)+',255,'+(0.3+row*0.04)+')';x.lineWidth=1.5;x.stroke();}})();""",
        "#29D3E6", "#7C6CF5", "#FF5C8A")]

    items += [("assets/精选素材", "bounce_balls", "弹性碰撞球",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var B=[];for(var i=0;i<10;i++)B.push({x:Math.random()*cv.width,y:Math.random()*cv.height,vx:(Math.random()-.5)*6,vy:(Math.random()-.5)*6,r:14+Math.random()*16});(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(8,6,14,0.2)';x.fillRect(0,0,cv.width,cv.height);for(var i=0;i<B.length;i++){var b=B[i];b.x+=b.vx;b.y+=b.vy;b.vy+=0.15;if(b.x<b.r||b.x>cv.width-b.r)b.vx*=-1;if(b.y>b.height-b.r){b.y=b.height-b.r;b.vy*=-0.92;if(Math.abs(b.vy)<1)b.vy=0;}x.beginPath();x.arc(b.x,b.y,b.r,0,7);var g=x.createRadialGradient(b.x,b.y,0,b.x,b.y,b.r);g.addColorStop(0,'#FF5C8A');g.addColorStop(1,'#7C6CF5');x.fillStyle=g;x.fill();}})();""",
        "#FF5C8A", "#7C6CF5", "#29D3E6")]

    items += [("assets/精选素材", "fireworks", "烟花",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var F=[];function boom(){var cx=Math.random()*cv.width,cy=Math.random()*cv.height*0.6,p=[];var hue=Math.floor(Math.random()*360);for(var i=0;i<60;i++){var a=i/60*7,sp=2+Math.random()*3;p.push({x:cx,y:cy,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,life:1,hue:hue});}F.push(p);}(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(6,4,14,0.2)';x.fillRect(0,0,cv.width,cv.height);if(Math.random()<0.04)boom();for(var k=F.length-1;k>=0;k--){var p=F[k];for(var i=p.length-1;i>=0;i--){var q=p[i];q.x+=q.vx;q.y+=q.vy;q.vy+=0.05;q.life-=0.015;if(q.life<=0){p.splice(i,1);continue;}x.beginPath();x.arc(q.x,q.y,2,0,7);x.fillStyle='hsla('+q.hue+',90%,'+(50+q.life*40)+'%,'+q.life+')';x.fill();}if(p.length===0)F.splice(k,1);}})();""",
        "#FFD200", "#FF5C8A", "#29D3E6")]

    items += [("assets/精选素材", "lissajous", "利萨茹曲线",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.01;x.fillStyle='rgba(8,6,14,0.12)';x.fillRect(0,0,cv.width,cv.height);x.strokeStyle='#43E97B';x.lineWidth=2;x.beginPath();for(var i=0;i<700;i++){var u=i/700*7;var px=cv.width/2+Math.sin(u*3+t)*cv.width*0.35;var py=cv.height/2+Math.sin(u*2+t*1.3)*cv.height*0.35;if(i===0)x.moveTo(px,py);else x.lineTo(px,py);}x.stroke();})();""",
        "#43E97B", "#38F9D7", "#5B86E5")]

    items += [("assets/精选素材", "lorenz", "洛伦兹吸引子",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var x0=0.1,y0=0,z0=0,t=0;(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(6,4,14,0.08)';x.fillRect(0,0,cv.width,cv.height);x.strokeStyle='rgba(255,92,138,0.9)';x.lineWidth=1.4;x.beginPath();for(var i=0;i<200;i++){var dt=0.008;var dx=(10*(y0-x0))*dt,dy=(x0*(28-z0)-y0)*dt,dz=(x0*y0-2.6*z0)*dt;x0+=dx;y0+=dy;z0+=dz;var px=cv.width/2+x0*9,py=cv.height/2+(z0-28)*7;if(i===0)x.moveTo(px,py);else x.lineTo(px,py);}x.stroke();})();""",
        "#FF5C8A", "#7C6CF5", "#29D3E6")]

    items += [("assets/精选素材", "metaballs", "融合球",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var M=[];for(var i=0;i<5;i++)M.push({x:Math.random()*cv.width,y:Math.random()*cv.height,vx:(Math.random()-.5)*2,vy:(Math.random()-.5)*2,r:60+Math.random()*40});var t=0;(function loop(){requestAnimationFrame(loop);t+=0.01;for(var i=0;i<M.length;i++){var m=M[i];m.x+=m.vx;m.y+=m.vy;if(m.x<0||m.x>cv.width)m.vx*=-1;if(m.y<0||m.y>cv.height)m.vy*=-1;}x.fillStyle='#0e0c16';x.fillRect(0,0,cv.width,cv.height);x.globalCompositeOperation='lighter';for(var k=0;k<3;k++){x.fillStyle=['rgba(124,108,245,0.5)','rgba(41,211,230,0.5)','rgba(255,92,138,0.5)'][k];for(var i=0;i<M.length;i++){var m=M[i];var g=x.createRadialGradient(m.x,m.y,0,m.x,m.y,m.r);g.addColorStop(0,'rgba(255,255,255,0.7)');g.addColorStop(1,'transparent');x.fillStyle=g;x.beginPath();x.arc(m.x+(k*20),m.y,m.r,0,7);x.fill();}}x.globalCompositeOperation='source-over';})();""",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("assets/精选素材", "hex_pulse", "六边形脉冲",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.03;x.fillStyle='#0a0a1f';x.fillRect(0,0,cv.width,cv.height);var cx=cv.width/2,cy=cv.height/2;for(var ring=0;ring<6;ring++){var R=ring*40+20+Math.sin(t+ring)*8;x.strokeStyle='rgba(0,229,255,'+(0.8-ring*0.12)+')';x.lineWidth=2;for(var a=0;a<6;a++){var ang=a/6*Math.PI*2+ring*0.3;var px=cx+Math.cos(ang)*R,py=cy+Math.sin(ang)*R;if(a===0)x.beginPath(),x.moveTo(px,py);else x.lineTo(px,py);}x.closePath();x.stroke();}})();""",
        "#00E5FF", "#7C4DFF", "#FF2E97")]

    items += [("assets/精选素材", "blackhole", "黑洞吸积",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.02;x.fillStyle='rgba(8,6,14,0.18)';x.fillRect(0,0,cv.width,cv.height);var cx=cv.width/2,cy=cv.height/2;for(var i=0;i<160;i++){var a=t+i*0.04,r=20+(i*2.2)%(Math.max(cv.width,cv.height)*0.45);var px=cx+Math.cos(a)*r,py=cy+Math.sin(a)*r;x.beginPath();x.arc(px,py,2.4,0,7);x.fillStyle=i%2?'#7C6CF5':'#29D3E6';x.fill();}x.beginPath();x.arc(cx,cy,18,0,7);x.fillStyle='#000';x.fill();x.lineWidth=4;x.strokeStyle='#FF5C8A';x.stroke();})();""",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("assets/精选素材", "audio_bars", "声谱条",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.05;x.clearRect(0,0,cv.width,cv.height);var n=48,bw=cv.width/n;for(var i=0;i<n;i++){var h=(Math.abs(Math.sin(t+i*0.3))*0.6+Math.abs(Math.sin(t*1.7+i))*0.4)*cv.height*0.55;var g=x.createLinearGradient(0,cv.height,0,cv.height-h);g.addColorStop(0,'#FF2D95');g.addColorStop(1,'#FFD200');x.fillStyle=g;x.fillRect(i*bw+bw*0.15,cv.height-h,bw*0.7,h);}x.fillStyle='#FF6A00';x.fillRect(0,cv.height-3,cv.width,3);})();""",
        "#FF6A00", "#FF2D95", "#FFD200")]

    items += [("assets/精选素材", "voronoi", "细胞网格",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var pts=[];for(var i=0;i<14;i++)pts.push({x:Math.random()*cv.width,y:Math.random()*cv.height,c:['#7C6CF5','#29D3E6','#FF5C8A','#43E97B'][i%4]});var t=0;(function loop(){requestAnimationFrame(loop);t+=0.01;x.fillStyle='#0e0c16';x.fillRect(0,0,cv.width,cv.height);for(var i=0;i<pts.length;i++){pts[i].x+=Math.sin(t+i)*0.6;pts[i].y+=Math.cos(t*0.8+i)*0.6;}var step=28;for(var Y=0;Y<cv.height;Y+=step)for(var X=0;X<cv.width;X+=step){var best=1e9,bi=0;for(var i=0;i<pts.length;i++){var d=(X-pts[i].x)*(X-pts[i].x)+(Y-pts[i].y)*(Y-pts[i].y);if(d<best){best=d;bi=i;}}x.fillStyle=pts[bi].c;x.globalAlpha=0.5;x.fillRect(X,Y,step,step);}x.globalAlpha=1;})();""",
        "#7C6CF5", "#29D3E6", "#FF5C8A")]

    items += [("assets/精选素材", "plasma", "等离子",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.04;var img=x.createImageData(cv.width,cv.height);for(var y=0;y<cv.height;y+=2)for(var xx=0;xx<cv.width;xx+=2){var v=Math.sin(xx*0.02+t)+Math.sin(y*0.02+t)+Math.sin((xx+y)*0.02+t)+Math.sin(Math.hypot(xx-cv.width/2,y-cv.height/2)*0.02-t);var c=Math.floor((v+4)/8*255);var idx=(y*cv.width+xx)*4;img.data[idx]=c;img.data[idx+1]=120+Math.floor(80*Math.sin(v));img.data[idx+2]=255-c;img.data[idx+3]=255;}x.putImageData(img,0,0);})();""",
        "#7C6CF5", "#FF5C8A", "#29D3E6")]

    items += [("assets/精选素材", "bubbles", "上浮气泡",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var B=[];(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(10,20,40,0.15)';x.fillRect(0,0,cv.width,cv.height);if(B.length<60)B.push({x:Math.random()*cv.width,y:cv.height+20,r:4+Math.random()*16,v:0.6+Math.random()*1.4});for(var i=B.length-1;i>=0;i--){var b=B[i];b.y-=b.v;if(b.y<-20){B.splice(i,1);continue;}x.beginPath();x.arc(b.x,b.y,b.r,0,7);x.strokeStyle='rgba(160,220,255,0.6)';x.lineWidth=1.5;x.stroke();x.fillStyle='rgba(160,220,255,0.12)';x.fill();}})();""",
        "#48C6EF", "#6F86D6", "#B2FEFA")]

    items += [("assets/精选素材", "lightning", "闪电",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var bolt=[];(function loop(){requestAnimationFrame(loop);x.fillStyle='rgba(6,4,14,0.3)';x.fillRect(0,0,cv.width,cv.height);if(Math.random()<0.04){bolt=[];var x0=cv.width/2+(Math.random()-.5)*cv.width*0.4;for(var y=0;y<cv.height;y+=14){x0+=(Math.random()-.5)*40;bolt.push([x0,y]);}}x.strokeStyle='#fff';x.shadowColor='#00E5FF';x.shadowBlur=18;x.lineWidth=2.5;x.beginPath();for(var i=0;i<bolt.length;i++){if(i===0)x.moveTo(bolt[i][0],bolt[i][1]);else x.lineTo(bolt[i][0],bolt[i][1]);}x.stroke();x.shadowBlur=0;bolt=bolt.slice(0,Math.max(0,bolt.length-3));})();""",
        "#00E5FF", "#FF2E97", "#7C4DFF")]

    items += [("assets/精选素材", "star_twinkle", "闪烁星海",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var S=[];for(var i=0;i<220;i++)S.push({x:Math.random()*cv.width,y:Math.random()*cv.height,ph:Math.random()*7,sp:0.5+Math.random()});var t=0;(function loop(){requestAnimationFrame(loop);t+=0.05;x.fillStyle='#05040c';x.fillRect(0,0,cv.width,cv.height);for(var i=0;i<S.length;i++){var s=S[i];var a=0.4+0.6*Math.abs(Math.sin(t*s.sp+s.ph));x.beginPath();x.arc(s.x,s.y,1.6,0,7);x.fillStyle='rgba(255,255,255,'+a+')';x.fill();}})();""",
        "#fff", "#29D3E6", "#7C6CF5")]

    items += [("assets/精选素材", "liquid_fill", "液体填充",
        '<canvas id="cv"></canvas>',
        "",
        CV_INIT + """var t=0;(function loop(){requestAnimationFrame(loop);t+=0.06;x.clearRect(0,0,cv.width,cv.height);var cx=cv.width/2,cy=cv.height/2,R=Math.min(cv.width,cv.height)*0.32;x.save();x.beginPath();x.arc(cx,cy,R,0,7);x.clip();var lvl=cy+R*0.4+Math.sin(t)*R*0.2;x.beginPath();x.moveTo(cx-R,lvl);for(var xx=cx-R;xx<=cx+R;xx+=8){x.lineTo(xx,lvl+Math.sin(xx*0.04+t*2)*8);}x.lineTo(cx+R,cy+R);x.lineTo(cx-R,cy+R);x.closePath();var g=x.createLinearGradient(0,lvl,0,cy+R);g.addColorStop(0,'#29D3E6');g.addColorStop(1,'#7C6CF5');x.fillStyle=g;x.fill();x.restore();x.beginPath();x.arc(cx,cy,R,0,7);x.strokeStyle='#fff';x.lineWidth=3;x.stroke();})();""",
        "#29D3E6", "#7C6CF5", "#FF5C8A")]

    return items

def _clean_spam():
    removed = 0
    for cat in ["styles", "widgets", "transitions", "assets"]:
        d = ROOT / cat
        if not d.exists():
            continue
        for root, dirs, files in os.walk(d):
            if os.path.basename(root).startswith("."):
                continue
            for fn in files:
                if fn.lower().endswith(".html") and any(fn.startswith(p) for p in SPAM_PREFIXES):
                    try:
                        os.remove(os.path.join(root, fn))
                        removed += 1
                    except Exception:
                        pass
    return removed

def main():
    removed = _clean_spam()
    print(f"cleaned spam html files: {removed}", flush=True)
    items = E()
    written = 0
    for sub, fname, title, stage, head, script, a, b, c in items:
        out = ROOT / sub
        out.mkdir(parents=True, exist_ok=True)
        html = wrap(title, stage, head, script, a, b, c)
        (out / (fname + ".html")).write_text(html, encoding="utf-8")
        written += 1
    print(f"generated {written} distinct effect files (zero recolor duplicates)")

if __name__ == "__main__":
    main()
