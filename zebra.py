"""담당: 윤준우"""

import random

from animal import Animal
from behaviors import ProduceDung, Flee, SeekWater, SeekPlantFood, Breed, Wander


class Zebra(Animal):
    species = "zebra"
    color = (225, 225, 230)
    base_speed = 2.5
    size = 2.0
    detection_range = 7.0
    flee_speed_mult = 1.3
    predators = ("lion", "hyena")

    def on_capture_attempt(self, predator, env) -> bool:
        # camouflage(passive): 줄무늬로 일정 확률로 포획을 회피한다.
        # 단, 사자의 ambush(은폐) 앞에서는 회피 확률이 크게 낮아진다.
        escape_chance = 0.3
        if predator.species == "lion":
            escape_chance *= (1.0 - getattr(predator, "stealth_rate", 0.0))
        if random.random() < escape_chance:
            print("얼룩말이 위장으로 공격을 피했습니다!")
            return False
        return True

    def build_behaviors(self) -> list:
        return [ProduceDung(), Flee(), SeekWater(), SeekPlantFood(), Breed(), Wander()]
