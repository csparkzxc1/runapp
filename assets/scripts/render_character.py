"""
캐릭터 스프라이트 + 9슬롯 코스튬 시연.

캔버스: 32x48 (정면 단일 프레임).
슬롯: 배경 / 얼굴 / 머리장식 / 모자 / 상의 / 하의 / 신발 / 장갑 / 손악세
앵커: 머리 중심(16,12), 몸 중심(16,28), 발(16,42)

각 슬롯에 2-3 변형 만들어 레이어드 합성 시연.

Run: python3 assets/scripts/render_character.py
Out: assets/character/parts/{slot}_{key}.png   (개별 슬롯)
     assets/character/composed/{preset}.png    (프리셋 합성)
     assets/character/_overview.png            (프리셋 그리드 + 슬롯 그리드)
"""

from __future__ import annotations
from pathlib import Path
from typing import Callable
from PIL import Image, ImageDraw

W, H = 32, 48
SCALE = 8
TRANSPARENT = (0, 0, 0, 0)

# 앵커
HEAD_CX, HEAD_CY = 16, 12
BODY_CX, BODY_CY = 16, 28
FEET_CX, FEET_Y  = 16, 42

# ─────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────
def new_layer() -> Image.Image:
    return Image.new("RGBA", (W, H), TRANSPARENT)


