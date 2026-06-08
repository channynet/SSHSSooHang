"""담당: 노민준"""

import config
from animal import Animal
from behaviors import ProduceDung, Hunt, SeekWater, Breed, Wander


class Cheetah(Animal):
    species = "cheetah"
    color = (210, 170, 60)
    base_speed = 2.6
    size = 1.2
    detection_range = 8.0

    def hunt_speed_mult(self, target, env) -> float:
        # sprint(skill): 스태미나가 있는 동안 속도 폭증, 소진되면 추격 실패
        if self.stamina > 15.0:
            self.stamina = max(0.0, self.stamina - config.SPRINT_STAMINA_COST * env._dt)
            return 2.5
        return 0.8

    def build_behaviors(self) -> list:
        from rabbit import Rabbit

        return [
            ProduceDung(),
            SeekWater(),
            Hunt(target_classes=[Rabbit]),
            Breed(),
            Wander(),
        ]
