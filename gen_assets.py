"""스프라이트 PNG 생성기 (pygame만 사용, 추가 의존성 없음).

실행하면 assets/ 폴더에 동물 8종 + 타일 3종 + 오브젝트 2종 + 날씨 2종의
픽셀아트 PNG를 그려서 저장한다. 결정적(deterministic)이며 재실행 가능.

    python gen_assets.py
"""

import base64
import io
import os

import pygame

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")

# 동물 캔버스는 32x32 정사각형(스케일·중앙정렬을 단순화하기 위함)
A = 32


# --- 색 헬퍼 ---
def darker(c, f=0.6):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def lighter(c, f=0.4):
    return (
        int(c[0] + (255 - c[0]) * f),
        int(c[1] + (255 - c[1]) * f),
        int(c[2] + (255 - c[2]) * f),
    )


def surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def save(s, *path):
    out = os.path.join(ASSETS, *path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(s, out)
    return out


def _legs(s, color, hoof, xs, top, h, w=3):
    for x in xs:
        pygame.draw.rect(s, color, (x, top, w, h))
        if hoof:
            pygame.draw.rect(s, hoof, (x, top + h - 2, w, 2))


# ------------------------------------------------------------------ 동물
def zebra():
    s = surf(A, A)
    white = (236, 236, 238)
    black = (38, 38, 44)
    _legs(s, white, black, [7, 12, 18, 22], 19, 9)
    pygame.draw.ellipse(s, white, (4, 10, 21, 11))          # 몸통
    pygame.draw.polygon(s, white, [(20, 12), (29, 6), (31, 12), (24, 18)])  # 목
    pygame.draw.ellipse(s, white, (26, 4, 6, 8))            # 머리
    pygame.draw.polygon(s, black, [(27, 4), (29, 0), (30, 4)])  # 귀
    pygame.draw.line(s, black, (22, 8), (28, 5), 2)         # 갈기
    for x in range(8, 23, 3):                               # 줄무늬
        pygame.draw.line(s, black, (x, 11), (x, 20), 1)
    pygame.draw.line(s, white, (5, 12), (1, 18), 2)         # 꼬리
    pygame.draw.circle(s, black, (1, 18), 2)
    return s


def rabbit():
    s = surf(A, A)
    white = (236, 236, 240)
    pink = (240, 180, 195)
    pygame.draw.ellipse(s, white, (8, 15, 13, 10))          # 몸통
    pygame.draw.circle(s, white, (10, 21), 3)               # 꼬리 솜
    pygame.draw.ellipse(s, white, (17, 11, 9, 9))           # 머리
    pygame.draw.ellipse(s, white, (18, 1, 4, 12))           # 귀
    pygame.draw.ellipse(s, white, (22, 1, 4, 12))
    pygame.draw.ellipse(s, pink, (19, 3, 2, 8))
    pygame.draw.ellipse(s, pink, (23, 3, 2, 8))
    pygame.draw.circle(s, (40, 40, 45), (23, 15), 1)        # 눈
    pygame.draw.circle(s, pink, (25, 17), 1)                # 코
    return s


def elephant():
    s = surf(A, A)
    body = (148, 138, 156)
    pygame.draw.rect(s, body, (6, 18, 5, 9))                # 다리
    pygame.draw.rect(s, body, (12, 18, 5, 9))
    pygame.draw.rect(s, body, (18, 18, 5, 9))
    pygame.draw.rect(s, body, (23, 18, 4, 9))
    pygame.draw.ellipse(s, body, (3, 7, 23, 15))            # 몸통
    pygame.draw.ellipse(s, body, (20, 6, 11, 13))          # 머리
    pygame.draw.ellipse(s, darker(body, 0.8), (18, 5, 9, 13))  # 귀
    pygame.draw.lines(s, body, False,                       # 코
                      [(29, 12), (31, 17), (29, 22), (30, 27)], 4)
    pygame.draw.line(s, (235, 230, 220), (27, 18), (29, 25), 2)  # 상아
    pygame.draw.circle(s, (40, 40, 45), (25, 11), 1)       # 눈
    pygame.draw.line(s, body, (3, 10), (1, 8), 2)          # 꼬리
    return s


def dung_beetle():
    s = surf(A, A)
    body = (66, 66, 78)
    ball = (96, 72, 46)
    pygame.draw.circle(s, ball, (8, 18), 6)                 # 똥 공
    pygame.draw.circle(s, darker(ball, 0.7), (6, 16), 1)
    pygame.draw.circle(s, darker(ball, 0.7), (10, 20), 1)
    for dx, dy in [(-1, 4), (2, 5), (5, 5)]:                # 다리
        pygame.draw.line(s, body, (16 + dx, 16), (16 + dx + dy - 4, 24), 1)
    pygame.draw.ellipse(s, body, (15, 11, 13, 10))          # 등딱지
    pygame.draw.line(s, darker(body, 0.5), (21, 11), (21, 21), 1)
    pygame.draw.circle(s, body, (28, 15), 3)                # 머리
    pygame.draw.circle(s, lighter(body, 0.5), (18, 14), 1)  # 광택
    return s


def lion():
    s = surf(A, A)
    body = (202, 152, 74)
    mane = (150, 100, 44)
    _legs(s, body, darker(body, 0.7), [8, 13, 18, 22], 19, 9)
    pygame.draw.ellipse(s, body, (5, 11, 19, 10))           # 몸통
    pygame.draw.line(s, body, (5, 13), (1, 17), 2)          # 꼬리
    pygame.draw.circle(s, mane, (26, 11), 3)                # 꼬리술
    pygame.draw.circle(s, mane, (25, 10), 8)                # 갈기
    pygame.draw.circle(s, body, (26, 9), 7)                # 머리
    pygame.draw.ellipse(s, lighter(body, 0.3), (27, 9, 6, 6))  # 주둥이
    pygame.draw.circle(s, (40, 35, 30), (28, 8), 1)        # 눈
    return s


def hyena():
    s = surf(A, A)
    body = (164, 144, 96)
    spot = darker(body, 0.55)
    _legs(s, body, darker(body, 0.7), [9, 13, 19, 23], 19, 9)
    pygame.draw.ellipse(s, body, (6, 12, 17, 9))            # 몸통(뒤 낮음)
    pygame.draw.ellipse(s, body, (16, 8, 10, 11))          # 어깨(앞 높음)
    pygame.draw.ellipse(s, body, (24, 7, 8, 8))            # 머리
    pygame.draw.polygon(s, body, [(25, 7), (24, 2), (28, 5)])  # 귀
    pygame.draw.line(s, darker(body, 0.6), (18, 8), (14, 13), 2)  # 갈기
    for cx, cy in [(10, 15), (14, 17), (18, 14), (12, 18)]:  # 점무늬
        pygame.draw.circle(s, spot, (cx, cy), 1)
    pygame.draw.circle(s, (40, 35, 30), (29, 10), 1)       # 눈
    return s


def cheetah():
    s = surf(A, A)
    body = (212, 172, 64)
    spot = (45, 35, 25)
    _legs(s, body, darker(body, 0.7), [8, 12, 18, 22], 20, 8, w=2)
    pygame.draw.ellipse(s, body, (5, 14, 20, 7))            # 날렵한 몸통
    pygame.draw.line(s, body, (5, 16), (0, 9), 2)           # 긴 꼬리
    pygame.draw.circle(s, body, (27, 13), 5)               # 작은 머리
    for cx, cy in [(9, 16), (13, 17), (17, 15), (21, 16),   # 점무늬
                   (11, 19), (15, 19), (4, 13), (2, 11)]:
        pygame.draw.circle(s, spot, (cx, cy), 1)
    pygame.draw.line(s, spot, (28, 12), (28, 16), 1)        # 눈물자국
    pygame.draw.circle(s, (40, 35, 30), (29, 12), 1)       # 눈
    return s


def eagle():
    s = surf(A, A)
    body = (96, 74, 52)
    wing = darker(body, 0.7)
    head = (236, 236, 230)
    pygame.draw.polygon(s, wing, [(15, 13), (1, 7), (3, 16), (15, 18)])   # 좌 날개
    pygame.draw.polygon(s, wing, [(17, 13), (31, 7), (29, 16), (17, 18)])  # 우 날개
    pygame.draw.line(s, darker(body, 0.5), (3, 9), (14, 15), 1)
    pygame.draw.line(s, darker(body, 0.5), (29, 9), (18, 15), 1)
    pygame.draw.ellipse(s, body, (13, 9, 6, 15))           # 몸통
    pygame.draw.polygon(s, body, [(13, 22), (11, 31), (21, 31), (19, 22)])  # 꼬리
    pygame.draw.circle(s, head, (16, 7), 4)                # 흰 머리
    pygame.draw.polygon(s, (240, 190, 50), [(16, 7), (16, 11), (19, 9)])   # 부리
    pygame.draw.circle(s, (30, 30, 30), (15, 6), 1)        # 눈
    return s


# ------------------------------------------------------------------ 타일
def _speckle(s, w, h, base, n, c1, c2):
    # 결정적 의사난수 점 배치
    seed = 2166136261
    for i in range(n):
        seed = (seed * 16777619 + 1) & 0xFFFFFFFF
        x = seed % w
        seed = (seed * 16777619 + 1) & 0xFFFFFFFF
        y = seed % h
        s.set_at((x, y), c1 if i % 2 else c2)


def tile_land():
    ts = 22
    s = surf(ts, ts)
    base = (188, 160, 110)
    s.fill(base)
    _speckle(s, ts, ts, base, 60, darker(base, 0.85), lighter(base, 0.2))
    return s


def tile_water():
    ts = 22
    s = surf(ts, ts)
    base = (40, 95, 175)
    s.fill(base)
    crest = lighter(base, 0.35)
    for y in range(3, ts, 5):
        for x in range(0, ts, 6):
            off = 2 if (y // 5) % 2 else 0
            pygame.draw.line(s, crest, (x + off, y), (x + off + 3, y), 1)
    return s


def tile_plant():
    ts = 22
    s = surf(ts, ts)
    base = (48, 120, 48)
    s.fill(base)
    dark = darker(base, 0.7)
    light = lighter(base, 0.3)
    for x in range(1, ts, 3):
        h = 4 + (x * 7) % 5
        pygame.draw.line(s, dark if x % 2 else light, (x, ts - 1), (x, ts - 1 - h), 1)
    return s


# ------------------------------------------------------------------ 오브젝트
_DUNG_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAZKADAAQAAAABAAAAZAAAAAAvu95BAAADl0lEQVR4Ae2WQRLbIAxF006P1ZN03WN13ZP0Xm3w1ETIsg0WGPA8z2RMsPSR3gcnrxcXBCAAAQhAAAIQgAAEIAABCEAAAhCAwIMJ/H33Fj6PuL5M3oU2YvZ+Xl8nNkSbMXErn9Jn3VFHZsza0+LKzCdkaeDXj++v8BHXkVkibMzhjIZE4MoISTjExDj5YPTxjIaYTHfMmc6U2d63EfCOAYtZP3//sUyboteZTkg0w6It53bMys6XWnePp9g1/6FEoDvATXbGaRm656GLU4QXQ0rMkPnKmGH7nuWVFU+HhFwyVkYGPbdmyfq5sTMYEsEpqLk9xjhvfhRqOBj26IqeoyHrnBesen0F2WE4DFPIClvdN2bI51eNMQwJskOwGKIICVmMoxkSvAVTPhf5p0NDqzuP7gXsUItmhOcWcA3TitnRTqa1zvthVyZdF0/IpF+iIWegNdCz+HSZzzel041Lt4U/KDajbDPWTAVznV7uJQYZOrfzmeFvbwLY+hKgl4C3NMKcoRE3x15O7fnbd0BGAwsEA05Gar0QdVpu4zTaCbl9R+5ZqDbEbXXd5vxe42I+Nq1giJD7h+qkhAKaMhvthNxP/GRFY3PEjXOSeulxU7cLKkqaNCAUSLULVaelCTtOyHX/kk10XSbNHMGQTWNqJ6YVd/p2V00jGBIRy1fVXQDi4geDg1o2m+lAJuvRUIaEirUpBzCyGvQG6fVDfbLGt35VU3obEpuRTcpxAKqheCHn5st1DSNyZYrimvxTKKjANETmSyjrvDZsna9xL1lPxVZhWUXEAWIx5Aywatxc7kzDTBKTZ2tY+kaOm6dbQPRUOjw9HZagAcEKqz5nGRIWUfW4eboFHJ1fMsRaT0GxQlxze2asomp9F1NX8lrQxXs1Qy6uXzVNmOJi2vtfVlUoTxDrbsjZ6+AJkEt66G5ISbGjxorXlbtEDHEjrCvQ3ZCau6sumjw1Vb/rBz2s6BbIK9uMiv+y1qcz/Z4oI0ILVVhWEVmBXrhvTAkaoxtjmBHKrsKyikioxnltjBnVFMOMqgyrijlNCemJMaOYYpgQam3CroloqNZ5JcY4tVqkN+P2rUW1D9VsZsJDedEWBCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQgAAEIQAACEIAABCAAAQhAAAIQgAAEIAABCEAAAhCAAAQkgX8Wq7wkh+irBgAAAABJRU5ErkJggg=="
)


def _fit_object_sprite(src, size):
    bounds = src.get_bounding_rect(min_alpha=1)
    out = surf(size, size)
    if bounds.width <= 0 or bounds.height <= 0:
        return out

    scale = min(size / bounds.width, size / bounds.height)
    w = max(1, round(bounds.width * scale))
    h = max(1, round(bounds.height * scale))
    scaled = pygame.transform.scale(src.subsurface(bounds), (w, h))
    out.blit(scaled, ((size - w) // 2, (size - h) // 2))
    return out


def dung():
    src = pygame.image.load(io.BytesIO(base64.b64decode(_DUNG_PNG_B64)), "dung.png")
    return _fit_object_sprite(src, 16)


def dead_body():
    s = surf(16, 16)
    bone = (224, 218, 206)
    sh = darker(bone, 0.8)
    pygame.draw.circle(s, bone, (4, 8), 3)                  # 두개골
    pygame.draw.circle(s, sh, (3, 8), 1)                   # 눈구멍
    pygame.draw.line(s, bone, (7, 8), (14, 8), 2)         # 척추
    for x in range(8, 14, 2):                              # 갈비뼈
        pygame.draw.arc(s, bone, (x - 1, 4, 4, 9), 3.4, 6.0, 1)
    return s


# ------------------------------------------------------------------ 날씨
def weather_sunny():
    s = surf(24, 24)
    sun = (255, 208, 56)
    ray = (255, 188, 40)
    import math
    for i in range(8):
        a = i * math.pi / 4
        x0, y0 = 12 + 8 * math.cos(a), 12 + 8 * math.sin(a)
        x1, y1 = 12 + 11 * math.cos(a), 12 + 11 * math.sin(a)
        pygame.draw.line(s, ray, (x0, y0), (x1, y1), 2)
    pygame.draw.circle(s, sun, (12, 12), 7)
    return s


def weather_rainy():
    s = surf(24, 24)
    cloud = (206, 206, 216)
    rain = (84, 134, 224)
    pygame.draw.ellipse(s, cloud, (2, 5, 12, 8))
    pygame.draw.ellipse(s, cloud, (8, 3, 12, 9))
    pygame.draw.ellipse(s, cloud, (4, 8, 16, 7))
    for x in (6, 11, 16):
        pygame.draw.line(s, rain, (x, 15), (x - 2, 21), 2)
    return s


ANIMALS = {
    "zebra": zebra, "rabbit": rabbit, "elephant": elephant,
    "dung_beetle": dung_beetle, "lion": lion, "hyena": hyena,
    "cheetah": cheetah, "eagle": eagle,
}
TILES = {"land": tile_land, "water": tile_water, "plant": tile_plant}
OBJECTS = {"dung": dung, "dead_body": dead_body}
WEATHER = {"sunny": weather_sunny, "rainy": weather_rainy}


def main():
    made = []
    for name, fn in ANIMALS.items():
        made.append(save(fn(), "animals", f"{name}.png"))
    for name, fn in TILES.items():
        made.append(save(fn(), "tiles", f"{name}.png"))
    for name, fn in OBJECTS.items():
        made.append(save(fn(), "objects", f"{name}.png"))
    for name, fn in WEATHER.items():
        made.append(save(fn(), "ui", f"{name}.png"))
    print(f"생성 완료: {len(made)}개 스프라이트 -> {ASSETS}")
    for p in made:
        print("  ", os.path.relpath(p, BASE))


if __name__ == "__main__":
    main()