def pixel(d, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        d.point((x, y), fill=c)


def rect(d, x0, y0, x1, y1, c):
    if x1 < x0 or y1 < y0:
        return
    d.rectangle([x0, y0, x1, y1], fill=c)


# ─────────────────────────────────────────────────────────────
# 슬롯 1: 배경
# ─────────────────────────────────────────────────────────────
def bg_none() -> Image.Image:
    return new_layer()


def bg_sky() -> Image.Image:
    img = Image.new("RGBA", (W, H), "#A8DCF0")
    d = ImageDraw.Draw(img)
    # 구름
    for cx, cy in [(7, 8), (24, 14)]:
        rect(d, cx - 2, cy, cx + 2, cy, "#FFFFFF")
        rect(d, cx - 1, cy - 1, cx + 1, cy - 1, "#FFFFFF")
    return img


def bg_room() -> Image.Image:
    img = Image.new("RGBA", (W, H), "#F4E1C2")
    d = ImageDraw.Draw(img)
    rect(d, 0, 36, W - 1, H - 1, "#8B5A3C")   # 마루
    rect(d, 0, 36, W - 1, 36, "#5C3A20")
    # 액자
    rect(d, 4, 8, 10, 14, "#7D4A2A")
    rect(d, 5, 9, 9, 13, "#E0C078")
    return img


def bg_night() -> Image.Image:
    img = Image.new("RGBA", (W, H), "#1A1F3D")
    d = ImageDraw.Draw(img)
    for x, y in [(4, 6), (10, 3), (18, 8), (25, 5), (8, 12), (22, 14)]:
        pixel(d, x, y, "#FFFFFF")
    rect(d, 23, 18, 25, 20, "#F2F0D8")   # 달
    return img


BACKGROUNDS = {
    "none": bg_none,
    "sky": bg_sky,
    "room": bg_room,
    "night": bg_night,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 2: 얼굴 (기본 신체 포함 — 머리/몸통/팔/다리)
# 얼굴 그 자체보다 "기본 캐릭터 베이스" 역할.
# 변형: 피부톤 + 표정
# ─────────────────────────────────────────────────────────────
def face_base(skin: str, blush: str, expression: str = "smile") -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 머리 (8x8 + 약간 둥근 모서리)
    rect(d, 12, 8, 19, 15, skin)
    pixel(d, 12, 8, TRANSPARENT)
    pixel(d, 19, 8, TRANSPARENT)
    pixel(d, 12, 15, TRANSPARENT)
    pixel(d, 19, 15, TRANSPARENT)
    # 목
    rect(d, 14, 16, 17, 17, skin)
    # 팔
    rect(d, 9, 21, 11, 32, skin)
    rect(d, 20, 21, 22, 32, skin)
    # 다리
    rect(d, 13, 36, 14, 41, skin)
    rect(d, 17, 36, 18, 41, skin)
    # 발 (살색이 신발 슬롯에 가려지지만 베이스로 그림)
    rect(d, 12, 42, 15, 42, skin)
    rect(d, 16, 42, 19, 42, skin)
    # 볼터치
    pixel(d, 13, 12, blush)
    pixel(d, 18, 12, blush)
    # 눈
    if expression == "smile":
        pixel(d, 14, 11, "#000000")
        pixel(d, 17, 11, "#000000")
        # 입
        pixel(d, 15, 13, "#7B3A1F")
        pixel(d, 16, 13, "#7B3A1F")
    elif expression == "wink":
        pixel(d, 14, 11, "#000000")
        rect(d, 17, 11, 17, 11, "#7B3A1F")
        # 입 ^
        rect(d, 15, 13, 16, 13, "#7B3A1F")
    elif expression == "sleepy":
        rect(d, 14, 11, 14, 11, "#7B3A1F")
        rect(d, 17, 11, 17, 11, "#7B3A1F")
        pixel(d, 16, 13, "#7B3A1F")
    return img


def face_light():  return face_base("#FCD8B0", "#FFB098", "smile")
def face_tan():    return face_base("#D9A87A", "#B87858", "smile")
def face_wink():   return face_base("#FCD8B0", "#FFB098", "wink")
def face_sleepy(): return face_base("#FCD8B0", "#FFB098", "sleepy")

FACES = {
    "light": face_light,
    "tan": face_tan,
    "wink": face_wink,
    "sleepy": face_sleepy,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 3: 머리장식 (앞머리/머리띠/포니테일 등)
# ─────────────────────────────────────────────────────────────
def hair_short_black() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 머리 윗부분
    rect(d, 12, 7, 19, 10, "#1A1A22")
    rect(d, 13, 6, 18, 6, "#1A1A22")
    # 앞머리
    rect(d, 12, 9, 14, 10, "#1A1A22")
    rect(d, 17, 9, 19, 10, "#1A1A22")
    # 옆머리
    pixel(d, 11, 11, "#1A1A22")
    pixel(d, 20, 11, "#1A1A22")
    return img


def hair_pony_brown() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 7, 19, 9, "#7B4A2A")
    rect(d, 13, 6, 18, 6, "#7B4A2A")
    # 앞머리
    rect(d, 13, 9, 15, 10, "#7B4A2A")
    # 옆머리
    pixel(d, 11, 11, "#7B4A2A")
    pixel(d, 20, 11, "#7B4A2A")
    # 포니테일
    rect(d, 21, 11, 23, 15, "#7B4A2A")
    rect(d, 22, 16, 22, 17, "#7B4A2A")
    # 머리끈
    rect(d, 21, 11, 23, 11, "#E04848")
    return img


def hair_pink_bun() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 7, 19, 9, "#E47BAB")
    rect(d, 13, 6, 18, 6, "#E47BAB")
    rect(d, 12, 9, 13, 10, "#E47BAB")
    rect(d, 18, 9, 19, 10, "#E47BAB")
    # 양 옆 만두
    rect(d, 10, 6, 11, 8, "#E47BAB")
    rect(d, 20, 6, 21, 8, "#E47BAB")
    pixel(d, 10, 6, "#C45A8B")
    pixel(d, 21, 6, "#C45A8B")
    return img


HAIRS = {
    "none": new_layer,
    "short_black": hair_short_black,
    "pony_brown": hair_pony_brown,
    "pink_bun": hair_pink_bun,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 4: 모자
# ─────────────────────────────────────────────────────────────
def hat_cap_red() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 6, 19, 8, "#D03030")
    rect(d, 13, 5, 18, 5, "#D03030")
    rect(d, 12, 9, 22, 9, "#A82020")  # 챙
    rect(d, 15, 4, 16, 4, "#F8E040")  # 단추
    return img


def hat_beanie_blue() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 5, 19, 9, "#3D7AB8")
    rect(d, 13, 4, 18, 4, "#3D7AB8")
    rect(d, 11, 9, 20, 9, "#2A5688")
    rect(d, 15, 3, 16, 3, "#E0F0FF")  # 방울
    return img


