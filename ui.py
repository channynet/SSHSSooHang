"""pygame 기반 렌더링. pygame이 없으면 콘솔 요약으로 대체된다 (headless)."""

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


def init(env) -> None:
    global _screen, _font, _big_font, _clock
    if HEADLESS:
        print("[headless] pygame이 없어 콘솔 모드로 실행합니다.")
        return
    pygame.init()
    w = env.width * config.TILE_PX
    h = env.height * config.TILE_PX + config.HUD_H
    _screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("세렝게티의 눈물")
    _font = pygame.font.SysFont("applegothic,arialunicodems", 16)
    _big_font = pygame.font.SysFont("applegothic,arialunicodems", 34)
    _clock = pygame.time.Clock()


def draw(env) -> bool:
    """한 프레임 렌더. 계속 실행하면 True, 종료하면 False 반환."""
    if HEADLESS:
        return _draw_headless(env)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

    _draw_tiles(env)
    _draw_dead_bodies(env)
    _draw_animals(env)
    _draw_hud(env)
    if env.collapsed:
        _draw_collapse(env)

    pygame.display.flip()
    _clock.tick(60)
    return True


def _px(coord: float) -> int:
    return int(coord * config.TILE_PX)


def _draw_tiles(env) -> None:
    ts = config.TILE_PX
    for row in env.grid:
        for t in row:
            if t.kind == TileType.WATER:
                shade = int(120 + 100 * (t.water / config.WATER_TILE_MAX))
                color = (40, 90, shade)
            elif t.kind == TileType.PLANT:
                g = int(90 + 130 * (t.plant / config.PLANT_MAX))
                color = (50, g, 50)
            else:
                color = LAND_COLOR
            pygame.draw.rect(_screen, color, (t.gx * ts, t.gy * ts, ts, ts))
            if t.has_dung():
                cx, cy = t.gx * ts + ts // 2, t.gy * ts + ts // 2
                pygame.draw.circle(_screen, (90, 60, 30), (cx, cy), 3)


def _draw_dead_bodies(env) -> None:
    for b in env.dead_bodies:
        x, y = _px(b.location.x), _px(b.location.y)
        pygame.draw.line(_screen, (120, 30, 30), (x - 4, y - 4), (x + 4, y + 4), 2)
        pygame.draw.line(_screen, (120, 30, 30), (x - 4, y + 4), (x + 4, y - 4), 2)


def _draw_animals(env) -> None:
    for a in env.animals:
        if not a.alive:
            continue
        x, y = _px(a.location.x), _px(a.location.y)
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


def finish(env) -> None:
    if HEADLESS:
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
