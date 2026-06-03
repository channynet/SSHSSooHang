"""담당: 김민찬D"""

import config
from animal import Animal
from base import Behavior
from behaviors import ProduceDung, SeekWater, SeekPlantFood, Breed, Wander
from dead_body import DeadBody


class Trample(Behavior):
    """passive: 발밑에 들어온 쇠똥구리/토끼를 짓밟는다 (토끼는 jump로 회피 가능)."""

    def determine(self, e, env) -> bool:
        victim = env.nearest_animal(
            e.location, config.INTERACT_RADIUS,
            lambda a: a.species in ("dung_beetle", "rabbit"),
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
    diet = "herbivore"
    base_speed = 1.3
    size = 5.0
    detection_range = 6.0

    def build_behaviors(self) -> list:
        return [ProduceDung(), SeekWater(), Trample(), SeekPlantFood(), Breed(), Wander()]
