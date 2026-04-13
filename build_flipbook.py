#!/usr/bin/env python3
"""
Twins Are Birds Flipbook Builder (v2 — Mobile Responsive)
==========================================================
Takes a PDF and produces a self-contained HTML flipbook.
Desktop: page-turn flipbook via StPageFlip
Mobile: vertical swipe-through, one slide at a time

Usage:
    python3 build_flipbook.py input.pdf [output.html]
    python3 build_flipbook.py input.pdf --spread 8,9 --spread-image spread.png [output.html]

Options:
    --spread X,Y         Page numbers (1-indexed) that form a double-page spread
    --spread-image PATH  Clean single image to replace the spread pages on mobile

Requirements:
    pip install PyMuPDF --break-system-packages

The StPageFlip library (page-flip.browser.js) must be in the same directory as this script.
"""

import base64
import fitz
import os
import sys
import argparse


def image_to_b64(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp", "gif": "image/gif"}
    mt = mime.get(ext.lstrip("."), "image/png")
    with open(path, "rb") as f:
        return f"data:{mt};base64,{base64.b64encode(f.read()).decode()}"


def build_flipbook(pdf_path, output_path=None, title="Twins Are Birds",
                   spread_pages=None, spread_image_path=None):
    if output_path is None:
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = f"{base}_flipbook.html"

    # Find the StPageFlip library
    lib_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "page-flip.browser.js"),
        os.path.join(os.path.dirname(__file__), "page-flip.browser.js"),
        "/home/claude/package/dist/js/page-flip.browser.js",
    ]
    lib_js = None
    for p in lib_paths:
        if os.path.exists(p):
            with open(p) as f:
                lib_js = f.read()
            break
    if lib_js is None:
        print("ERROR: Cannot find page-flip.browser.js")
        sys.exit(1)

    # Patch canvas background from white to dark
    patched_lib = lib_js.replace(
        'this.ctx.fillStyle="white"',
        'this.ctx.fillStyle="#0a0a0a"'
    )

    # Extract pages as base64 JPEG
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(1.3, 1.3)
    pages_b64 = []
    for i in range(doc.page_count):
        page = doc[i]
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("jpeg")
        b64 = base64.b64encode(img_bytes).decode()
        pages_b64.append(f"data:image/jpeg;base64,{b64}")
        print(f"  Page {i+1}/{doc.page_count}: {len(b64)//1024}KB")

    # Build mobile pages list (replacing spread pages with single image)
    spread_b64 = "null"
    spread_idx_js = "null"
    if spread_pages and spread_image_path and os.path.exists(spread_image_path):
        spread_b64 = f'"{image_to_b64(spread_image_path)}"'
        # Convert to 0-indexed
        spread_idx_js = str([p - 1 for p in spread_pages])
        print(f"  Spread image: {os.path.basename(spread_image_path)} replaces pages {spread_pages}")

    pages_js = "[\n" + ",\n".join(f'"{p}"' for p in pages_b64) + "\n]"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #0a0a0a;
    color: #fff;
    font-family: 'Josefin Sans', sans-serif;
    overflow: hidden;
    user-select: none;
    -webkit-user-select: none;
    height: 100vh;
    height: 100dvh;
  }}

  /* ===== DESKTOP FLIPBOOK ===== */
  .desktop-mode {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 100vh;
  }}

  #book {{
    margin: 0 auto;
    transform: scale(0.7);
    transform-origin: center top;
    margin-top: 20px;
    margin-bottom: -30%;
  }}

  .stf__parent {{
    background: transparent !important;
  }}
  .stf__parent canvas {{
    background: #0a0a0a !important;
  }}

  .nav-btn {{
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.45);
    padding: 12px 16px;
    font-family: 'Josefin Sans', sans-serif;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 2px;
    z-index: 200;
  }}
  .nav-btn:hover {{
    border-color: rgba(255,255,255,0.3);
    color: rgba(255,255,255,0.75);
  }}
  #prevBtn {{ left: 20px; }}
  #nextBtn {{ right: 20px; }}

  .page-indicator {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    font-weight: 300;
    font-size: 12px;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.25);
    z-index: 200;
  }}

  .hint {{
    position: fixed;
    bottom: 6px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 10px;
    color: rgba(255,255,255,0.12);
    letter-spacing: 0.1em;
    white-space: nowrap;
  }}

  /* ===== MOBILE SWIPE MODE ===== */
  .mobile-mode {{
    display: none;
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    position: relative;
    overflow: hidden;
    background: #0a0a0a;
  }}

  .mobile-track {{
    display: flex;
    height: calc(100% - 60px);
    transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    will-change: transform;
  }}

  .mobile-slide {{
    flex: 0 0 100vw;
    width: 100vw;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px;
    background: #0a0a0a;
  }}

  .mobile-slide img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transform: scale(1.2);
    transform-origin: center center;
  }}

  /* Spread image gets special treatment */
  .mobile-slide.spread-slide img {{
    max-width: 100%;
    max-height: 90vh;
    object-fit: contain;
  }}

  .mobile-nav {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 32px;
    background: #0a0a0a;
    z-index: 200;
  }}

  .mobile-nav-btn {{
    background: none;
    border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.4);
    padding: 8px 18px;
    font-family: 'Josefin Sans', sans-serif;
    font-size: 14px;
    cursor: pointer;
    border-radius: 2px;
    transition: all 0.3s ease;
    -webkit-tap-highlight-color: transparent;
  }}

  .mobile-nav-btn:active {{
    border-color: rgba(255,255,255,0.3);
    color: rgba(255,255,255,0.7);
  }}

  .mobile-indicator {{
    font-weight: 300;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.25);
  }}

  /* ===== RESPONSIVE SWITCH ===== */
  @media (max-width: 768px) {{
    .desktop-mode {{ display: none !important; }}
    .mobile-mode {{ display: block !important; }}
  }}

  @media (min-width: 769px) {{
    .desktop-mode {{ display: flex !important; }}
    .mobile-mode {{ display: none !important; }}
  }}

  /* ===== HAMBURGER MENU ===== */
  .hamburger-btn {{
    position: fixed;
    top: 18px;
    right: 20px;
    z-index: 1000;
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    display: flex;
    flex-direction: column;
    gap: 5px;
    -webkit-tap-highlight-color: transparent;
  }}
  .hamburger-btn span {{
    display: block;
    width: 22px;
    height: 1px;
    background: rgba(255,255,255,0.45);
    transition: all 0.3s ease;
    transform-origin: center;
  }}
  .hamburger-btn:hover span {{ background: rgba(255,255,255,0.75); }}
  .hamburger-btn.open span:nth-child(1) {{ transform: translateY(6px) rotate(45deg); }}
  .hamburger-btn.open span:nth-child(2) {{ opacity: 0; transform: scaleX(0); }}
  .hamburger-btn.open span:nth-child(3) {{ transform: translateY(-6px) rotate(-45deg); }}

  .nav-overlay {{
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(10,10,10,0.0);
    z-index: 998;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }}
  .nav-overlay.open {{ opacity: 1; pointer-events: all; }}

  .nav-drawer {{
    position: fixed;
    top: 0; right: 0;
    width: 220px; height: 100%;
    background: #0a0a0a;
    border-left: 1px solid rgba(255,255,255,0.07);
    z-index: 999;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 40px 36px;
    transform: translateX(100%);
    transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }}
  .nav-drawer.open {{ transform: translateX(0); }}
  .nav-drawer a {{
    display: block;
    font-family: 'Josefin Sans', sans-serif;
    font-weight: 300;
    font-size: 13px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    text-decoration: none;
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    transition: color 0.2s ease;
  }}
  .nav-drawer a:first-child {{ border-top: 1px solid rgba(255,255,255,0.06); }}
  .nav-drawer a:hover {{ color: rgba(255,255,255,0.8); }}
  .nav-drawer .nav-label {{
    font-size: 9px;
    letter-spacing: 0.25em;
    color: rgba(255,255,255,0.15);
    text-transform: uppercase;
    margin-bottom: 24px;
  }}
