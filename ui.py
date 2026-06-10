"""pygame 기반 렌더링. pygame이 없으면 콘솔 요약으로 대체된다 (headless)."""

import os

import config
from tile import TileType

try:
    import pygame

    HEADLESS = False
except ImportError:  # pragma: no cover - 환경에 pygame이 없을 때
    pygame = None
    HEADLESS = True

_screen = None
_font = None
_big_font = None
_clock = None
_headless_timer = 0.0

LAND_COLOR = (188, 160, 110)

# --- 스프라이트 에셋 (gen_assets.py로 생성) ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_assets = {"ok": False, "tiles": {}, "animals": {}, "objects": {}, "weather": {}}
_animal_scaled = {}  # (species, px) -> 스케일된 Surface 캐시
_shade = None        # 물/식물 잔량 표현용 반투명 검정 사각형
_terrain_bg = None   # 정적 지형을 미리 합쳐둔 배경 (매 프레임 한 번에 blit)


def _load_assets() -> None:
    """assets/의 PNG를 로드한다. 실패하면 _assets['ok']=False로 두어 도형 렌더로 폴백."""
    if HEADLESS:
        return
    global _shade

    def _load(*path):
        return pygame.image.load(os.path.join(ASSETS_DIR, *path)).convert_alpha()

    try:
        ts = config.TILE_PX
        for k in ("land", "water", "plant"):
            _assets["tiles"][k] = pygame.transform.scale(_load("tiles", f"{k}.png"), (ts, ts))
        for k in ("zebra", "rabbit", "elephant", "dung_beetle",
                  "lion", "hyena", "cheetah", "eagle"):
            _assets["animals"][k] = _load("animals", f"{k}.png")
        for k in ("dung", "dead_body"):
            _assets["objects"][k] = _load("objects", f"{k}.png")
        for k in ("sunny", "rainy"):
            _assets["weather"][k] = _load("ui", f"{k}.png")
        _shade = pygame.Surface((ts, ts))
        _shade.fill((0, 0, 0))
        _assets["ok"] = True
    except (pygame.error, FileNotFoundError) as e:  # 에셋 없거나 손상 → 폴백
        _assets["ok"] = False
        print(f"[ui] 스프라이트 로드 실패, 도형 렌더로 대체합니다: {e}")


def init(env) -> None:
    global _screen, _font, _big_font, _clock
    if HEADLESS:
        print("[headless] pygame이 없어 콘솔 모드로 실행합니다.")
        return
    pygame.init()
    w = env.width * config.TILE_PX
    h = env.height * config.TILE_PX + config.HUD_H
    _screen = pygame.display.set_mode((w, h), pygame.SCALED | pygame.FULLSCREEN)
    pygame.display.set_caption("세렝게티의 눈물  (Space/P: 일시정지, ESC: 종료, F/F11: 전체화면)")
    # malgungothic(맑은 고딕)이 있으면 한글이 정상 출력된다. 없으면 다음 후보로 폴백.
    _font = pygame.font.SysFont("malgungothic,applegothic,arialunicodems", 16)
    _big_font = pygame.font.SysFont("malgungothic,applegothic,arialunicodems", 34)
    _clock = pygame.time.Clock()
    _load_assets()


def draw(env, paused: bool = False) -> tuple[bool, bool]:
    """한 프레임 렌더. (계속 실행 여부, 일시정지 여부)를 반환."""
    if HEADLESS:
        return _draw_headless(env), paused

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, paused
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False, paused
            if event.key in (pygame.K_SPACE, pygame.K_p):
                paused = not paused
            if event.key in (pygame.K_f, pygame.K_F11):
                pygame.display.toggle_fullscreen()

    _draw_tiles(env)
    _draw_dead_bodies(env)
    _draw_animals(env)
    _draw_hud(env)
    if paused and not env.collapsed:
        _draw_paused()
    if env.collapsed:
        _draw_collapse(env)

    pygame.display.flip()
    _clock.tick(60)
    return True, paused


def _px(coord: float) -> int:
    return int(coord * config.TILE_PX)


