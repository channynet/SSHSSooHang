import random

import config
from base import Entity
from geo import Point


class Animal(Entity):
    """모든 동물의 공통 부모. 속성과 기본 동작(이동/섭취/번식/사망)을 제공한다.

    '언제 무엇을 할지'에 대한 복잡한 판단은 Behavior가 담당하고,
    여기서는 그 판단이 호출하는 저수준 동작만 구현한다 (하이브리드 구조).
    """

    # --- 종별 기본값 (서브클래스에서 재정의) ---
    species = "animal"
    color = (220, 220, 220)
    diet = "herbivore"          # herbivore / carnivore / scavenger / detritivore
    base_speed = 2.0            # 이동 속도 (타일/초)
    size = 1.0                  # 몸집 (사냥 시 영양가, 충돌 판정)
    detection_range = 6.0       # 주변 인지 범위 (타일)
    fly = False                 # 비행 가능 여부
    prey = ()                   # 사냥 대상 종 이름들
    predators = ()              # 두려워하는 포식자 종 이름들
    max_body_water = 100.0
    max_fullness = 100.0
    max_stamina = 100.0

    def __init__(self, location: Point, gender: str | None = None):
        self.location = location
        self.gender = gender if gender in ("M", "F") else random.choice(("M", "F"))
        self.body_water = self.max_body_water
        self.fullness = self.max_fullness
        self.stamina = self.max_stamina
        self.age = 0.0
        self.alive = True
        self.is_flying = False
        self.breed_cooldown = 0.0
        self.dung_timer = random.uniform(0.0, config.DUNG_PRODUCE_SEC)
        self.skill_timer = 0.0      # 스킬 쿨다운 등 종별 용도
        self.food_store = 0.0       # 비축 식량 (cheetah/lion → hyena가 탈취)
        self._behaviors = self.build_behaviors()

    # --- 서브클래스가 행동 목록을 구성 ---
    def build_behaviors(self) -> list:
        return []

    def behaviors(self) -> list:
        return self._behaviors

    # --- 매 프레임 생리 변화 ---
    def tick(self, dt_sec: float) -> None:
        self.age += dt_sec
        self.body_water -= config.WATER_DECAY * dt_sec
        self.fullness -= config.FULLNESS_DECAY * dt_sec
        self.stamina = min(self.max_stamina, self.stamina + config.STAMINA_REGEN * dt_sec)
        self.breed_cooldown = max(0.0, self.breed_cooldown - dt_sec)
        self.dung_timer += dt_sec
        if self.skill_timer > 0.0:
            self.skill_timer = max(0.0, self.skill_timer - dt_sec)
        if self.body_water <= 0.0 or self.fullness <= 0.0:
            self.alive = False

    # --- 비율 헬퍼 ---
    @property
    def thirst_ratio(self) -> float:
        return self.body_water / self.max_body_water

    @property
    def hunger_ratio(self) -> float:
        return self.fullness / self.max_fullness

    # --- 기본 동작 ---
    def step_toward(self, target: Point, env, dt_sec: float, speed_mult: float = 1.0) -> None:
        direction = target - self.location
        if direction.length() < 1e-6:
            return
        self._move(direction, env, dt_sec, speed_mult)

    def step_away(self, threat: Point, env, dt_sec: float, speed_mult: float = 1.0) -> None:
        direction = self.location - threat
        if direction.length() < 1e-6:
            direction = Point(random.uniform(-1, 1), random.uniform(-1, 1)) - Point(0, 0)
        self._move(direction, env, dt_sec, speed_mult)

    def _move(self, direction, env, dt_sec: float, speed_mult: float) -> None:
        step = direction.normalized() * (self.base_speed * speed_mult * dt_sec)
        new_loc = self.location + step
        self.location = env.clamp(new_loc)
        env.entity_loc[self] = self.location

    def drink(self, tile) -> None:
        if tile.has_water():
            taken = min(config.DRINK_AMOUNT, tile.water)
            tile.water -= taken
            self.body_water = min(self.max_body_water, self.body_water + config.DRINK_AMOUNT)

    def eat_plant(self, tile) -> None:
        if tile.has_food():
            taken = min(config.EAT_PLANT_AMOUNT, tile.plant)
            tile.plant -= taken
            self.fullness = min(self.max_fullness, self.fullness + taken)

    def eat_prey(self, prey: "Animal") -> None:
        gain = config.MEAT_PER_SIZE * prey.size
        before = self.fullness
        self.fullness = min(self.max_fullness, self.fullness + gain)
        self.body_water = min(self.max_body_water, self.body_water + gain * 0.3)
        # 다 못 먹은 잉여는 비축한다 (store_food).
        leftover = gain - (self.fullness - before)
        if leftover > 0:
            self.store_food(leftover)
        prey.alive = False

    def store_food(self, amount: float) -> None:
        self.food_store += amount

    def on_capture_attempt(self, predator: "Animal", env) -> bool:
        """포식자가 잡으려 할 때 회피 여부. True면 포획 성공. 종별로 재정의."""
        return True

    def produce_dung(self, env) -> None:
        self.dung_timer = 0.0
        tile = env.tile_at(self.location)
        tile.dung += config.DUNG_AMOUNT

    def can_breed(self) -> bool:
        return self.alive and self.breed_cooldown <= 0.0 and self.hunger_ratio >= config.BREED_THRESHOLD

    def breed_with(self, other: "Animal", env) -> None:
        self.breed_cooldown = config.BREED_COOLDOWN
        other.breed_cooldown = config.BREED_COOLDOWN
        self.fullness *= 0.6
        other.fullness *= 0.6
        offset = Point(random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8)) - Point(0, 0)
        child = type(self)(env.clamp(self.location + offset))
        env.spawn(child)