</style>
</head>
<body>

<!-- HAMBURGER MENU -->
<button class="hamburger-btn" id="hamburgerBtn" aria-label="Menu">
  <span></span>
  <span></span>
  <span></span>
</button>
<div class="nav-overlay" id="navOverlay"></div>
<nav class="nav-drawer" id="navDrawer">
  <p class="nav-label">Twins Are Birds</p>
  <a href="index.html">Home</a>
  <a href="menu.html">Menu</a>
  <a href="about.html">About</a>
</nav>

<!-- DESKTOP -->
<div class="desktop-mode">
  <div id="book"></div>
  <button class="nav-btn" id="prevBtn">&#8592;</button>
  <button class="nav-btn" id="nextBtn">&#8594;</button>
  <span class="page-indicator" id="pageIndicator"></span>
  <div class="hint">drag corners to turn &#183; click edges &#183; swipe</div>
</div>

<!-- MOBILE -->
<div class="mobile-mode" id="mobileMode">
  <div class="mobile-track" id="mobileTrack"></div>
  <div class="mobile-nav">
    <button class="mobile-nav-btn" id="mobilePrev">&#8592;</button>
    <span class="mobile-indicator" id="mobileIndicator"></span>
    <button class="mobile-nav-btn" id="mobileNext">&#8594;</button>
  </div>