def hat_witch_purple() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 10, 8, 21, 9, "#3A2858")    # 챙
    # 원뿔
    for i, dy in enumerate(range(0, 8)):
        y = 7 - dy
        half = 4 - i // 2
        if half < 0:
            break
        rect(d, 16 - half, y, 15 + half, y, "#3A2858")
    pixel(d, 15, 0, "#D9B85A")  # 끝 별
    return img


HATS = {
    "none": new_layer,
    "cap_red": hat_cap_red,
    "beanie_blue": hat_beanie_blue,
    "witch_purple": hat_witch_purple,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 5: 상의
# ─────────────────────────────────────────────────────────────
def shirt_tee_white() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 11, 18, 20, 28, "#F8F8F8")
    rect(d, 9, 18, 11, 23, "#F8F8F8")
    rect(d, 20, 18, 22, 23, "#F8F8F8")
    rect(d, 18, 18, 20, 23, "#D8D8D8")
    rect(d, 14, 18, 17, 19, "#C8C8C8")  # 목선
    return img


def shirt_hoodie_orange() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 11, 18, 20, 30, "#E07A30")
    rect(d, 9, 18, 11, 24, "#E07A30")
    rect(d, 20, 18, 22, 24, "#E07A30")
    rect(d, 18, 18, 20, 24, "#A85015")
    # 후드
    rect(d, 12, 16, 19, 19, "#E07A30")
    rect(d, 13, 17, 18, 18, "#A85015")
    # 끈
    pixel(d, 14, 19, "#FFFFFF")
    pixel(d, 17, 19, "#FFFFFF")
    return img


def shirt_dress_pink() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 11, 18, 20, 25, "#F08AB0")
    # 드레스 자락
    rect(d, 10, 26, 21, 35, "#F08AB0")
    rect(d, 9, 30, 22, 35, "#F08AB0")
    rect(d, 9, 35, 22, 35, "#C04880")
    # 어깨
    rect(d, 9, 18, 11, 22, "#F08AB0")
    rect(d, 20, 18, 22, 22, "#F08AB0")
    # 리본
    rect(d, 15, 18, 16, 19, "#FFFFFF")
    pixel(d, 14, 19, "#FFFFFF")
    pixel(d, 17, 19, "#FFFFFF")
    return img


SHIRTS = {
    "tee_white": shirt_tee_white,
    "hoodie_orange": shirt_hoodie_orange,
    "dress_pink": shirt_dress_pink,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 6: 하의
# ─────────────────────────────────────────────────────────────
def pants_jeans() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 29, 14, 41, "#3D5A88")
    rect(d, 17, 29, 19, 41, "#3D5A88")
    # 음영
    rect(d, 14, 29, 14, 41, "#2A3F60")
    rect(d, 19, 29, 19, 41, "#2A3F60")
    rect(d, 12, 29, 19, 29, "#5A7AAA")  # 벨트선
    return img


def pants_shorts_brown() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 29, 14, 35, "#7B4A2A")
    rect(d, 17, 29, 19, 35, "#7B4A2A")
    rect(d, 14, 29, 14, 35, "#5C3A20")
    rect(d, 19, 29, 19, 35, "#5C3A20")
    return img


def pants_skirt_navy() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    # A라인
    rect(d, 11, 28, 20, 30, "#2A3A60")
    rect(d, 10, 30, 21, 35, "#2A3A60")
    rect(d, 9, 35, 22, 36, "#2A3A60")
    # 주름
    for x in (12, 15, 18):
        rect(d, x, 30, x, 35, "#1A2540")
    return img


PANTS = {
    "jeans": pants_jeans,
    "shorts_brown": pants_shorts_brown,
    "skirt_navy": pants_skirt_navy,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 7: 신발
# ─────────────────────────────────────────────────────────────
def shoes_sneakers_white() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 42, 15, 43, "#F8F8F8")
    rect(d, 16, 42, 19, 43, "#F8F8F8")
    rect(d, 12, 43, 15, 43, "#C8C8C8")
    rect(d, 16, 43, 19, 43, "#C8C8C8")
    pixel(d, 13, 42, "#E04040")
    pixel(d, 18, 42, "#E04040")
    return img


def shoes_boots_black() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 12, 40, 14, 43, "#1A1A1A")
    rect(d, 17, 40, 19, 43, "#1A1A1A")
    rect(d, 11, 43, 15, 43, "#1A1A1A")
    rect(d, 16, 43, 20, 43, "#1A1A1A")
    pixel(d, 12, 40, "#5C5C5C")
    pixel(d, 19, 40, "#5C5C5C")
    return img


