"""
마당 시즈널 자동 변화 PoC 렌더러.

64x64 픽셀 캔버스에 6 등급 × 4 계절 × 4 시간대 = 96 마당 시안.
PIL만 사용 — 실제 게임에선 픽셀 아티스트가 그릴 부분의 자동 시안.

Run: python3 assets/scripts/render_yard.py
Out: assets/yard/{tier}/{season}_{daypart}.png + per-tier 4x4 grids
     + assets/yard/_overview_tiers.png
"""

from __future__ import annotations
from pathlib import Path
from typing import Callable
from PIL import Image, ImageDraw

W, H = 64, 64
SCALE = 8
GROUND_Y = 48  # 지평선 (이 아래로 ground 색)

TIERS = ["tent", "cabin", "yard_house", "villa", "apartment", "mansion"]
SEASONS = ["spring", "summer", "autumn", "winter"]
DAYPARTS = ["morning", "afternoon", "evening", "night"]

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
    "spring": "#F4A8C0",
    "summer": "#3F9E3D",
    "autumn": "#D86A1F",
    "winter": None,
}
TREE_TRUNK = {
    "spring": "#7A4F30",
    "summer": "#6B4525",
    "autumn": "#5C3A20",
    "winter": "#473023",
}

SUN, SUN_GLOW = "#FFE76A", "#FFB347"
MOON, STAR    = "#F2F0D8", "#FFFFFF"
PETAL, SNOW   = "#FFB6CB", "#FFFFFF"

