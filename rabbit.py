"""담당: 노민준"""

from animal import Animal
from behaviors import ProduceDung, Flee, SeekWater, SeekPlantFood, Breed, Wander

JUMP_COOLDOWN = 3.0


class Rabbit(Animal):
    species = "rabbit"
    color = (235, 235, 240)
    base_speed = 2.2
    size = 0.4
    detection_range = 7.0
    flee_speed_mult = 1.6  # 도망칠 때 빠름

    def is_caught_by(self, predator, env) -> bool:
        # jump(skill): 쿨다운이 차면 점프로 포획/짓밟기를 회피한다.
        if self.skill_timer <= 0.0:
            self.skill_timer = JUMP_COOLDOWN
            self.step_away(predator.location, env, env._dt, 2.5)  # 크게 도약
            print("토끼가 점프하여 공격을 피했습니다!")
            return False
        return True

    def build_behaviors(self) -> list:
        from cheetah import Cheetah
        from eagle import Eagle
        from hyena import Hyena
        from lion import Lion
        from elephant import Elephant

        return [
            ProduceDung(),
            Flee(target_classes=[Cheetah, Eagle, Hyena, Lion, Elephant]),
            SeekWater(),
            SeekPlantFood(),
            Breed(),
            Wander(),
        ]