</div>

<script>{patched_lib}</script>
<script>
const ALL_PAGES = {pages_js};
const SPREAD_IMAGE = {spread_b64};
const SPREAD_INDICES = {spread_idx_js};

// ===== DESKTOP FLIPBOOK =====
function initDesktop() {{
  const pageFlip = new St.PageFlip(document.getElementById("book"), {{
    width: 810,
    height: 1012,
    size: "stretch",
    minWidth: 300,
    maxWidth: 810,
    minHeight: 375,
    maxHeight: 1012,
    showCover: true,
    maxShadowOpacity: 0.6,
    mobileScrollSupport: true,
    flippingTime: 800,
    useMouseEvents: true,
    swipeDistance: 30,
    showPageCorners: true,
    drawShadow: true,
    autoSize: true
  }});
  pageFlip.loadFromImages(ALL_PAGES);

  const indicator = document.getElementById("pageIndicator");
  const total = ALL_PAGES.length;
  function updateIndicator() {{
    const current = pageFlip.getCurrentPageIndex() + 1;
    indicator.textContent = current + " / " + total;
  }}
  pageFlip.on("flip", () => updateIndicator());
  pageFlip.on("init", () => updateIndicator());

  document.getElementById("prevBtn").addEventListener("click", () => pageFlip.flipPrev());
  document.getElementById("nextBtn").addEventListener("click", () => pageFlip.flipNext());

  document.addEventListener("keydown", (e) => {{
    if (e.key === "ArrowRight" || e.key === " ") {{ e.preventDefault(); pageFlip.flipNext(); }}
    if (e.key === "ArrowLeft") {{ e.preventDefault(); pageFlip.flipPrev(); }}
  }});
  updateIndicator();
}}

