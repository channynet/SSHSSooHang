"""담당: 김민찬D"""

import config
from animal import Animal
from base import Behavior
from behaviors import ProduceDung, SeekWater, SeekPlantFood, Breed, Wander
from dead_body import DeadBody


class Trample(Behavior):
    """passive: 발밑에 들어온 주어진 종(쇠똥구리/토끼)을 짓밟는다 (토끼는 jump로 회피 가능)."""

    def __init__(self, target_classes):
        # 짓밟을 Animal 하위 클래스들 (isinstance용 튜플)
        self.target_classes = tuple(target_classes)

    def determine(self, e, env) -> bool:
        victim = env.nearest_animal(
            e.location,
            config.INTERACT_RADIUS,
            lambda a: isinstance(a, self.target_classes),
        )
        e._victim = victim
        return victim is not None

    def act(self, e, env) -> None:
        v = e._victim
        if not v.on_capture_attempt(e, env):
            return  # 회피 성공
        v.alive = False
        env.dead_bodies.append(DeadBody(v.location, v.species, v.size))
        print(f"코끼리가 {v.species}을(를) 짓밟았습니다.")


class Elephant(Animal):
    species = "elephant"
    color = (140, 130, 150)
    base_speed = 1.3
    size = 5.0
    detection_range = 6.0

    def build_behaviors(self) -> list:
        from dung_beetle import DungBeetle
        from rabbit import Rabbit

        return [
            ProduceDung(),
            SeekWater(),
            Trample(target_classes=[DungBeetle, Rabbit]),
            SeekPlantFood(),
            Breed(),
            Wander(),
        ]
