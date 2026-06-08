"""담당: 윤준우"""

import config
from animal import Animal
from base import Behavior
from behaviors import ProduceDung, Hunt, SeekWater, Breed, Wander

ROAR_COOLDOWN = 10.0


class Roar(Behavior):
    """포효(skill): 주변 사냥감의 스태미나를 깎아 도주를 어렵게 만든다."""

    def __init__(self, target_classes):
        # 포효가 영향을 줄 사냥감 Animal 하위 클래스들 (isinstance용 튜플)
        self.target_classes = tuple(target_classes)

    def determine(self, e, env) -> bool:
        if e.skill_timer > 0.0:
            return False
        e._roar_targets = env.animals_near(
            e.location,
            e.detection_range,
            lambda a: isinstance(a, self.target_classes),
        )
        return len(e._roar_targets) > 0

    def act(self, e, env) -> None:
        e.skill_timer = ROAR_COOLDOWN
        for prey in e._roar_targets:
            prey.stamina *= 0.4
        print("사자가 포효하여 주변 동물들이 위축됩니다!")


class Lion(Animal):
    species = "lion"
    color = (200, 150, 70)
    base_speed = 2.4
    size = 3.0
    detection_range = 9.0
    stealth_rate = 0.9  # ambush: 은폐율 (사냥감 회피 확률을 낮춤)

    def build_behaviors(self) -> list:
        from zebra import Zebra
        from hyena import Hyena

        # 얼룩말 사냥 + 하이에나 추격
        return [
            ProduceDung(),
            SeekWater(),
            Hunt(target_classes=[Zebra, Hyena]),
            Roar(target_classes=[Zebra, Hyena]),
            Breed(),
            Wander(),
        ]