// ===== MOBILE SWIPE =====
function initMobile() {{
  const track = document.getElementById("mobileTrack");
  const indicator = document.getElementById("mobileIndicator");

  // Build mobile pages: replace spread pages with single image
  let mobilePages = [];
  let spreadSet = new Set(SPREAD_INDICES || []);
  let spreadInserted = false;

  for (let i = 0; i < ALL_PAGES.length; i++) {{
    if (spreadSet.has(i)) {{
      if (!spreadInserted && SPREAD_IMAGE) {{
        mobilePages.push({{ src: SPREAD_IMAGE, isSpread: true }});
        spreadInserted = true;
      }}
    }} else {{
      mobilePages.push({{ src: ALL_PAGES[i], isSpread: false }});
    }}
  }}

  // Create slides
  mobilePages.forEach((page, i) => {{
    const slide = document.createElement("div");
    slide.className = "mobile-slide" + (page.isSpread ? " spread-slide" : "");
    const img = document.createElement("img");
    img.src = page.src;
    img.alt = "Page " + (i + 1);
    img.draggable = false;
    slide.appendChild(img);
    track.appendChild(slide);
  }});

  const total = mobilePages.length;
  let current = 0;
  let startX = 0;
  let startY = 0;
  let deltaX = 0;
  let isDragging = false;
  let isHorizontal = null;

  function goTo(idx) {{
    current = Math.max(0, Math.min(total - 1, idx));
    track.style.transform = `translateX(${{-current * 100}}vw)`;
    indicator.textContent = (current + 1) + " / " + total;
  }}

  // Nav buttons
  document.getElementById("mobilePrev").addEventListener("click", () => goTo(current - 1));
  document.getElementById("mobileNext").addEventListener("click", () => goTo(current + 1));

  // Touch events
  track.addEventListener("touchstart", (e) => {{
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    deltaX = 0;
    isDragging = true;
    isHorizontal = null;
    track.style.transition = "none";
  }}, {{ passive: true }});

  track.addEventListener("touchmove", (e) => {{
    if (!isDragging) return;
    const dx = e.touches[0].clientX - startX;
    const dy = e.touches[0].clientY - startY;

    // Determine direction on first significant move
    if (isHorizontal === null && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) {{
      isHorizontal = Math.abs(dx) > Math.abs(dy);
    }}

    if (isHorizontal) {{
      e.preventDefault();
      deltaX = dx;
      const offset = -current * window.innerWidth + deltaX;
      track.style.transform = `translateX(${{offset}}px)`;
    }}
  }}, {{ passive: false }});

  track.addEventListener("touchend", () => {{
    isDragging = false;
    track.style.transition = "transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)";

    if (isHorizontal) {{
      const threshold = window.innerWidth * 0.2;
      if (deltaX < -threshold) goTo(current + 1);
      else if (deltaX > threshold) goTo(current - 1);
      else goTo(current);
    }}
    deltaX = 0;
    isHorizontal = null;
  }});

  goTo(0);
}}

// ===== INIT =====
if (window.innerWidth <= 768) {{
  initMobile();
}} else {{
  initDesktop();
}}

// Handle resize (e.g. rotate device)
let lastMode = window.innerWidth <= 768 ? "mobile" : "desktop";
window.addEventListener("resize", () => {{
  const newMode = window.innerWidth <= 768 ? "mobile" : "desktop";
  if (newMode !== lastMode) {{
    lastMode = newMode;
    location.reload();
  }}
}});

// ===== HAMBURGER MENU =====
const hamburgerBtn = document.getElementById('hamburgerBtn');
const navDrawer = document.getElementById('navDrawer');
const navOverlay = document.getElementById('navOverlay');

function openMenu() {{
  hamburgerBtn.classList.add('open');
  navDrawer.classList.add('open');
  navOverlay.classList.add('open');
}}

function closeMenu() {{
  hamburgerBtn.classList.remove('open');
  navDrawer.classList.remove('open');
  navOverlay.classList.remove('open');
}}

hamburgerBtn.addEventListener('click', (e) => {{
  e.stopPropagation();
  navDrawer.classList.contains('open') ? closeMenu() : openMenu();
}});

navOverlay.addEventListener('click', closeMenu);

navDrawer.querySelectorAll('a').forEach(link => {{
  link.addEventListener('click', closeMenu);
}});

document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') closeMenu();
}});
</script>
</body>
</html>'''

    with open(output_path, "w") as f:
        f.write(html)

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\nDone! {output_path} ({size_mb:.1f}MB, {doc.page_count} pages)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a responsive flipbook from a PDF")
    parser.add_argument("pdf", help="Input PDF file")
    parser.add_argument("output", nargs="?", default=None, help="Output HTML file")
    parser.add_argument("--spread", help="Comma-separated page numbers forming a spread (e.g. 8,9)")
    parser.add_argument("--spread-image", help="Clean image to replace spread pages on mobile")
    args = parser.parse_args()

    spread_pages = None
    if args.spread:
        spread_pages = [int(x.strip()) for x in args.spread.split(",")]

    build_flipbook(args.pdf, args.output, spread_pages=spread_pages,
                   spread_image_path=args.spread_image)