def shoes_slippers_red() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 11, 43, 15, 43, "#C04040")
    rect(d, 16, 43, 20, 43, "#C04040")
    return img


SHOES = {
    "sneakers_white": shoes_sneakers_white,
    "boots_black": shoes_boots_black,
    "slippers_red": shoes_slippers_red,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 8: 장갑
# ─────────────────────────────────────────────────────────────
def gloves_none():
    return new_layer()


def gloves_mittens_red() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 9, 31, 11, 33, "#D03030")
    rect(d, 20, 31, 22, 33, "#D03030")
    rect(d, 9, 30, 11, 30, "#A82020")
    rect(d, 20, 30, 22, 30, "#A82020")
    return img


def gloves_white() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    rect(d, 9, 31, 11, 32, "#F8F8F8")
    rect(d, 20, 31, 22, 32, "#F8F8F8")
    return img


GLOVES = {
    "none": gloves_none,
    "mittens_red": gloves_mittens_red,
    "white": gloves_white,
}


# ─────────────────────────────────────────────────────────────
# 슬롯 9: 손악세 (들고 있는 것)
# ─────────────────────────────────────────────────────────────
def acc_none():
    return new_layer()


def acc_macaron() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 오른손에 마카롱
    rect(d, 20, 30, 22, 30, "#F8B8D0")
    rect(d, 20, 31, 22, 31, "#E89AB8")
    rect(d, 20, 32, 22, 32, "#F8B8D0")
    pixel(d, 21, 31, "#FFFFFF")
    return img


def acc_sword() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 검 (오른손)
    rect(d, 21, 22, 21, 32, "#C0C8D0")
    pixel(d, 20, 31, "#7A5A2A")    # 손잡이
    rect(d, 20, 32, 22, 33, "#7A5A2A")
    pixel(d, 21, 21, "#F8F8F8")
    return img


def acc_balloon() -> Image.Image:
    img = new_layer()
    d = ImageDraw.Draw(img)
    # 풍선
    rect(d, 24, 6, 28, 10, "#E04040")
    rect(d, 23, 7, 23, 9, "#E04040")
    rect(d, 29, 7, 29, 9, "#E04040")
    pixel(d, 24, 7, "#FFFFFF")
    # 줄
    for y in range(11, 30):
        pixel(d, 26 - (y % 2), y, "#888888")
    return img


ACCS = {
    "none": acc_none,
    "macaron": acc_macaron,
    "sword": acc_sword,
    "balloon": acc_balloon,
}


# 슬롯 순서 (아래→위 합성)
SLOT_ORDER = ["bg", "face", "hair", "hat", "shirt", "pants", "shoes", "gloves", "acc"]
SLOT_REGISTRY = {
    "bg": BACKGROUNDS,
    "face": FACES,
    "hair": HAIRS,
    "hat": HATS,
    "shirt": SHIRTS,
    "pants": PANTS,
    "shoes": SHOES,
    "gloves": GLOVES,
    "acc": ACCS,
}
SLOT_LABEL_KO = {
    "bg": "배경",
    "face": "얼굴",
    "hair": "머리장식",
    "hat": "모자",
    "shirt": "상의",
    "pants": "하의",
    "shoes": "신발",
    "gloves": "장갑",
    "acc": "손악세",
}


def compose(parts: dict[str, str]) -> Image.Image:
    """parts = {slot: key}. 슬롯 순서대로 알파 합성."""
    base = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    for slot in SLOT_ORDER:
        key = parts.get(slot, "none")
        registry = SLOT_REGISTRY[slot]
        if key not in registry:
            continue
        layer = registry[key]()
        if slot == "bg" and key == "none":
            # 투명 배경 → 체커보드 대신 회색
            bg_img = Image.new("RGBA", (W, H), "#E8E8E8")
            base = bg_img
            continue
        base = Image.alpha_composite(base.convert("RGBA"), layer)
    return base


