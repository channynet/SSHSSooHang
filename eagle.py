"""담당: 김민찬D"""

from animal import Animal
from behaviors import ProduceDung, Hunt, SeekWater, Breed, Wander


class Eagle(Animal):
    species = "eagle"
    color = (90, 70, 50)
    diet = "carnivore"
    base_speed = 3.6        # 비행: 타일 간 빠르게 이동
    size = 1.0
    detection_range = 10.0  # 비행 중 넓은 시야
    fly = True
    prey = ("rabbit",)

    def __init__(self, location, gender=None):
        super().__init__(location, gender)
        # 비행 상태에서는 다른 동물과의 상호작용(피식)을 피한다.
        self.is_flying = True

    def hunt_speed_mult(self, target, env) -> float:
        # dive_attack: 급강하 추격 속도
        return 1.8

    def build_behaviors(self) -> list:
        return [ProduceDung(), SeekWater(), Hunt(), Breed(), Wander()]
