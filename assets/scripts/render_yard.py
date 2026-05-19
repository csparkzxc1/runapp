"""
마당 시즈널 자동 변화 PoC 렌더러.

64x64 픽셀 캔버스에 tent 등급 마당을 4계절 × 4시간대로 그림.
PIL만 사용 — 실제 게임에선 픽셀 아티스트가 그릴 부분의 자동 시안.

Run: python3 assets/scripts/render_yard.py
Out: assets/yard/{season}_{daypart}.png  (각 512x512, nearest-neighbor 8배 확대)
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 64, 64
SCALE = 8

# ─────────────────────────────────────────────────────────────
# Palette
# ─────────────────────────────────────────────────────────────
SKY = {
    ("spring", "morning"):   "#FFD9C2",
    ("spring", "afternoon"): "#9FD8F0",
    ("spring", "evening"):   "#F7B27A",
    ("spring", "night"):     "#1A1F3D",
    ("summer", "morning"):   "#FFE9A3",
    ("summer", "afternoon"): "#5EC0EA",
    ("summer", "evening"):   "#E07A4F",
    ("summer", "night"):     "#0F1838",
    ("autumn", "morning"):   "#F5C690",
    ("autumn", "afternoon"): "#BCDDEB",
    ("autumn", "evening"):   "#C95A2D",
    ("autumn", "night"):     "#1C1832",
    ("winter", "morning"):   "#E5DCEA",
    ("winter", "afternoon"): "#D3E3EE",
    ("winter", "evening"):   "#A89AB8",
    ("winter", "night"):     "#171B30",
}

GROUND = {
    "spring": "#8FCE60",
    "summer": "#5DB73C",
    "autumn": "#C8923A",
    "winter": "#EDEEF0",
}

TREE_LEAVES = {
    "spring": "#F4A8C0",   # 벚꽃
    "summer": "#3F9E3D",
    "autumn": "#D86A1F",
    "winter": None,         # 가지만
}

TREE_TRUNK = {
    "spring": "#7A4F30",
    "summer": "#6B4525",
    "autumn": "#5C3A20",
    "winter": "#473023",
}

TENT_BODY  = "#C04545"
TENT_DARK  = "#8A2E2E"
TENT_DOOR  = "#3A1818"

SUN        = "#FFE76A"
SUN_GLOW   = "#FFB347"
MOON       = "#F2F0D8"
STAR       = "#FFFFFF"

PETAL      = "#FFB6CB"
SNOWFLAKE  = "#FFFFFF"

# ─────────────────────────────────────────────────────────────
# Primitives
# ─────────────────────────────────────────────────────────────
def fill_band(draw, color, y0, y1):
    draw.rectangle([0, y0, W - 1, y1], fill=color)


def pixel(draw, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        draw.point((x, y), fill=color)


def rect(draw, x0, y0, x1, y1, color):
    draw.rectangle([x0, y0, x1, y1], fill=color)


def draw_sun(draw, cx, cy):
    # 4x4 core + cross glow
    rect(draw, cx - 1, cy - 1, cx + 2, cy + 2, SUN)
    pixel(draw, cx, cy - 2, SUN_GLOW)
    pixel(draw, cx, cy + 3, SUN_GLOW)
    pixel(draw, cx - 2, cy, SUN_GLOW)
    pixel(draw, cx + 3, cy, SUN_GLOW)
    pixel(draw, cx + 1, cy - 2, SUN_GLOW)
    pixel(draw, cx + 1, cy + 3, SUN_GLOW)


def draw_moon(draw, cx, cy):
    rect(draw, cx - 1, cy - 1, cx + 1, cy + 1, MOON)
    pixel(draw, cx - 1, cy - 1, "#C8C5B0")  # crater shading


def draw_stars(draw, seed_seed):
    # 결정론적 별 배치
    coords = [(8, 4), (18, 9), (28, 3), (38, 11), (48, 5), (56, 13), (12, 16)]
    for x, y in coords:
        pixel(draw, x, y, STAR)


def draw_tree(draw, season, base_x=44):
    # 트렁크
    trunk = TREE_TRUNK[season]
    rect(draw, base_x, 38, base_x + 2, 47, trunk)
    # 잎
    leaves = TREE_LEAVES[season]
    if leaves:
        # 다이아몬드형 캐노피
        rect(draw, base_x - 5, 28, base_x + 7, 32, leaves)
        rect(draw, base_x - 4, 25, base_x + 6, 28, leaves)
        rect(draw, base_x - 3, 23, base_x + 5, 25, leaves)
        rect(draw, base_x - 6, 32, base_x + 8, 36, leaves)
        rect(draw, base_x - 4, 36, base_x + 6, 38, leaves)
        # 약간의 음영
        pixel(draw, base_x + 7, 31, "#000000")
        pixel(draw, base_x - 5, 31, "#000000")
    else:
        # 겨울: 가지만
        pixel(draw, base_x - 2, 36, trunk)
        pixel(draw, base_x - 3, 34, trunk)
        pixel(draw, base_x + 3, 36, trunk)
        pixel(draw, base_x + 4, 34, trunk)
        pixel(draw, base_x + 1, 32, trunk)


def draw_tent(draw, base_x=18, base_y=47):
    # 삼각 텐트 (좌우 대칭)
    for dy in range(0, 10):
        y = base_y - dy
        half = 9 - dy
        if half < 0:
            break
        rect(draw, base_x - half, y, base_x + half, y, TENT_BODY)
        # 어두운 면 (우측 절반) — half > 0일 때만
        if half >= 1:
            rect(draw, base_x + 1, y, base_x + half, y, TENT_DARK)
    # 입구
    rect(draw, base_x - 1, base_y - 3, base_x + 1, base_y, TENT_DOOR)
    # 꼭짓점 깃대
    pixel(draw, base_x, base_y - 11, "#666666")
    pixel(draw, base_x, base_y - 12, "#888888")


def draw_petals(draw):
    coords = [(10, 18), (22, 24), (35, 14), (52, 20), (8, 30), (45, 32)]
    for x, y in coords:
        pixel(draw, x, y, PETAL)


def draw_snow(draw):
    coords = [
        (5, 10), (12, 18), (20, 6), (28, 14), (35, 8),
        (42, 18), (50, 10), (58, 16), (15, 28), (40, 26),
    ]
    for x, y in coords:
        pixel(draw, x, y, SNOWFLAKE)


# ─────────────────────────────────────────────────────────────
# Composer
# ─────────────────────────────────────────────────────────────
def render(season: str, daypart: str) -> Image.Image:
    img = Image.new("RGB", (W, H), SKY[(season, daypart)])
    d = ImageDraw.Draw(img)

    # Sky band + horizon
    fill_band(d, SKY[(season, daypart)], 0, 47)

    # Celestial body
    if daypart == "night":
        draw_stars(d, hash(season))
        draw_moon(d, 50, 8)
    elif daypart == "morning":
        draw_sun(d, 10, 10)
    elif daypart == "afternoon":
        draw_sun(d, 32, 6)
    elif daypart == "evening":
        draw_sun(d, 54, 14)

    # Ground
    fill_band(d, GROUND[season], 48, 63)

    # Atmospheric overlay
    if season == "spring":
        draw_petals(d)
    elif season == "winter":
        draw_snow(d)

    # Tree + tent
    draw_tree(d, season)
    draw_tent(d)

    return img


def upscale(img: Image.Image, scale: int) -> Image.Image:
    return img.resize((W * scale, H * scale), Image.NEAREST)


def grid(images, cols: int, label_map: dict) -> Image.Image:
    """그리드 컴포지트 — cols개씩 배치."""
    rows = (len(images) + cols - 1) // cols
    cell_w, cell_h = images[0].size
    pad = 8
    out = Image.new(
        "RGB",
        (cols * cell_w + (cols + 1) * pad, rows * cell_h + (rows + 1) * pad),
        "#222222",
    )
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + pad)
        out.paste(im, (x, y))
    return out


def main():
    out_dir = Path(__file__).resolve().parents[1] / "yard"
    out_dir.mkdir(parents=True, exist_ok=True)

    seasons = ["spring", "summer", "autumn", "winter"]
    dayparts = ["morning", "afternoon", "evening", "night"]

    # 개별 파일
    all_imgs = []
    for s in seasons:
        for d in dayparts:
            img = render(s, d)
            big = upscale(img, SCALE)
            path = out_dir / f"{s}_{d}.png"
            big.save(path)
            all_imgs.append(big)
            print(f"  ✓ {path.name}")

    # 4x4 그리드 시안
    grid_img = grid(all_imgs, cols=4, label_map={})
    grid_path = out_dir / "_grid_4x4.png"
    grid_img.save(grid_path)
    print(f"\n  ✓ {grid_path.name}")


if __name__ == "__main__":
    main()
