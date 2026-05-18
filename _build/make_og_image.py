#!/usr/bin/env python3
"""Generate the Flikt.AI demo OG image (1200x630) in the portal report-view style.

Light body, dark navy navbar header, amber accents, sample conflict cards.
Run:
    python3 _build/make_og_image.py
Writes: og_final_demo.png in the demo folder.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent.parent / "og_final_demo.png"

# Canvas
W, H = 1200, 630

# Palette (mirrors page_template.py)
NAVY = (10, 25, 41)         # #0a1929
AMBER = (232, 160, 32)      # #E8A020
TEXT = (15, 23, 42)         # #0F172A
TEXT_MUTED = (100, 116, 139) # #64748B
BG = (245, 247, 250)        # #F5F7FA
CARD = (255, 255, 255)
BORDER = (226, 232, 240)    # #E2E8F0
CRITICAL = (220, 38, 38)
CRITICAL_TINT = (254, 242, 242)
CRITICAL_BORDER = (254, 202, 202)
HIGH = (234, 88, 12)
HIGH_TINT = (255, 247, 237)
HIGH_BORDER = (254, 215, 170)
MEDIUM = (217, 119, 6)
MEDIUM_TINT = (255, 251, 235)


def load_font(size: int, weight: str = "regular"):
    """Try Inter -> SF -> Helvetica -> default."""
    candidates = []
    if weight == "bold":
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """Pillow Draw.rounded_rectangle compatibility wrapper."""
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_flikt_icon(draw, cx, cy, size=60):
    """Two overlapping squares + center dot, amber. Centered on (cx, cy)."""
    s = size
    half = s // 2
    sq_size = int(s * 0.62)
    sw = max(3, int(s * 0.08))  # stroke width
    # First square (offset up-left)
    x1 = cx - half + int(s * 0.06)
    y1 = cy - half + int(s * 0.06)
    draw.rectangle([x1, y1, x1 + sq_size, y1 + sq_size], outline=AMBER, width=sw)
    # Second square (offset down-right, overlapping)
    x2 = cx - half + int(s * 0.32)
    y2 = cy - half + int(s * 0.32)
    draw.rectangle([x2, y2, x2 + sq_size, y2 + sq_size], outline=AMBER, width=sw)
    # Center dot
    dr = max(4, int(s * 0.10))
    draw.ellipse([cx - dr, cy - dr, cx + dr, cy + dr], fill=AMBER)


def draw_severity_pill(draw, x, y, label, count, fill, border, fg, font_count, font_label):
    """Pill with severity color tint + count + label."""
    pad_x = 14
    pad_y = 8
    text = f"{count} {label}"
    bbox = draw.textbbox((0, 0), text, font=font_count)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    w = text_w + pad_x * 2
    h = text_h + pad_y * 2
    rounded_rect(draw, (x, y, x + w, y + h), radius=h // 2, fill=fill, outline=border, width=1)
    draw.text((x + pad_x, y + pad_y - 2), text, font=font_count, fill=fg)
    return w


def draw_conflict_card(draw, x, y, w, h, sev_color, sev_tint, sev_label, title, snippet, fonts):
    """Mini conflict card — severity-tinted, severity badge, title, snippet."""
    # Card background gradient effect — simplified to flat tint with white bottom
    # Pillow doesn't do gradients trivially; draw a tinted top + white bottom.
    rounded_rect(draw, (x, y, x + w, y + h), radius=12, fill=CARD, outline=BORDER, width=1)
    # Tinted top accent
    rounded_rect(draw, (x, y, x + w, y + 38), radius=12, fill=sev_tint)
    # Re-draw bottom corners to keep them white (overlay a rect that re-colors)
    draw.rectangle((x, y + 18, x + w, y + 38), fill=sev_tint)
    draw.rectangle((x, y + 38, x + w, y + h - 12), fill=CARD)
    # Re-stroke the rounded border
    rounded_rect(draw, (x, y, x + w, y + h), radius=12, fill=None, outline=BORDER, width=1)
    # Left-border accent
    draw.rectangle((x, y + 12, x + 4, y + h - 12), fill=sev_color)
    # Severity badge
    badge_w, badge_h = 60, 22
    bx, by = x + 14, y + 14
    rounded_rect(draw, (bx, by, bx + badge_w, by + badge_h), radius=4, fill=sev_color)
    # Center sev label in badge
    bbox = draw.textbbox((0, 0), sev_label, font=fonts["sev_badge"])
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((bx + (badge_w - tw) // 2, by + (badge_h - th) // 2 - 1),
              sev_label, font=fonts["sev_badge"], fill=CARD)
    # Title
    draw.text((x + 84, y + 14), title, font=fonts["card_title"], fill=TEXT)
    # Snippet (2 lines)
    snippet_y = y + 44
    line1, line2 = wrap_two_lines(snippet, fonts["card_body"], w - 32, draw)
    draw.text((x + 16, snippet_y), line1, font=fonts["card_body"], fill=TEXT_MUTED)
    if line2:
        draw.text((x + 16, snippet_y + 22), line2, font=fonts["card_body"], fill=TEXT_MUTED)


def wrap_two_lines(text, font, max_w, draw):
    """Wrap text into at most 2 lines, ellipsizing the second."""
    words = text.split()
    line1 = ""
    i = 0
    while i < len(words):
        candidate = (line1 + " " + words[i]).strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] > max_w:
            break
        line1 = candidate
        i += 1
    if i == len(words):
        return line1, ""
    line2 = ""
    while i < len(words):
        candidate = (line2 + " " + words[i]).strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] > max_w - 20:
            line2 = (line2 + "…").strip()
            break
        line2 = candidate
        i += 1
    return line1, line2


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    fonts = {
        "wordmark": load_font(34, "bold"),
        "badge": load_font(14, "bold"),
        "h1": load_font(60, "bold"),
        "tagline": load_font(22, "regular"),
        "url": load_font(18, "bold"),
        "pill": load_font(15, "bold"),
        "card_title": load_font(18, "bold"),
        "card_body": load_font(15, "regular"),
        "sev_badge": load_font(11, "bold"),
        "footer": load_font(14, "regular"),
    }

    # --- Navbar (dark navy, top 80px) ---
    NAV_H = 80
    draw.rectangle((0, 0, W, NAV_H), fill=NAVY)
    # Icon (40x40 inside nav)
    draw_flikt_icon(draw, 60, NAV_H // 2, size=40)
    # Wordmark
    draw.text((88, NAV_H // 2 - 20), "Flikt", font=fonts["wordmark"], fill=CARD)
    bbox = draw.textbbox((88, NAV_H // 2 - 20), "Flikt", font=fonts["wordmark"])
    flikt_w = bbox[2] - bbox[0]
    draw.text((88 + flikt_w, NAV_H // 2 - 20), ".AI", font=fonts["wordmark"], fill=AMBER)
    # "Real AI analysis" badge on right
    badge_text = "REAL AI ANALYSIS"
    bbox = draw.textbbox((0, 0), badge_text, font=fonts["badge"])
    bw = bbox[2] - bbox[0] + 28
    bh = bbox[3] - bbox[1] + 14
    bx = W - bw - 60
    by = (NAV_H - bh) // 2
    # Subtle amber tint over the navy navbar — mix amber 12% over navy
    badge_fill = (
        int(NAVY[0] * 0.88 + AMBER[0] * 0.12),
        int(NAVY[1] * 0.88 + AMBER[1] * 0.12),
        int(NAVY[2] * 0.88 + AMBER[2] * 0.12),
    )
    rounded_rect(draw, (bx, by, bx + bw, by + bh), radius=bh // 2,
                 fill=badge_fill, outline=AMBER, width=1)
    draw.text((bx + 14, by + 6), badge_text, font=fonts["badge"], fill=AMBER)

    # --- Body content area ---
    body_top = NAV_H + 50

    # Headline
    headline = "AI-Powered Plan"
    headline2 = "Coordination"
    draw.text((60, body_top), headline, font=fonts["h1"], fill=TEXT)
    draw.text((60, body_top + 64), headline2, font=fonts["h1"], fill=NAVY)

    # Tagline
    tagline = "Detect coordination conflicts across architectural, MEP,"
    tagline2 = "structural, and civil disciplines. Real pipeline data."
    draw.text((60, body_top + 150), tagline, font=fonts["tagline"], fill=TEXT_MUTED)
    draw.text((60, body_top + 180), tagline2, font=fonts["tagline"], fill=TEXT_MUTED)

    # Severity pills row
    pill_y = body_top + 232
    pill_x = 60
    pill_x += draw_severity_pill(draw, pill_x, pill_y, "Critical", 11,
                                 CRITICAL_TINT, CRITICAL_BORDER, CRITICAL,
                                 fonts["pill"], fonts["pill"]) + 8
    pill_x += draw_severity_pill(draw, pill_x, pill_y, "High", 80,
                                 HIGH_TINT, HIGH_BORDER, HIGH,
                                 fonts["pill"], fonts["pill"]) + 8
    pill_x += draw_severity_pill(draw, pill_x, pill_y, "Medium", 59,
                                 MEDIUM_TINT, (253, 230, 138), MEDIUM,
                                 fonts["pill"], fonts["pill"]) + 8

    # URL/CTA
    cta_text = "demo.flikt.ai"
    draw.text((60, body_top + 310), cta_text, font=fonts["url"], fill=AMBER)

    # --- Right side: 3 stacked conflict cards (preview) ---
    card_x = 700
    card_w = 440
    card_h = 100
    card_gap = 14
    card_y = body_top - 10
    draw_conflict_card(draw, card_x, card_y, card_w, card_h,
                       CRITICAL, CRITICAL_TINT, "CRITICAL",
                       "Plumbing clashes structural beam",
                       "Fixture at Grid C-4 conflicts with structural beam depth. Field rework required.",
                       fonts)
    draw_conflict_card(draw, card_x, card_y + (card_h + card_gap), card_w, card_h,
                       HIGH, HIGH_TINT, "HIGH",
                       "Electrical panel access blocked",
                       "Mechanical duct within 18\" of panel face. NEC 110.26 clearance violation.",
                       fonts)
    draw_conflict_card(draw, card_x, card_y + 2 * (card_h + card_gap), card_w, card_h,
                       MEDIUM, MEDIUM_TINT, "MEDIUM",
                       "Sprinkler head spacing exceeds",
                       "Three heads in west corridor exceed 12' max spacing per NFPA 13. Add one head.",
                       fonts)

    # --- Footer band ---
    foot_y = H - 36
    draw.text((60, foot_y), "Plan conflict detection for multifamily, commercial & residential construction",
              font=fonts["footer"], fill=TEXT_MUTED)

    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
