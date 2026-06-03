import config
from geo import Point


class TileType:
    LAND = "land"
    WATER = "water"
    PLANT = "plant"


class Tile:
    """월드를 구성하는 2D 타일. 물/육지/식물 중 하나의 종류를 가진다."""

    def __init__(self, gx: int, gy: int, kind: str):
        self.gx = gx
        self.gy = gy
        self.kind = kind
        # 물 타일은 물의 양을, 식물 타일은 식물의 양을 가진다.
        self.water = config.WATER_TILE_MAX if kind == TileType.WATER else 0.0
        self.plant = config.PLANT_MAX if kind == TileType.PLANT else 0.0
        self.dung = 0.0

    @property
    def center(self) -> Point:
        return Point(self.gx + 0.5, self.gy + 0.5)

    # --- 상태 조회 ---
    def has_food(self) -> bool:
        return self.kind == TileType.PLANT and self.plant > 1.0

    def has_water(self) -> bool:
        return self.kind == TileType.WATER and self.water > 1.0

    def has_dung(self) -> bool:
        return self.dung > 0.0

    # --- 환경 변화 (Phase 2) ---
    def decrease_water(self, dt_sec: float) -> None:
        if self.kind == TileType.WATER:
            self.water = max(0.0, self.water - config.SUNNY_WATER_LOSS * dt_sec)

    def increase_water(self, dt_sec: float) -> None:
        if self.kind == TileType.WATER:
            self.water = min(config.WATER_TILE_MAX, self.water + config.RAIN_WATER_GAIN * dt_sec)

    def grow_plants(self, dt_sec: float, rainy: bool) -> None:
        if self.kind == TileType.PLANT:
            rate = config.PLANT_REGEN * (config.RAIN_PLANT_BONUS if rainy else 1.0)
            self.plant = min(config.PLANT_MAX, self.plant + rate * dt_sec)
