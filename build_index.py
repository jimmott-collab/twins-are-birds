#!/usr/bin/env python3
import os

with open('/home/claude/header_b64.txt') as f: header_b64 = f.read()
with open('/home/claude/cover1_b64.txt') as f: cover1_b64 = f.read()
with open('/home/claude/cover2_b64.txt') as f: cover2_b64 = f.read()
with open('/home/claude/cover3_b64.txt') as f: cover3_b64 = f.read()
with open('/home/claude/flower_b64.txt') as f: flower_b64 = f.read()

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Twins Are Birds — Anthropology for Strategists</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@200;300;400;600&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{
    background: #000;
  }}
  body {{
    background: #000;
    color: #e8e0d4;
    font-family: 'Josefin Sans', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }}
  img {{
    background: #000;
  }}

  .hero {{
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 0;
    background: #000;
  }}
  .hero-stack {{
    position: relative;
    width: 100%;
  }}
  .masthead-img {{
    width: 100%;
    height: auto;
    display: block;
    background: #000;
  }}
  .flower-img {{
    position: absolute;
    width: clamp(300px, 50vw, 550px);
    left: 50%;
    top: 25%;
    transform: translateX(-50%);
    z-index: 2;
  }}

  .carousel-section {{
    padding: 20px 0 40px;
    position: relative;
    background: #000;
  }}
  .carousel-viewport {{
    overflow: hidden;
    width: 100%;
    background: #000;
  }}
  .carousel-track {{
    display: flex;
    background: #000;
  }}
  .carousel-item {{
    flex: 0 0 100vw;
    width: 100vw;
    display: flex;
    justify-content: center;
    background: #000;
  }}
  .carousel-item a {{
    display: block;
    text-decoration: none;
    color: #e8e0d4;
    width: clamp(220px, 35vw, 340px);
    transition: opacity 0.3s ease;
    opacity: 0.85;
  }}
  .carousel-item a:hover {{
    opacity: 1;
  }}
  .carousel-item img {{
    width: 100%;
    height: auto;
    display: block;
  }}
  .carousel-label {{
    padding: 12px 0 4px;
    text-align: center;
  }}
  .carousel-number {{
    font-size: 10px;
    font-weight: 300;
    letter-spacing: 0.2em;
    color: rgba(232,224,212,0.25);
    display: block;
    margin-bottom: 3px;
  }}
  .carousel-title {{
    font-size: clamp(12px, 1.5vw, 15px);
    font-weight: 300;
    letter-spacing: 0.06em;
  }}
  .carousel-thinker {{
    font-size: 10px;
    font-weight: 300;
    letter-spacing: 0.15em;
    color: rgba(232,224,212,0.25);
    text-transform: uppercase;
    margin-top: 2px;
  }}
  .carousel-nav {{
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-bottom: 20px;
  }}
  .carousel-btn {{
    background: none;
    border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.4);
    padding: 8px 20px;
    font-family: 'Josefin Sans', sans-serif;
    font-size: 16px;
    cursor: pointer;
    border-radius: 2px;
    transition: all 0.3s ease;
    -webkit-tap-highlight-color: transparent;
  }}
  .carousel-btn:hover {{
    border-color: rgba(255,255,255,0.3);
    color: rgba(255,255,255,0.7);
  }}

  .footer {{
    text-align: center;
    padding: 50px 40px;
    background: #000;
  }}
  .footer-text {{
    font-size: 11px;
    font-weight: 300;
    letter-spacing: 0.12em;
    color: rgba(232,224,212,0.18);
    line-height: 2.2;
  }}

  @media (max-width: 600px) {{
    .hero-stack {{ width: 100%; }}
    .flower-img {{ width: 75vw; }}
    .carousel-item a {{ width: 65vw; }}
  }}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-stack">
    <img class="masthead-img" src="{header_b64}" alt="Twins Are Birds - Anthropology for Strategists">
    <img class="flower-img" src="{flower_b64}" alt="">
  </div>
</div>

<div class="carousel-section">
  <div class="carousel-nav">
    <button class="carousel-btn" id="carouselPrev">&#8592;</button>
    <button class="carousel-btn" id="carouselNext">&#8594;</button>
  </div>
  <div class="carousel-viewport">
    <div class="carousel-track" id="carouselTrack"></div>
  </div>
</div>

<footer class="footer">
  <div class="footer-text">
    Jim Mott &mdash; Commercial Anthropologist &amp; Cultural Strategist
  </div>
</footer>

<script>
var ISSUES = [
  {{ href: "issues/01-merleau-ponty.html", img: "{cover1_b64}", num: "#1", title: "Why is Reaching Thinking?", thinker: "Merleau-Ponty" }},
  {{ href: "issues/02-latour.html", img: "{cover2_b64}", num: "#2", title: "Why Did Aramis Die?", thinker: "Latour" }},
  {{ href: "issues/03-evans-pritchard.html", img: "{cover3_b64}", num: "#3", title: "Why Are Twins Birds?", thinker: "Evans-Pritchard" }}
];

var track = document.getElementById("carouselTrack");
var copies = 10;

for (var c = 0; c < copies; c++) {{
  for (var i = 0; i < ISSUES.length; i++) {{
    var issue = ISSUES[i];
    var div = document.createElement("div");
    div.className = "carousel-item";
    var link = document.createElement("a");
    link.href = issue.href;
    var img = document.createElement("img");
    img.src = issue.img;
    img.alt = issue.title;
    link.appendChild(img);
    var label = document.createElement("div");
    label.className = "carousel-label";
    label.innerHTML = '<span class="carousel-number">' + issue.num + '</span>' +
      '<div class="carousel-thinker">' + issue.thinker + '</div>';
    link.appendChild(label);
    div.appendChild(link);
    track.appendChild(div);
  }}
}}

var currentIndex = Math.floor(copies / 2) * ISSUES.length;
var isAnimating = false;

function getItemWidth() {{
  return window.innerWidth;
}}

function jumpTo(idx, animate) {{
  var offset = idx * getItemWidth();
  if (animate) {{
    track.style.transition = "transform 0.4s ease";
  }} else {{
    track.style.transition = "none";
  }}
  track.style.transform = "translateX(" + (-offset) + "px)";
}}

function wrapIndex() {{
  var setLen = ISSUES.length;
  var totalItems = copies * setLen;
  var midStart = Math.floor(copies / 2) * setLen;
  if (currentIndex < setLen) {{
    currentIndex += setLen;
    jumpTo(currentIndex, false);
  }} else if (currentIndex >= (copies - 1) * setLen) {{
    currentIndex -= setLen;
    jumpTo(currentIndex, false);
  }}
}}

function stepNext() {{
  if (isAnimating) return;
  isAnimating = true;
  currentIndex++;
  jumpTo(currentIndex, true);
  setTimeout(function() {{
    wrapIndex();
    isAnimating = false;
  }}, 450);
}}

function stepPrev() {{
  if (isAnimating) return;
  isAnimating = true;
  currentIndex--;
  jumpTo(currentIndex, true);
  setTimeout(function() {{
    wrapIndex();
    isAnimating = false;
  }}, 450);
}}

// Initial position
jumpTo(currentIndex, false);

document.getElementById("carouselPrev").addEventListener("click", stepPrev);
document.getElementById("carouselNext").addEventListener("click", stepNext);
</script>

</body>
</html>'''

with open('/mnt/user-data/outputs/index.html', 'w') as f:
    f.write(html)

size = os.path.getsize('/mnt/user-data/outputs/index.html') / 1024 / 1024
print(f'Done: {size:.1f}MB')
