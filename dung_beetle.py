"""담당: 박시은"""

import config
from animal import Animal
from base import Behavior
from behaviors import Flee, SeekWater, Breed, Wander


class RollDung(Behavior):
    """배설물을 찾아 공을 굴린다 (ball_size가 점점 커짐)."""

    def should_run(self, e, env) -> bool:
        if e.ball_size >= config.DUNG_BALL_EAT_SIZE:
            return False
        # claimer=e: 다른 쇠똥구리가 더 가까운 똥은 그쪽에 양보하고, 나는 내게
        # 가장 가까운 '비어 있는' 똥을 맡는다 (한 곳 몰림 방지).
        tile = env.nearest_dung_tile(e.location, e.detection_range, claimer=e)
        e._dung_tile = tile
        return tile is not None

    def act(self, e, env) -> None:
        tile = e._dung_tile
        if e.location.distance_to(tile.center) < 0.8:
            e.start_rolling(tile)
        else:
            e.step_toward(tile.center, env, env._dt)


class EatDung(Behavior):
    """공 크기가 일정 수준 이상이면 섭취한다."""

    def should_run(self, e, env) -> bool:
        return e.is_rolling and e.ball_size >= config.DUNG_BALL_EAT_SIZE

    def act(self, e, env) -> None:
        e.eat_dung()


class DungBeetle(Animal):
    species = "dung_beetle"
    color = (60, 60, 70)
    base_speed = 1.35
    size = 0.3
    detection_range = 13.0
    flee_speed_mult = 1.6
    max_body_water = 120.0
    max_fullness = 140.0

    def __init__(self, location, gender=None):
        super().__init__(location, gender)
        self.is_rolling = False
        self.ball_size = 0.0

    def start_rolling(self, tile) -> None:
        self.is_rolling = True
        taken = min(config.DUNG_BEETLE_COLLECT_AMOUNT, tile.dung)
        tile.dung -= taken
        self.ball_size += taken
        if not getattr(self, "_announced", False):
            print("쇠똥구리가 배설물을 발견하여 공을 굴리기 시작합니다!")
            self._announced = True

    def eat_dung(self) -> None:
        self.fullness = min(self.max_fullness, self.fullness + self.ball_size * 8.0)
        self.is_rolling = False
        self.ball_size = 0.0
        self._announced = False
        print("공 크기가 충분하여 쇠똥구리가 섭취했습니다.")

    def build_behaviors(self) -> list:
        from elephant import Elephant

        return [
            Flee(target_classes=[Elephant]),
            SeekWater(),
            EatDung(),
            RollDung(),
            Breed(),
            Wander(),
        ]
