import config


class Weather:
    """날씨 상태. sunny면 물 타일을 마르게 하고, rainy면 물을 채운다."""

    SUNNY = "sunny"
    RAINY = "rainy"

    def __init__(self, state: str = SUNNY):
        self.state = state
        self._timer = 0.0

    @property
    def is_rainy(self) -> bool:
        return self.state == Weather.RAINY

    def set_sunny(self) -> None:
        self.state = Weather.SUNNY

    def set_rainy(self) -> None:
        self.state = Weather.RAINY

    def update(self, env, dt_sec: float) -> None:
        # 주기마다 날씨 전환
        self._timer += dt_sec
        if self._timer >= config.WEATHER_SWITCH_SEC:
            self._timer = 0.0
            self.set_sunny() if self.is_rainy else self.set_rainy()

        # 물 타일에 날씨 효과 적용
        for tile in env.water_tiles:
            if self.is_rainy:
                tile.increase_water(dt_sec)
            else:
                tile.decrease_water(dt_sec)