def upscale(img: Image.Image, scale: int) -> Image.Image:
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def grid(images, cols: int, bg="#2C2C2C", pad=8) -> Image.Image:
    rows = (len(images) + cols - 1) // cols
    cw, ch = images[0].size
    out = Image.new(
        "RGBA",
        (cols * cw + (cols + 1) * pad, rows * ch + (rows + 1) * pad),
        bg,
    )
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        out.paste(im, (pad + c * (cw + pad), pad + r * (ch + pad)))
    return out


# ─────────────────────────────────────────────────────────────
# 프리셋 (9슬롯 동시 시연용)
# ─────────────────────────────────────────────────────────────
PRESETS = {
    "casual_walker": {
        "bg": "sky", "face": "light", "hair": "short_black",
        "hat": "cap_red", "shirt": "tee_white", "pants": "jeans",
        "shoes": "sneakers_white", "gloves": "none", "acc": "macaron",
    },
    "cozy_winter": {
        "bg": "room", "face": "tan", "hair": "pony_brown",
        "hat": "beanie_blue", "shirt": "hoodie_orange", "pants": "jeans",
        "shoes": "boots_black", "gloves": "mittens_red", "acc": "balloon",
    },
    "witch_quest": {
        "bg": "night", "face": "wink", "hair": "pink_bun",
        "hat": "witch_purple", "shirt": "dress_pink", "pants": "skirt_navy",
        "shoes": "slippers_red", "gloves": "white", "acc": "sword",
    },
    "sleepy_default": {
        "bg": "none", "face": "sleepy", "hair": "short_black",
        "hat": "none", "shirt": "tee_white", "pants": "shorts_brown",
        "shoes": "slippers_red", "gloves": "none", "acc": "none",
    },
}


def main():
    base = Path(__file__).resolve().parents[1] / "character"
    parts_dir = base / "parts"
    composed_dir = base / "composed"
    parts_dir.mkdir(parents=True, exist_ok=True)
    composed_dir.mkdir(parents=True, exist_ok=True)

    # 1) 슬롯별 개별 PNG (디자이너 참고용)
    for slot, registry in SLOT_REGISTRY.items():
        for key in registry:
            if key == "none":
                continue
            # 슬롯 단독 + 베이스 얼굴 (구도 확인용)
            if slot == "face":
                img = registry[key]()
            elif slot == "bg":
                img = registry[key]()
            else:
                base_img = face_light()
                layer = registry[key]()
                img = Image.alpha_composite(base_img, layer)
            big = upscale(img, SCALE)
            big.save(parts_dir / f"{slot}_{key}.png")

    # 2) 프리셋 합성
    composed_images = []
    for name, parts in PRESETS.items():
        img = compose(parts)
        big = upscale(img, SCALE)
        big.save(composed_dir / f"{name}.png")
        composed_images.append(big)

    # 3) 오버뷰: 4 프리셋 + 슬롯별 변형 그리드
    overview_top = grid(composed_images, cols=4)

    # 슬롯별 그리드 (face 4, hair 4, hat 4, shirt 3, pants 3, shoes 3, gloves 3, acc 4 → 가변)
    slot_rows = []
    for slot in ["face", "hair", "hat", "shirt", "pants", "shoes", "gloves", "acc"]:
        slot_imgs = []
        for key, fn in SLOT_REGISTRY[slot].items():
            if slot == "face":
                base_img = fn()
            else:
                base_img = face_light()
                layer = fn()
                base_img = Image.alpha_composite(base_img, layer)
            slot_imgs.append(upscale(base_img, SCALE))
        # 4열 그리드
        slot_rows.append(grid(slot_imgs, cols=4))

    # 슬롯 그리드를 위에서 아래로 스택
    max_w = max(r.width for r in [overview_top] + slot_rows)
    total_h = overview_top.height + sum(r.height + 4 for r in slot_rows)
    overview = Image.new("RGBA", (max_w, total_h), "#1F1F1F")
    overview.paste(overview_top, (0, 0))
    y = overview_top.height
    for r in slot_rows:
        overview.paste(r, (0, y))
        y += r.height + 4
    overview.save(base / "_overview.png")

    n_parts = sum(
        1 for slot, reg in SLOT_REGISTRY.items() for k in reg if k != "none"
    )
    print(f"  ✓ {n_parts}개 파츠 + {len(PRESETS)} 프리셋 + overview")


if __name__ == "__main__":
    main()
