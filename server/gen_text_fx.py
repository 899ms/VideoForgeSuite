#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 18 种结构各异的文字入场 HTML 动效（自包含、零外部依赖、背景辉光）
每种模板独立视觉技法：CSS keyframes / Canvas / SVG filter。
输出到 materials/styles/文字入场/ 命名 txt_<name>.html
"""
from pathlib import Path

OUT = Path(r"D:/VideoForgeSuite/materials/styles/文字入场")
OUT.mkdir(parents=True, exist_ok=True)

# 通用头尾（背景辉光保证 headless 截图明亮，任意帧可见）
HEAD = """<!doctype html><html lang=zh><head><meta charset=utf-8>
<style>html,body{margin:0;height:100%;overflow:hidden;background:radial-gradient(120% 120% at 18% 8%, #5B8CFF66 0%, transparent 55%),radial-gradient(120% 120% at 86% 92%, #FF5C8A66 0%, transparent 55%),radial-gradient(120% 120% at 50% 50%, #29D3E655 0%, transparent 62%),linear-gradient(135deg,#141228,#241f3d);display:flex;align-items:center;justify-content:center;font-family:'Segoe UI',system-ui,sans-serif}
"""

# 模板: name -> (head_css, body_html, body_js)
TEMPLATES = {}

TEMPLATES["typewriter"] = ("""
.t{color:#fff;font-size:44px;font-weight:800;letter-spacing:2px;white-space:pre}
.cursor{display:inline-block;width:3px;height:48px;background:#29D3E6;vertical-align:-8px;animation:blink .8s steps(1) infinite;margin-left:2px}
@keyframes blink{50%{opacity:0}}
""",
"""<div class="t" id="t"></div><span class="cursor" id="c"></span>""",
"""var txt="VIDEO FORGE";var i=0,el=document.getElementById('t');
window.__iv=setInterval(function(){if(i<=txt.length){el.textContent=txt.slice(0,i);i++;}},110);""")

TEMPLATES["char_pop"] = ("""
.ch{display:inline-block;color:#fff;font-size:46px;font-weight:800;animation:pop .6s cubic-bezier(.2,1.6,.4,1) both;text-shadow:0 0 18px rgba(124,108,245,.8)}
@keyframes pop{0%{opacity:0;transform:translateY(40px) scale(.3)}60%{opacity:1}100%{opacity:1;transform:translateY(0) scale(1)}}
""",
"""<div id="w"></div>""",
"""var s="POP IN";var w=document.getElementById('w');
for(var i=0;i<s.length;i++){var sp=document.createElement('span');sp.className='ch';sp.textContent=s[i]===' '?'\\u00A0':s[i];sp.style.animationDelay=(i*0.07)+'s';w.appendChild(sp);}""")

TEMPLATES["flip3d"] = ("""
.ch{display:inline-block;color:#fff;font-size:44px;font-weight:800;transform-style:preserve-3d;animation:flip .8s ease both;text-shadow:0 0 14px rgba(41,211,230,.7)}
@keyframes flip{0%{opacity:0;transform:rotateX(90deg) translateY(-30px)}100%{opacity:1;transform:rotateX(0) translateY(0)}}
""",
"""<div id="w"></div>""",
"""var s="FLIP 3D";var w=document.getElementById('w');
for(var i=0;i<s.length;i++){var sp=document.createElement('span');sp.className='ch';sp.textContent=s[i];sp.style.animationDelay=(i*0.09)+'s';w.appendChild(sp);}""")

TEMPLATES["neon_outline"] = ("""
.t{font-size:52px;font-weight:800;color:transparent;-webkit-text-stroke:2px #29D3E6;animation:nGlow 1.6s ease-in-out infinite alternate;letter-spacing:3px}
@keyframes nGlow{from{text-shadow:0 0 8px rgba(41,211,230,.4),0 0 22px rgba(41,211,230,.2)}to{text-shadow:0 0 14px rgba(41,211,230,.9),0 0 40px rgba(41,211,230,.5),0 0 70px rgba(124,108,245,.4)}}
""",
"""<div class="t">NEON</div>""", "")

TEMPLATES["gradient_fill"] = ("""
.t{font-size:58px;font-weight:900;background:linear-gradient(90deg,#FF5C8A,#7C6CF5,#29D3E6,#FFC75F,#FF5C8A);background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:flow 3s linear infinite;letter-spacing:2px}
@keyframes flow{to{background-position:300% 0}}
""",
"""<div class="t">GRADIENT</div>""", "")

TEMPLATES["stroke_draw"] = ("""
svg{width:520px;height:120px}
path{fill:none;stroke:#FFC75F;stroke-width:3;stroke-dasharray:600;stroke-dashoffset:600;animation:draw 2.2s ease forwards;filter:drop-shadow(0 0 8px rgba(255,199,95,.6))}
@keyframes draw{to{stroke-dashoffset:0}}
""",
"""<svg viewBox="0 0 520 120"><path d="M20,80 L70,80 L95,30 L120,110 L150,40 L175,80 L220,80 M260,30 L260,110 M260,55 L300,55 M260,80 L305,80 M340,30 L340,110 L400,110 M340,70 L390,70 M430,30 L430,110 M430,30 L470,30 M430,70 L465,70 M430,110 L470,110"/></svg>""", "")

TEMPLATES["particle_dissolve"] = ("""
#cv{position:absolute;inset:0}
.t{position:absolute;color:#fff;font-size:54px;font-weight:800;text-shadow:0 0 16px rgba(124,108,245,.8);pointer-events:none}
""",
"""<canvas id="cv"></canvas><div class="t" id="t">DISSOLVE</div>""",
"""var cv=document.getElementById('cv'),ctx=cv.getContext('2d');cv.width=cv.offsetWidth||520;cv.height=cv.offsetHeight||200;
var t=document.getElementById('t');var rect=t.getBoundingClientRect();
var parts=[];for(var i=0;i<90;i++){parts.push({x:rect.left+Math.random()*rect.width,y:rect.top+Math.random()*rect.height,vx:(Math.random()-.5)*2,vy:-Math.random()*2-0.5,a:1});}
var f=0;function tick(){ctx.clearRect(0,0,cv.width,cv.height);f++;
 for(var i=0;i<parts.length;i++){var p=parts[i];p.x+=p.vx;p.y+=p.vy;p.a-=0.006;
  ctx.fillStyle='rgba(255,255,255,'+Math.max(0,p.a)+')';ctx.beginPath();ctx.arc(p.x,p.y,2.2,0,7);ctx.fill();}
 if(f<220){window.__iv=setTimeout(tick,16);}}tick();""")

TEMPLATES["elastic_bounce"] = ("""
.t{color:#FFC75F;font-size:52px;font-weight:900;animation:el 1.4s cubic-bezier(.68,-0.55,.27,1.55) both;text-shadow:0 0 20px rgba(255,199,95,.5)}
@keyframes el{0%{opacity:0;transform:scale(0)}60%{opacity:1;transform:scale(1.15)}80%{transform:scale(.94)}100%{opacity:1;transform:scale(1)}}
""",
"""<div class="t">BOUNCE!</div>""", "")

TEMPLATES["matrix_rain"] = ("""
#cv{position:absolute;inset:0}
.t{position:absolute;color:#7C6CF5;font-size:52px;font-weight:900;text-shadow:0 0 22px rgba(124,108,245,.7);pointer-events:none}
""",
"""<canvas id="cv"></canvas><div class="t">MATRIX</div>""",
"""var cv=document.getElementById('cv'),ctx=cv.getContext('2d');cv.width=cv.width=cv.offsetWidth||520;cv.height=cv.offsetHeight||220;
var cols=Math.floor(cv.width/18),drops=[];for(var i=0;i<cols;i++)drops[i]=Math.random()*-30;
var chars='アイウエオカキクケコサシスセソ0123456789';
function tick(){ctx.fillStyle='rgba(13,10,26,0.12)';ctx.fillRect(0,0,cv.width,cv.height);ctx.font='15px monospace';
 for(var i=0;i<cols;i++){var ch=chars[Math.floor(Math.random()*chars.length)];
  ctx.fillStyle=(Math.random()>0.97)?'#FFC75F':'#29D3E6';ctx.fillText(ch,i*18,drops[i]*18);
  if(drops[i]*18>cv.height&&Math.random()>0.975)drops[i]=0;drops[i]++;}}
window.__iv=setInterval(tick,45);""")

TEMPLATES["burn_in"] = ("""
.t{position:relative;font-size:56px;font-weight:900;color:#FF5C8A;animation:shake .3s infinite;text-shadow:0 0 26px rgba(255,92,138,.9),0 -6px 14px #FFC75F}
@keyframes shake{0%,100%{transform:translate(0,0)}25%{transform:translate(-2px,1px)}75%{transform:translate(2px,-1px)}}
.t::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,rgba(255,199,95,.5) 60%,transparent 85%);mix-blend-mode:screen;animation:flicker .5s steps(2) infinite}
@keyframes flicker{50%{opacity:.4}}
""",
"""<div class="t">BURN</div>""", "")

TEMPLATES["liquid_text"] = ("""
svg{width:560px;height:150px;overflow:visible}
text{font-size:70px;font-weight:900;fill:#29D3E6;filter:url(#goo);animation:liq 2.4s ease-in-out infinite alternate}
@keyframes liq{from{transform:scale(1) rotate(0)}to{transform:scale(1.06) rotate(-1.2deg)}}
""",
"""<svg viewBox="0 0 560 150"><defs><filter id="goo"><feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves="3" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="14"/></filter></defs><text x="280" y="105" text-anchor="middle">LIQUID</text></svg>""", "")

TEMPLATES["metal_shine"] = ("""
.t{font-size:58px;font-weight:900;letter-spacing:2px;background:linear-gradient(100deg,#8a8a9a 20%,#fff 40%,#8a8a9a 60%,#c8c8d8 80%);background-size:220% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 2.2s linear infinite}
@keyframes shine{from{background-position:220% 0}to{background-position:-220% 0}}
""",
"""<div class="t">METAL</div>""", "")

TEMPLATES["scan_highlight"] = ("""
.t{position:relative;font-size:56px;font-weight:900;color:#fff;letter-spacing:2px}
.t::before{content:attr(data-t);position:absolute;inset:0;color:#FF5C8A;clip-path:inset(0 100% 0 0);animation:scan 2s linear infinite}
@keyframes scan{0%{clip-path:inset(0 100% 0 0)}100%{clip-path:inset(0 0 0 0)}}
""",
"""<div class="t" data-t="SCAN">SCAN</div>""", "")

TEMPLATES["blur_in"] = ("""
.t{font-size:56px;font-weight:900;color:#fff;animation:bl 1.6s ease both;text-shadow:0 0 20px rgba(41,211,230,.5)}
@keyframes bl{0%{opacity:0;filter:blur(22px);letter-spacing:14px}100%{opacity:1;filter:blur(0);letter-spacing:2px}}
""",
"""<div class="t">BLUR IN</div>""", "")

TEMPLATES["roll_in"] = ("""
.t{font-size:52px;font-weight:900;color:#FFC75F;animation:roll 1.1s cubic-bezier(.2,1.3,.4,1) both;text-shadow:0 0 18px rgba(255,199,95,.5)}
@keyframes roll{0%{opacity:0;transform:rotateY(140deg) translateX(-60px)}100%{opacity:1;transform:rotateY(0) translateX(0)}}
""",
"""<div class="t">ROLL IN</div>""", "")

TEMPLATES["wave_letters"] = ("""
.ch{display:inline-block;color:#29D3E6;font-size:48px;font-weight:800;animation:wave 1.2s ease-in-out infinite;text-shadow:0 0 16px rgba(41,211,230,.7)}
@keyframes wave{0%,100%{transform:translateY(0)}50%{transform:translateY(-26px)}}
""",
"""<div id="w"></div>""",
"""var s="WAVE!";var w=document.getElementById('w');
for(var i=0;i<s.length;i++){var sp=document.createElement('span');sp.className='ch';sp.textContent=s[i]===' '?'\\u00A0':s[i];sp.style.animationDelay=(i*0.1)+'s';w.appendChild(sp);}""")

TEMPLATES["glitch_split"] = ("""
.t{position:relative;font-size:56px;font-weight:900;color:#fff}
.t::before,.t::after{content:attr(data-t);position:absolute;left:0;top:0;width:100%;opacity:.85;mix-blend-mode:screen}
.t::before{color:#FF5C8A;clip-path:inset(0 0 55% 0);animation:g1 2.4s steps(2) infinite}
.t::after{color:#29D3E6;clip-path:inset(55% 0 0 0);animation:g2 2.1s steps(2) infinite}
@keyframes g1{0%,92%{transform:translate(0,0)}94%{transform:translate(-6px,2px)}98%{transform:translate(4px,-2px)}100%{transform:translate(0,0)}}
@keyframes g2{0%,90%{transform:translate(0,0)}93%{transform:translate(5px,-2px)}97%{transform:translate(-4px,1px)}100%{transform:translate(0,0)}}
""",
"""<div class="t" data-t="GLITCH">GLITCH</div>""", "")

TEMPLATES["counter_pop"] = ("""
#n{color:#FFC75F;font-size:74px;font-weight:900;text-shadow:0 0 26px rgba(255,199,95,.6)}
.lbl{color:#fff9;font-size:16px;letter-spacing:3px;margin-top:6px;text-align:center}
""",
"""<div style="text-align:center"><div id="n">0</div><div class="lbl">VIEWS</div></div>""",
"""var el=document.getElementById('n'),v=0;
window.__iv=setInterval(function(){v+=137;el.textContent=v;el.style.transform='scale('+(1+Math.sin(v/50)*0.03)+')';if(v>=12345){v=12345;el.textContent=v;clearInterval(window.__iv);}},30);""")

TEMPLATES["mask_reveal"] = ("""
.t{position:relative;font-size:54px;font-weight:900;color:transparent;-webkit-text-stroke:2px #7C6CF5}
.t::after{content:attr(data-t);position:absolute;inset:0;color:#fff;clip-path:inset(0 100% 0 0);animation:mask 2s ease forwards}
@keyframes mask{to{clip-path:inset(0 0 0 0)}}
""",
"""<div class="t" data-t="REVEAL">REVEAL</div>""", "")

TEMPLATES["shadow_3d"] = ("""
.t{color:#fff;font-size:58px;font-weight:900;animation:sh 2s ease-in-out infinite alternate;text-shadow:3px 3px 0 #FF5C8A,6px 6px 0 #7C6CF5,9px 9px 0 rgba(41,211,230,.5)}
@keyframes sh{from{transform:translate(0,0)}to{transform:translate(-4px,-4px)}}
""",
"""<div class="t">3D SHADOW</div>""", "")

def build(name):
    css, body, js = TEMPLATES[name]
    js_block = f"<script>{js}</script>" if js else ""
    # 冻结脚本：1.5s 后停掉 JS 循环 + 暂停全部 CSS 动画，保证 headless 截图能自然退出
    freeze = (
        "<script>setTimeout(function(){"
        "try{if(window.__iv)clearInterval(window.__iv);}catch(e){}"
        "var a=document.querySelectorAll('*');for(var i=0;i<a.length;i++){a[i].style.animationPlayState='paused';}"
        "},1500);</script>"
    )
    return f"{HEAD}{css}</style></head><body>{body}{js_block}{freeze}</body></html>"

count = 0
for name in TEMPLATES:
    fp = OUT / f"txt_{name}.html"
    fp.write_text(build(name), encoding="utf-8")
    count += 1

print(f"generated text-entry effects: {count} -> {OUT}")