def _draw_tiles(env) -> None:
    ts = config.TILE_PX
    use = _assets["ok"]
    global _terrain_bg
    if use:
        # 정적 지형(물/육지/식물 배치)은 변하지 않으므로 한 번만 합쳐두고 재사용한다.
        if _terrain_bg is None:
            _terrain_bg = pygame.Surface((env.width * ts, env.height * ts))
            for row in env.grid:
                for t in row:
                    key = ("water" if t.kind == TileType.WATER
                           else "plant" if t.kind == TileType.PLANT else "land")
                    _terrain_bg.blit(_assets["tiles"][key], (t.gx * ts, t.gy * ts))
        _screen.blit(_terrain_bg, (0, 0))  # 프레임당 지형 blit 1회
    for row in env.grid:
        for t in row:
            px, py = t.gx * ts, t.gy * ts
            if use:
                # 잔량이 적은 물/식물 타일만 어둡게 덧칠 (상태 피드백 유지)
                if t.kind == TileType.WATER:
                    ratio = t.water / config.WATER_TILE_MAX
                elif t.kind == TileType.PLANT:
                    ratio = t.plant / config.PLANT_MAX
                else:
                    ratio = 1.0
                if ratio < 0.98:
                    _shade.set_alpha(int(150 * (1.0 - ratio)))
                    _screen.blit(_shade, (px, py))
            else:
                if t.kind == TileType.WATER:
                    shade = int(120 + 100 * (t.water / config.WATER_TILE_MAX))
                    color = (40, 90, shade)
                elif t.kind == TileType.PLANT:
                    g = int(90 + 130 * (t.plant / config.PLANT_MAX))
                    color = (50, g, 50)
                else:
                    color = LAND_COLOR
                pygame.draw.rect(_screen, color, (px, py, ts, ts))
            if t.has_dung():
                if use:
                    img = _assets["objects"]["dung"]
                    _screen.blit(img, (px + ts // 2 - img.get_width() // 2,
                                       py + ts // 2 - img.get_height() // 2))
                else:
                    cx, cy = px + ts // 2, py + ts // 2
                    pygame.draw.circle(_screen, (90, 60, 30), (cx, cy), 3)


def _draw_dead_bodies(env) -> None:
    img = _assets["objects"].get("dead_body") if _assets["ok"] else None
    for b in env.dead_bodies:
        x, y = _px(b.location.x), _px(b.location.y)
        if img is not None:
            _screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
        else:
            pygame.draw.line(_screen, (120, 30, 30), (x - 4, y - 4), (x + 4, y + 4), 2)
            pygame.draw.line(_screen, (120, 30, 30), (x - 4, y + 4), (x + 4, y - 4), 2)


def _animal_sprite(a):
    """동물의 size에 맞춰 스케일된 스프라이트를 반환 (종별 캐시). 없으면 None."""
    base = _assets["animals"].get(a.species)
    if base is None:
        return None
    px = max(14, int(round(14 + a.size * 3.0)))
    key = (a.species, px)
    spr = _animal_scaled.get(key)
    if spr is None:
        spr = pygame.transform.smoothscale(base, (px, px))
        _animal_scaled[key] = spr
    return spr


def _draw_animals(env) -> None:
    use = _assets["ok"]
    for a in env.animals:
        if not a.alive:
            continue
        x, y = _px(a.location.x), _px(a.location.y)
        spr = _animal_sprite(a) if use else None
        if spr is not None:
            w, h = spr.get_size()
            _screen.blit(spr, (x - w // 2, y - h // 2))
            if getattr(a, "is_flying", False):
                pygame.draw.circle(_screen, (255, 255, 255), (x, y), w // 2 + 2, 1)
        else:
            r = max(3, int(2 + a.size * 1.8))
            pygame.draw.circle(_screen, a.color, (x, y), r)
            pygame.draw.circle(_screen, (20, 20, 20), (x, y), r, 1)
            if getattr(a, "is_flying", False):
                pygame.draw.circle(_screen, (255, 255, 255), (x, y), r + 3, 1)


def _draw_hud(env) -> None:
    ts = config.TILE_PX
    top = env.height * ts
    pygame.draw.rect(_screen, (25, 25, 30), (0, top, _screen.get_width(), config.HUD_H))

    counts = env.species_counts()
    summary = "  ".join(f"{s}:{n}" for s, n in sorted(counts.items()))
    line1 = f"날씨 {env.weather.state}   경과 {env.elapsed:5.0f}s"
    _blit(line1, 8, top + 8, (230, 230, 120))
    if _assets["ok"]:
        icon = _assets["weather"].get(env.weather.state)
        if icon is not None:
            _screen.blit(icon, (_screen.get_width() - icon.get_width() - 10, top + 6))
    _blit(summary, 8, top + 34, (210, 210, 220))
    total = sum(counts.values())
    _blit(f"총 개체수 {total}", 8, top + 60, (160, 200, 160))


def _draw_collapse(env) -> None:
    overlay = pygame.Surface(_screen.get_size())
    overlay.set_alpha(170)
    overlay.fill((0, 0, 0))
    _screen.blit(overlay, (0, 0))
    msg = _big_font.render("생태계 붕괴", True, (240, 80, 80))
    _screen.blit(
        msg,
        msg.get_rect(center=(_screen.get_width() // 2, _screen.get_height() // 2 - 20)),
    )
    reason = _font.render(env.collapse_reason, True, (230, 230, 230))
    _screen.blit(
        reason,
        reason.get_rect(
            center=(_screen.get_width() // 2, _screen.get_height() // 2 + 20)
        ),
    )


def _draw_paused() -> None:
    overlay = pygame.Surface(_screen.get_size())
    overlay.set_alpha(120)
    overlay.fill((0, 0, 0))
    _screen.blit(overlay, (0, 0))
    msg = _big_font.render("일시정지", True, (245, 245, 245))
    _screen.blit(msg, msg.get_rect(center=_screen.get_rect().center))


def _blit(text, x, y, color) -> None:
    _screen.blit(_font.render(text, True, color), (x, y))


# --- headless 대체 렌더 ---
def _draw_headless(env) -> bool:
    global _headless_timer
    _headless_timer += config.MS_PER_FRAME
    if _headless_timer >= 1000:  # 1초마다 요약 출력
        _headless_timer = 0.0
        counts = env.species_counts()
        summary = "  ".join(f"{s}:{n}" for s, n in sorted(counts.items()))
        print(f"[{env.elapsed:6.0f}s] {env.weather.state:5}  {summary}")
    if env.collapsed:
        print(f"\n=== {env.collapse_reason} (경과 {env.elapsed:.0f}s) ===")
        return False
    return True


def finish(env, keep_open: bool = True) -> None:
    if HEADLESS:
        return
    if not keep_open:
        pygame.quit()
        return
    # 창이 닫힐 때까지 마지막 화면 유지
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                return
        _clock.tick(30)
