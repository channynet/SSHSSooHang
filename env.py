import config
from geo import Point
from tile import Tile, TileType
from weather import Weather
from dead_body import DeadBody


class Env:
    """생태계 월드. 타일 그리드, 동물, 사체, 날씨를 보유하고 매 프레임 갱신한다."""

    def __init__(self, grid: list[list[Tile]]):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.weather = Weather()

        self.animals: list = []
        self.entity_loc: dict[object, Point] = {}
        self.dead_bodies: list[DeadBody] = []

        # 자주 조회하는 타일은 미리 모아둔다.
        self.water_tiles = [t for row in grid for t in row if t.kind == TileType.WATER]
        self.plant_tiles = [t for row in grid for t in row if t.kind == TileType.PLANT]

        self.elapsed = 0.0  # 경과 시간(초)
        self.collapsed = False  # 생태계 붕괴 여부
        self.collapse_reason = ""
        self._initial_species: set[str] = set()

    # --- 개체 관리 ---
    def spawn(self, animal) -> None:
        self.animals.append(animal)
        self.entity_loc[animal] = animal.location

    def populate(self, animals: list) -> None:
        for a in animals:
            self.spawn(a)
        self._initial_species = {a.species for a in self.animals}

    def species_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {s: 0 for s in self._initial_species}
        for a in self.animals:
            if a.alive:
                counts[a.species] = counts.get(a.species, 0) + 1
        return counts

    # --- 공간 헬퍼 ---
    def clamp(self, p: Point) -> Point:
        x = min(max(p.x, 0.0), self.width - 1e-3)
        y = min(max(p.y, 0.0), self.height - 1e-3)
        return Point(x, y)

    def tile_at(self, p: Point) -> Tile:
        gx = min(max(int(p.x), 0), self.width - 1)
        gy = min(max(int(p.y), 0), self.height - 1)
        return self.grid[gy][gx]

    def animals_near(self, origin: Point, radius: float, predicate=None) -> list:
        found = []
        for a in self.animals:
            if not a.alive or a.location is origin:
                continue
            if predicate and not predicate(a):
                continue
            if a.location.distance_to(origin) <= radius:
                found.append(a)
        found.sort(key=lambda a: a.location.distance_to(origin))
        return found

    def nearest_animal(self, origin: Point, radius: float, predicate=None):
        near = self.animals_near(origin, radius, predicate)
        return near[0] if near else None

    def nearest_tile(self, origin: Point, tiles: list):
        best, best_d = None, float("inf")
        for t in tiles:
            d = t.center.distance_to(origin)
            if d < best_d:
                best, best_d = t, d
        return best

    def nearest_dung_tile(self, origin: Point, radius: float):
        best, best_d = None, radius
        for row in self.grid:
            for t in row:
                if t.has_dung():
                    d = t.center.distance_to(origin)
                    if d <= best_d:
                        best, best_d = t, d
        return best

    def nearest_dead_body(self, origin: Point, radius: float):
        best, best_d = None, radius
        for b in self.dead_bodies:
            if b.depleted:
                continue
            d = b.location.distance_to(origin)
            if d <= best_d:
                best, best_d = b, d
        return best

    # --- 메인 갱신 루프 ---
    def update(self, dt_ms: float) -> None:
        if self.collapsed:
            return
        dt = dt_ms / 1000.0
        self.elapsed += dt

        # 1) 환경: 날씨 → 식물 재생
        self.weather.update(self, dt)
        for t in self.plant_tiles:
            t.grow_plants(dt, self.weather.is_rainy)

        # 2) 동물: 생리 변화 후 행동 1개 실행
        for animal in list(self.animals):
            if not animal.alive:
                continue
            animal.tick(dt)
            if not animal.alive:
                self._on_death(animal, natural=True)
                continue
            self._dt = dt  # 현재 프레임 dt를 행동에서 참조
            for behavior in animal.behaviors():
                if behavior.determine(animal, self):
                    behavior.act(animal, self)
                    break

        # 3) 사냥 등으로 죽은 개체 정리
        for animal in list(self.animals):
            if not animal.alive:
                self._on_death(animal, natural=False)

        # 4) 사체: 각자의 행동(부패) 실행
        self._dt = dt
        for body in list(self.dead_bodies):
            for behavior in body.behaviors():
                if behavior.determine(body, self):
                    behavior.act(body, self)
            if body.depleted:
                self.dead_bodies.remove(body)

        # 5) 종료조건 검사
        self._check_extinction()

    def _on_death(self, animal, natural: bool) -> None:
        if animal in self.entity_loc:
            del self.entity_loc[animal]
        if animal in self.animals:
            self.animals.remove(animal)
        # 자연사(굶주림/갈증)는 사체를 남긴다. 포식으로 먹힌 경우는 남기지 않는다.
        if natural:
            self.dead_bodies.append(
                DeadBody(animal.location, animal.species, animal.size)
            )

    def _check_extinction(self) -> None:
        for species, count in self.species_counts().items():
            if count == 0:
                self.collapsed = True
                self.collapse_reason = (
                    f"{species} 종이 멸종하여 먹이사슬이 붕괴했습니다."
                )
                return