# ─────────────────────────────────────────────────────────────
# Primitives
# ─────────────────────────────────────────────────────────────
def pixel(d, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        d.point((x, y), fill=c)


def rect(d, x0, y0, x1, y1, c):
    if x1 < x0 or y1 < y0:
        return
    d.rectangle([x0, y0, x1, y1], fill=c)


def fill_band(d, c, y0, y1):
    d.rectangle([0, y0, W - 1, y1], fill=c)


def draw_sun(d, cx, cy):
    rect(d, cx - 1, cy - 1, cx + 2, cy + 2, SUN)
    for dx, dy in [(0, -2), (1, -2), (0, 3), (1, 3), (-2, 0), (3, 0), (-2, 1), (3, 1)]:
        pixel(d, cx + dx, cy + dy, SUN_GLOW)


def draw_moon(d, cx, cy):
    rect(d, cx - 1, cy - 1, cx + 1, cy + 1, MOON)
    pixel(d, cx - 1, cy - 1, "#C8C5B0")


def draw_stars(d):
    for x, y in [(8, 4), (18, 9), (28, 3), (38, 11), (48, 5), (56, 13), (12, 16)]:
        pixel(d, x, y, STAR)


def draw_celestial(d, daypart):
    if daypart == "night":
        draw_stars(d)
        draw_moon(d, 50, 8)
    elif daypart == "morning":
        draw_sun(d, 10, 10)
    elif daypart == "afternoon":
        draw_sun(d, 32, 6)
    elif daypart == "evening":
        draw_sun(d, 54, 14)


def draw_tree(d, season, base_x=52):
    """장식용 나무 (작게)."""
    trunk = TREE_TRUNK[season]
    rect(d, base_x, 40, base_x + 1, 47, trunk)
    leaves = TREE_LEAVES[season]
    if leaves:
        rect(d, base_x - 3, 32, base_x + 4, 35, leaves)
        rect(d, base_x - 2, 30, base_x + 3, 32, leaves)
        rect(d, base_x - 4, 35, base_x + 5, 39, leaves)
        rect(d, base_x - 2, 39, base_x + 3, 40, leaves)
        pixel(d, base_x + 4, 34, "#000000")
    else:
        pixel(d, base_x - 1, 38, trunk)
        pixel(d, base_x - 2, 36, trunk)
        pixel(d, base_x + 2, 38, trunk)
        pixel(d, base_x + 3, 36, trunk)


def draw_petals(d):
    for x, y in [(10, 18), (22, 24), (35, 14), (52, 20), (8, 30), (45, 32)]:
        pixel(d, x, y, PETAL)


def draw_snow(d):
    for x, y in [
        (5, 10), (12, 18), (20, 6), (28, 14), (35, 8),
        (42, 18), (50, 10), (58, 16), (15, 28), (40, 26),
    ]:
        pixel(d, x, y, SNOW)


# ─────────────────────────────────────────────────────────────
# Building primitives — 각 건물은 ground_y를 기준으로 위로 그림.
# 모두 cx (수평 중심)에 정렬.
# ─────────────────────────────────────────────────────────────
def building_tent(d, cx, gy):
    body, dark, door = "#C04545", "#8A2E2E", "#3A1818"
    for dy in range(0, 10):
        y, half = gy - dy, 9 - dy
        if half < 0:
            break
        rect(d, cx - half, y, cx + half, y, body)
        if half >= 1:
            rect(d, cx + 1, y, cx + half, y, dark)
    rect(d, cx - 1, gy - 3, cx + 1, gy, door)
    pixel(d, cx, gy - 11, "#666666")
    pixel(d, cx, gy - 12, "#888888")


def building_cabin(d, cx, gy):
    wood, wood_d = "#B07845", "#7B4D2A"
    roof, roof_d = "#5C2E1A", "#3F1E10"
    win = "#FFE680"
    door = "#3A1F10"
    # 바디
    rect(d, cx - 7, gy - 10, cx + 7, gy, wood)
    # 가로 판자 음영
    for y in (gy - 7, gy - 4, gy - 1):
        rect(d, cx - 7, y, cx + 7, y, wood_d)
    # 지붕 (삼각)
    for dy in range(0, 6):
        y = gy - 10 - dy
        half = 8 - dy
        if half < 0:
            break
        rect(d, cx - half, y, cx + half, y, roof)
    rect(d, cx - 8, gy - 10, cx + 8, gy - 10, roof_d)
    # 굴뚝
    rect(d, cx + 4, gy - 14, cx + 5, gy - 11, roof_d)
    # 문
    rect(d, cx - 1, gy - 5, cx + 1, gy, door)
    pixel(d, cx + 1, gy - 3, "#FFD060")
    # 창
    rect(d, cx - 5, gy - 8, cx - 3, gy - 6, win)
    rect(d, cx + 3, gy - 8, cx + 5, gy - 6, win)


def building_yard_house(d, cx, gy):
    """한옥 마당집 — 곡선 기와 + 흙색 벽 + 마당."""
    wall, wall_d = "#E8D5A8", "#A18555"
    roof, roof_d = "#3D2A1F", "#1F1310"
    pillar = "#4A2F1A"
    door = "#4A2F1A"
    paper = "#F2DFAA"
    # 벽
    rect(d, cx - 11, gy - 8, cx + 11, gy, wall)
    # 벽 음영 (오른쪽)
    rect(d, cx + 6, gy - 8, cx + 11, gy, wall_d)
    # 기둥
    for px in (cx - 11, cx - 4, cx + 3, cx + 10):
        rect(d, px, gy - 8, px, gy, pillar)
    # 곡선 지붕 (단을 더해 휘어 보이게)
    rect(d, cx - 13, gy - 9, cx + 13, gy - 9, roof)
    rect(d, cx - 14, gy - 8, cx - 13, gy - 8, roof)
    rect(d, cx + 13, gy - 8, cx + 14, gy - 8, roof)
    rect(d, cx - 12, gy - 11, cx + 12, gy - 10, roof)
    rect(d, cx - 10, gy - 13, cx + 10, gy - 12, roof)
    rect(d, cx - 8, gy - 14, cx + 8, gy - 14, roof_d)
    # 처마 끝 살짝 들림
    pixel(d, cx - 14, gy - 9, roof_d)
    pixel(d, cx + 14, gy - 9, roof_d)
    # 문 (중앙)
    rect(d, cx - 2, gy - 6, cx + 2, gy, door)
    rect(d, cx - 1, gy - 5, cx + 1, gy - 1, paper)
    # 창호지
    rect(d, cx - 9, gy - 6, cx - 6, gy - 3, paper)
    rect(d, cx + 5, gy - 6, cx + 8, gy - 3, paper)


def building_villa(d, cx, gy):
    """2층 빌라 — 베이지 + 청회색 지붕."""
    wall, wall_d = "#E0CCA5", "#A8906A"
    roof, roof_d = "#5B6F88", "#3F4F62"
    win = "#A6D8F0"
    win_d = "#5C99B8"
    door = "#3A2818"
    # 본체
    rect(d, cx - 9, gy - 18, cx + 9, gy, wall)
    rect(d, cx + 6, gy - 18, cx + 9, gy, wall_d)
    # 지붕 (낮은 박공)
    for dy in range(0, 4):
        y, half = gy - 18 - dy, 10 - dy
        if half < 0:
            break
        rect(d, cx - half, y, cx + half, y, roof)
    rect(d, cx - 10, gy - 18, cx + 10, gy - 18, roof_d)
    # 2층 창 4개
    for wx in (cx - 7, cx - 2, cx + 3):
        rect(d, wx, gy - 15, wx + 2, gy - 13, win)
        rect(d, wx + 2, gy - 14, wx + 2, gy - 13, win_d)
    # 1층 창 2개 + 문
    rect(d, cx - 7, gy - 9, cx - 4, gy - 6, win)
    rect(d, cx + 4, gy - 9, cx + 7, gy - 6, win)
    rect(d, cx - 1, gy - 8, cx + 2, gy, door)
    pixel(d, cx + 2, gy - 4, "#D9B85A")
    # 발코니 선
    rect(d, cx - 9, gy - 11, cx + 9, gy - 11, wall_d)


def building_apartment(d, cx, gy):
    """3-4층 아파트 — 회색 본체 + 야간 점등 창."""
    wall, wall_d = "#C4C4C4", "#888888"
    edge = "#5F5F5F"
    win = "#7AB5D8"  # 낮 창
    door = "#3A2A1A"
    rect(d, cx - 8, gy - 26, cx + 8, gy, wall)
    rect(d, cx + 5, gy - 26, cx + 8, gy, wall_d)
    rect(d, cx - 8, gy - 26, cx + 8, gy - 26, edge)
    # 4층 창
    for row_y in (gy - 23, gy - 17, gy - 11):
        for wx in (cx - 6, cx - 1, cx + 4):
            rect(d, wx, row_y, wx + 2, row_y + 2, win)
    # 베란다 가로선
    for y in (gy - 20, gy - 14, gy - 8):
        rect(d, cx - 8, y, cx + 8, y, edge)
    # 1층 입구
    rect(d, cx - 2, gy - 7, cx + 2, gy, door)
    pixel(d, cx + 2, gy - 3, "#D9B85A")
    # 안테나
    rect(d, cx - 1, gy - 29, cx, gy - 27, edge)
    pixel(d, cx, gy - 30, "#C04545")


def building_mansion(d, cx, gy):
    """저택 — 중앙동 + 양측 윙 + 기둥."""
    wall, wall_d = "#F0E1C5", "#B89870"
    roof, roof_d = "#6B3030", "#3E1818"
    win, win_d = "#FFE680", "#B89248"
    door = "#3A1F10"
    pillar = "#F8EED3"
    # 양측 윙
    rect(d, cx - 18, gy - 14, cx - 8, gy, wall)
    rect(d, cx + 8, gy - 14, cx + 18, gy, wall)
    rect(d, cx + 16, gy - 14, cx + 18, gy, wall_d)
    rect(d, cx - 10, gy - 14, cx - 8, gy, wall_d)
    # 윙 지붕
    rect(d, cx - 19, gy - 16, cx - 7, gy - 15, roof)
    rect(d, cx + 7, gy - 16, cx + 19, gy - 15, roof)
    rect(d, cx - 19, gy - 14, cx - 7, gy - 14, roof_d)
    rect(d, cx + 7, gy - 14, cx + 19, gy - 14, roof_d)
    # 중앙동
    rect(d, cx - 9, gy - 22, cx + 9, gy, wall)
    rect(d, cx + 6, gy - 22, cx + 9, gy, wall_d)
    # 중앙 박공 지붕
    for dy in range(0, 5):
        y, half = gy - 22 - dy, 10 - dy
        if half < 0:
            break
        rect(d, cx - half, y, cx + half, y, roof)
    rect(d, cx - 10, gy - 22, cx + 10, gy - 22, roof_d)
    # 기둥 (중앙 입구)
    rect(d, cx - 6, gy - 9, cx - 5, gy, pillar)
    rect(d, cx + 5, gy - 9, cx + 6, gy, pillar)
    rect(d, cx - 7, gy - 10, cx + 7, gy - 10, roof_d)
    # 중앙 문
    rect(d, cx - 3, gy - 9, cx + 3, gy, door)
    pixel(d, cx + 3, gy - 5, "#D9B85A")
    pixel(d, cx - 3, gy - 5, "#D9B85A")
    # 윙 창
    for wx in (cx - 16, cx - 13, cx + 11, cx + 14):
        rect(d, wx, gy - 11, wx + 1, gy - 9, win)
        pixel(d, wx + 1, gy - 9, win_d)
    # 중앙 2층 창
    rect(d, cx - 7, gy - 19, cx - 4, gy - 16, win)
    rect(d, cx + 4, gy - 19, cx + 7, gy - 16, win)
    # 중앙 처마 위 장식 (둥근 창)
    rect(d, cx - 1, gy - 25, cx, gy - 24, win)


BUILDINGS: dict[str, Callable] = {
    "tent": building_tent,
    "cabin": building_cabin,
    "yard_house": building_yard_house,
    "villa": building_villa,
    "apartment": building_apartment,
    "mansion": building_mansion,
}

# 등급별 빌딩 가로 중심 — 트리와 겹치지 않게
BUILDING_CX = {
    "tent": 18,
    "cabin": 20,
    "yard_house": 22,
    "villa": 22,
    "apartment": 20,
    "mansion": 32,
}

# 큰 빌딩(mansion)은 트리를 가림 — 트리 그리지 않거나 작게
DRAW_TREE = {
    "tent": True,
    "cabin": True,
    "yard_house": True,
    "villa": True,
    "apartment": True,
    "mansion": False,
}


# ─────────────────────────────────────────────────────────────
# Composer
# ─────────────────────────────────────────────────────────────
def render(tier: str, season: str, daypart: str) -> Image.Image:
    img = Image.new("RGB", (W, H), SKY[(season, daypart)])
    d = ImageDraw.Draw(img)

    fill_band(d, SKY[(season, daypart)], 0, GROUND_Y - 1)
    draw_celestial(d, daypart)
    fill_band(d, GROUND[season], GROUND_Y, H - 1)

    if season == "spring":
        draw_petals(d)
    elif season == "winter":
        draw_snow(d)

    if DRAW_TREE[tier]:
        draw_tree(d, season)

    BUILDINGS[tier](d, BUILDING_CX[tier], GROUND_Y - 1)

    return img


def upscale(img: Image.Image, scale: int) -> Image.Image:
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def grid(images, cols: int, bg="#222222", pad=8) -> Image.Image:
    rows = (len(images) + cols - 1) // cols
    cw, ch = images[0].size
    out = Image.new(
        "RGB",
        (cols * cw + (cols + 1) * pad, rows * ch + (rows + 1) * pad),
        bg,
    )
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        out.paste(im, (pad + c * (cw + pad), pad + r * (ch + pad)))
    return out


def main():
    base = Path(__file__).resolve().parents[1] / "yard"
    base.mkdir(parents=True, exist_ok=True)

    overview_cells = []  # 등급당 봄/오후 1장씩
    total = 0

    for tier in TIERS:
        tier_dir = base / tier
        tier_dir.mkdir(parents=True, exist_ok=True)
        tier_imgs = []
        for s in SEASONS:
            for d in DAYPARTS:
                img = render(tier, s, d)
                big = upscale(img, SCALE)
                big.save(tier_dir / f"{s}_{d}.png")
                tier_imgs.append(big)
                total += 1
                if s == "spring" and d == "afternoon":
                    overview_cells.append(big)
        # 등급별 4x4 그리드
        grid(tier_imgs, cols=4).save(tier_dir / "_grid.png")
        print(f"  ✓ {tier}: 16개 + grid")

    # 등급 오버뷰: 6 tier × 4 season (오후만)
    overview_by_season = []
    for s in SEASONS:
        for tier in TIERS:
            overview_by_season.append(upscale(render(tier, s, "afternoon"), SCALE))
    grid(overview_by_season, cols=6).save(base / "_overview_tiers.png")
    print(f"\n  ✓ overview (6 tiers × 4 seasons, 오후): _overview_tiers.png")
    print(f"\n총 {total}개 마당 이미지 생성")


if __name__ == "__main__":
    main()
