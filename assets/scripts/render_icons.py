"""
마카롱 화폐 + 마일스톤 + UI 아이콘.

16x16 픽셀 아이콘 — 작은 사이즈는 RN <Image> 컴포넌트나 헤더 배지에 직접 사용 가능.
일부 큰 아이콘은 32x32.

Run: python3 assets/scripts/render_icons.py
Out: assets/icons/{name}.png  + assets/icons/_overview.png
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw

SCALE = 16

def new_layer(size=16):
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def pixel(d, x, y, c, w=None, h=None):
    d.point((x, y), fill=c)


def rect(d, x0, y0, x1, y1, c):
    if x1 < x0 or y1 < y0:
        return
    d.rectangle([x0, y0, x1, y1], fill=c)


def upscale(img, scale):
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


# ─────────────────────────────────────────────────────────────
# 화폐 (16x16)
# ─────────────────────────────────────────────────────────────
def icon_macaron():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 위 빵 (분홍)
    rect(d, 3, 3, 12, 5, "#F8B8D0")
    rect(d, 4, 2, 11, 2, "#F8B8D0")
    rect(d, 3, 5, 12, 5, "#E89AB8")
    # 크림
    rect(d, 4, 6, 11, 8, "#FFE8C8")
    rect(d, 4, 8, 11, 8, "#E0C078")
    # 아래 빵
    rect(d, 3, 9, 12, 11, "#F8B8D0")
    rect(d, 4, 12, 11, 12, "#F8B8D0")
    rect(d, 3, 9, 12, 9, "#FFD0E0")
    # 광택
    pixel(d, 6, 3, "#FFFFFF")
    pixel(d, 5, 10, "#FFFFFF")
    return img


def icon_coin():
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 4, 2, 11, 13, "#F8D060")
    rect(d, 3, 4, 12, 11, "#F8D060")
    rect(d, 2, 6, 13, 9, "#F8D060")
    # 음영
    rect(d, 11, 4, 12, 11, "#C8902A")
    rect(d, 9, 12, 11, 13, "#C8902A")
    # 광택
    pixel(d, 5, 3, "#FFFFFF")
    pixel(d, 6, 3, "#FFFFFF")
    pixel(d, 4, 4, "#FFFFFF")
    # M 글자
    rect(d, 6, 6, 6, 9, "#7A5418")
    rect(d, 9, 6, 9, 9, "#7A5418")
    pixel(d, 7, 7, "#7A5418")
    pixel(d, 8, 7, "#7A5418")
    return img


# ─────────────────────────────────────────────────────────────
# 마일스톤 아이콘 (16x16)
# ─────────────────────────────────────────────────────────────
def icon_step():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 발자국 2개
    # 왼발
    rect(d, 3, 4, 5, 8, "#7B4A2A")
    rect(d, 2, 9, 3, 9, "#7B4A2A")
    rect(d, 5, 9, 6, 9, "#7B4A2A")
    pixel(d, 4, 3, "#7B4A2A")
    # 오른발
    rect(d, 9, 7, 11, 12, "#7B4A2A")
    rect(d, 8, 13, 9, 13, "#7B4A2A")
    rect(d, 11, 13, 12, 13, "#7B4A2A")
    pixel(d, 10, 6, "#7B4A2A")
    return img


def icon_flights():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 계단 — 좌하 → 우상
    rect(d, 2, 12, 5, 13, "#888888")
    rect(d, 5, 10, 8, 13, "#888888")
    rect(d, 8, 8, 11, 13, "#888888")
    rect(d, 11, 6, 13, 13, "#888888")
    # 엣지 하이라이트
    rect(d, 2, 12, 5, 12, "#C0C0C0")
    rect(d, 5, 10, 8, 10, "#C0C0C0")
    rect(d, 8, 8, 11, 8, "#C0C0C0")
    rect(d, 11, 6, 13, 6, "#C0C0C0")
    # 상승 화살표
    pixel(d, 12, 3, "#5DBB3C")
    rect(d, 11, 4, 13, 4, "#5DBB3C")
    rect(d, 10, 5, 14, 5, "#5DBB3C")
    return img


def icon_distance():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 핀
    rect(d, 6, 2, 9, 5, "#E04848")
    rect(d, 5, 3, 10, 4, "#E04848")
    pixel(d, 7, 3, "#FFFFFF")
    pixel(d, 8, 3, "#FFFFFF")
    rect(d, 7, 6, 8, 9, "#A02828")
    # 점선 경로
    pixel(d, 4, 11, "#3A88C8")
    pixel(d, 6, 12, "#3A88C8")
    pixel(d, 8, 12, "#3A88C8")
    pixel(d, 10, 11, "#3A88C8")
    pixel(d, 12, 13, "#3A88C8")
    return img


def icon_attendance():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 달력
    rect(d, 2, 3, 13, 13, "#F8F8F8")
    rect(d, 2, 3, 13, 5, "#E04848")
    rect(d, 2, 13, 13, 13, "#C8C8C8")
    rect(d, 4, 2, 5, 4, "#888888")
    rect(d, 10, 2, 11, 4, "#888888")
    # 체크
    rect(d, 5, 8, 5, 9, "#5DBB3C")
    rect(d, 6, 9, 6, 10, "#5DBB3C")
    rect(d, 7, 10, 7, 9, "#5DBB3C")
    rect(d, 8, 9, 8, 8, "#5DBB3C")
    rect(d, 9, 7, 9, 8, "#5DBB3C")
    rect(d, 10, 7, 10, 6, "#5DBB3C")
    return img


def icon_ad():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 비디오 프레임
    rect(d, 2, 4, 11, 12, "#1A1A1A")
    rect(d, 3, 5, 10, 11, "#3A88C8")
    # 재생 삼각형
    rect(d, 5, 6, 5, 10, "#FFFFFF")
    rect(d, 6, 7, 6, 9, "#FFFFFF")
    rect(d, 7, 8, 7, 8, "#FFFFFF")
    # 화면 우상에 선물
    rect(d, 11, 2, 13, 4, "#E04848")
    pixel(d, 12, 3, "#F8D060")
    return img


# ─────────────────────────────────────────────────────────────
# 등급 배지 (16x16) — 6단계
# ─────────────────────────────────────────────────────────────
def _badge(rank: int, body_color: str, ring_color: str):
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 외부 링
    rect(d, 4, 2, 11, 2, ring_color)
    rect(d, 4, 13, 11, 13, ring_color)
    rect(d, 2, 4, 2, 11, ring_color)
    rect(d, 13, 4, 13, 11, ring_color)
    rect(d, 3, 3, 3, 3, ring_color)
    rect(d, 12, 3, 12, 3, ring_color)
    rect(d, 3, 12, 3, 12, ring_color)
    rect(d, 12, 12, 12, 12, ring_color)
    # 본체
    rect(d, 4, 3, 11, 12, body_color)
    rect(d, 3, 4, 12, 11, body_color)
    # 광택
    pixel(d, 5, 4, "#FFFFFF")
    pixel(d, 6, 4, "#FFFFFF")
    # 등급 점
    if rank == 1:
        pixel(d, 8, 8, "#FFFFFF")
    elif rank == 2:
        rect(d, 6, 8, 9, 8, "#FFFFFF")
    elif rank == 3:
        rect(d, 6, 7, 9, 9, "#FFFFFF")
        pixel(d, 7, 8, body_color)
        pixel(d, 8, 8, body_color)
    elif rank == 4:
        rect(d, 5, 6, 10, 10, "#FFFFFF")
        rect(d, 7, 7, 8, 9, body_color)
    elif rank == 5:
        # 별 5각
        rect(d, 7, 5, 8, 5, "#F8E040")
        rect(d, 4, 7, 11, 7, "#F8E040")
        rect(d, 5, 8, 10, 8, "#F8E040")
        rect(d, 5, 9, 6, 11, "#F8E040")
        rect(d, 9, 9, 10, 11, "#F8E040")
    elif rank == 6:
        # 별 + 광선
        rect(d, 7, 4, 8, 5, "#F8E040")
        rect(d, 4, 6, 11, 7, "#F8E040")
        rect(d, 5, 8, 10, 8, "#F8E040")
        rect(d, 5, 9, 6, 11, "#F8E040")
        rect(d, 9, 9, 10, 11, "#F8E040")
        pixel(d, 3, 3, "#FFFFFF")
        pixel(d, 12, 3, "#FFFFFF")
        pixel(d, 3, 12, "#FFFFFF")
        pixel(d, 12, 12, "#FFFFFF")
    return img


def icon_tier_tent():       return _badge(1, "#888888", "#5C5C5C")
def icon_tier_cabin():      return _badge(2, "#7B4A2A", "#4A2A18")
def icon_tier_yard_house(): return _badge(3, "#3D7AB8", "#2A5688")
def icon_tier_villa():      return _badge(4, "#5C8A3A", "#3A5A20")
def icon_tier_apartment():  return _badge(5, "#B85C2A", "#7A3A18")
def icon_tier_mansion():    return _badge(6, "#9A3AB8", "#5A1F7A")


# ─────────────────────────────────────────────────────────────
# 시즌/시간대 아이콘 (16x16)
# ─────────────────────────────────────────────────────────────
def icon_spring():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 벚꽃 꽃
    rect(d, 7, 4, 8, 5, "#F4A8C0")
    rect(d, 5, 6, 10, 9, "#F4A8C0")
    rect(d, 6, 10, 9, 10, "#F4A8C0")
    pixel(d, 4, 7, "#F4A8C0")
    pixel(d, 11, 7, "#F4A8C0")
    # 중심
    pixel(d, 7, 7, "#F8E040")
    pixel(d, 8, 7, "#F8E040")
    # 꽃잎 떨어지는
    pixel(d, 3, 12, "#F4A8C0")
    pixel(d, 12, 13, "#F4A8C0")
    return img


def icon_summer():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 태양
    rect(d, 6, 4, 9, 11, "#F8D060")
    rect(d, 4, 6, 11, 9, "#F8D060")
    rect(d, 5, 5, 10, 10, "#F8D060")
    # 광선
    pixel(d, 7, 2, "#F8D060")
    pixel(d, 8, 2, "#F8D060")
    pixel(d, 7, 13, "#F8D060")
    pixel(d, 8, 13, "#F8D060")
    pixel(d, 2, 7, "#F8D060")
    pixel(d, 2, 8, "#F8D060")
    pixel(d, 13, 7, "#F8D060")
    pixel(d, 13, 8, "#F8D060")
    return img


def icon_autumn():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 단풍잎
    rect(d, 7, 3, 8, 4, "#D86A1F")
    rect(d, 5, 5, 10, 5, "#D86A1F")
    rect(d, 4, 6, 11, 8, "#D86A1F")
    rect(d, 5, 9, 10, 9, "#D86A1F")
    rect(d, 5, 10, 6, 10, "#D86A1F")
    rect(d, 9, 10, 10, 10, "#D86A1F")
    # 줄기
    rect(d, 7, 11, 8, 13, "#5C3A20")
    return img


def icon_winter():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 눈송이
    rect(d, 7, 2, 8, 13, "#9CC4E8")
    rect(d, 2, 7, 13, 8, "#9CC4E8")
    # 대각선
    pixel(d, 4, 4, "#9CC4E8")
    pixel(d, 11, 4, "#9CC4E8")
    pixel(d, 4, 11, "#9CC4E8")
    pixel(d, 11, 11, "#9CC4E8")
    pixel(d, 5, 5, "#9CC4E8")
    pixel(d, 10, 5, "#9CC4E8")
    pixel(d, 5, 10, "#9CC4E8")
    pixel(d, 10, 10, "#9CC4E8")
    # 중심
    rect(d, 7, 7, 8, 8, "#FFFFFF")
    return img


# ─────────────────────────────────────────────────────────────
# UI 액션 아이콘 (16x16)
# ─────────────────────────────────────────────────────────────
def icon_refresh():
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 5, 2, 10, 3, "#3D7AB8")
    rect(d, 3, 4, 4, 11, "#3D7AB8")
    rect(d, 11, 4, 12, 11, "#3D7AB8")
    rect(d, 5, 12, 10, 13, "#3D7AB8")
    rect(d, 5, 4, 10, 11, None)
    pixel(d, 4, 4, "#3D7AB8")
    pixel(d, 11, 4, "#3D7AB8")
    pixel(d, 4, 11, "#3D7AB8")
    pixel(d, 11, 11, "#3D7AB8")
    # 화살표
    pixel(d, 10, 1, "#3D7AB8")
    pixel(d, 11, 2, "#3D7AB8")
    pixel(d, 12, 3, "#3D7AB8")
    return img


def icon_home():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 지붕
    for dy in range(0, 5):
        y = 3 + dy
        half = 6 - dy
        rect(d, 8 - half, y, 7 + half, y, "#C04545")
    rect(d, 1, 7, 14, 7, "#8A2E2E")
    # 본체
    rect(d, 3, 8, 12, 13, "#F0E1C5")
    rect(d, 11, 8, 12, 13, "#B89870")
    # 문
    rect(d, 6, 9, 8, 13, "#5C3A20")
    pixel(d, 8, 11, "#D9B85A")
    return img


def icon_settings():
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 톱니바퀴
    rect(d, 6, 1, 9, 2, "#888888")
    rect(d, 6, 13, 9, 14, "#888888")
    rect(d, 1, 6, 2, 9, "#888888")
    rect(d, 13, 6, 14, 9, "#888888")
    rect(d, 3, 3, 4, 4, "#888888")
    rect(d, 11, 3, 12, 4, "#888888")
    rect(d, 3, 11, 4, 12, "#888888")
    rect(d, 11, 11, 12, 12, "#888888")
    rect(d, 4, 4, 11, 11, "#888888")
    # 중심
    rect(d, 6, 6, 9, 9, "#3A3A3A")
    return img


# ─────────────────────────────────────────────────────────────
# 등록
# ─────────────────────────────────────────────────────────────
ICONS = {
    # 화폐
    "macaron": icon_macaron,
    "coin": icon_coin,
    # 마일스톤
    "step": icon_step,
    "flights": icon_flights,
    "distance": icon_distance,
    "attendance": icon_attendance,
    "ad": icon_ad,
    # 등급
    "tier_tent": icon_tier_tent,
    "tier_cabin": icon_tier_cabin,
    "tier_yard_house": icon_tier_yard_house,
    "tier_villa": icon_tier_villa,
    "tier_apartment": icon_tier_apartment,
    "tier_mansion": icon_tier_mansion,
    # 시즌
    "spring": icon_spring,
    "summer": icon_summer,
    "autumn": icon_autumn,
    "winter": icon_winter,
    # UI
    "refresh": icon_refresh,
    "home": icon_home,
    "settings": icon_settings,
}


def grid(images, labels, cols, bg="#1F1F1F", pad=10):
    rows = (len(images) + cols - 1) // cols
    cw, ch = images[0].size
    label_h = 14
    out = Image.new(
        "RGBA",
        (cols * cw + (cols + 1) * pad, rows * (ch + label_h) + (rows + 1) * pad),
        bg,
    )
    d = ImageDraw.Draw(out)
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad)
        y = pad + r * (ch + label_h)
        out.paste(im, (x, y), im if im.mode == "RGBA" else None)
        d.text((x + 2, y + ch), labels[i], fill="#CCCCCC")
    return out


def main():
    base = Path(__file__).resolve().parents[1] / "icons"
    base.mkdir(parents=True, exist_ok=True)

    big_imgs = []
    labels = []
    for name, fn in ICONS.items():
        img = fn()
        # 작은 (16x16) + 큰 (4x 확대)
        img.save(base / f"{name}.png")
        big = upscale(img, SCALE)
        big.save(base / f"{name}@{SCALE}x.png")
        big_imgs.append(big)
        labels.append(name)

    overview = grid(big_imgs, labels, cols=5)
    overview.save(base / "_overview.png")
    print(f"  ✓ {len(ICONS)}개 아이콘 (16px + {SCALE}x) + overview")


if __name__ == "__main__":
    main()
