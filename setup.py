"""월드 생성과 초기 개체군 배치."""

import random

import config
from env import Env
from tile import Tile, TileType
from geo import Point

from elephant import Elephant
from eagle import Eagle
from cheetah import Cheetah
from rabbit import Rabbit
from dung_beetle import DungBeetle
from hyena import Hyena
from lion import Lion
from zebra import Zebra

# 종별 초기 개체 수 (먹이사슬 균형용)
POPULATION = {
    Zebra: 14,
    Rabbit: 24,  # 포식 강화·번식 쿨다운↑에 맞춰 ~2분 붕괴하도록 버퍼 증량
    Elephant: 4,
    DungBeetle: 8,
    Lion: 3,
    Hyena: 5,
    Cheetah: 4,
    Eagle: 4,
}


def _build_grid(rng: random.Random) -> list[list[Tile]]:
    # 기본은 육지
    grid = [
        [Tile(x, y, TileType.LAND) for x in range(config.GRID_W)]
        for y in range(config.GRID_H)
    ]

    # 물 웅덩이 몇 개 배치
    for _ in range(4):
        cx, cy = rng.randint(4, config.GRID_W - 5), rng.randint(4, config.GRID_H - 5)
        r = rng.randint(2, 4)
        for y in range(max(0, cy - r), min(config.GRID_H, cy + r + 1)):
            for x in range(max(0, cx - r), min(config.GRID_W, cx + r + 1)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    grid[y][x] = Tile(x, y, TileType.WATER)

    # 나머지 육지의 절반가량을 식물 타일로
    for row in grid:
        for i, t in enumerate(row):
            if t.kind == TileType.LAND and rng.random() < 0.5:
                row[i] = Tile(t.gx, t.gy, TileType.PLANT)
    return grid


def _random_land_point(grid, rng: random.Random) -> Point:
    while True:
        x = rng.randint(0, config.GRID_W - 1)
        y = rng.randint(0, config.GRID_H - 1)
        if grid[y][x].kind != TileType.WATER:
            return Point(x + 0.5, y + 0.5)


def build_env(seed: int | None = None) -> Env:
    rng = random.Random(seed)
    grid = _build_grid(rng)
    env = Env(grid)

    animals = []
    for species_cls, count in POPULATION.items():
        for i in range(count):
            gender = "M" if i % 2 == 0 else "F"  # 번식을 위해 성별 균형 보장
            animals.append(species_cls(_random_land_point(grid, rng), gender))
    env.populate(animals)
    return env
