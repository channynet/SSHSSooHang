"""시뮬레이션 전역 상수. 수치 세부조정은 이 파일에서 관리한다."""

# --- 월드 / 렌더 ---
GRID_W = 50  # 가로 타일 수
GRID_H = 34  # 세로 타일 수
TILE_PX = 22  # 타일 한 변의 픽셀 크기 (UI)
HUD_H = 90  # 화면 하단 HUD 높이 (픽셀)

# --- 생명 수치 (초당 변화량) ---
WATER_DECAY = 1.5  # body_water 매초 감소량
FULLNESS_DECAY = 1.0  # fullness 매초 감소량
STAMINA_REGEN = 12.0  # stamina 매초 회복량

# 섭취 시 회복량
DRINK_AMOUNT = 45.0  # 물 한 번 마실 때 body_water 회복
EAT_PLANT_AMOUNT = 35.0  # 식물 섭취 시 fullness 회복
MEAT_PER_SIZE = 60.0  # 사냥감 size 1당 얻는 fullness

# --- 행동 임계값 ---
THIRST_THRESHOLD = 0.45  # body_water 비율이 이 값 미만이면 물을 찾음
HUNGER_THRESHOLD = 0.55  # fullness 비율이 이 값 미만이면 먹이를 찾음
HUNT_FULLNESS_THRESHOLD = 0.82  # 포식자가 이 포만도 미만이면 사냥을 시작
BREED_THRESHOLD = 0.75  # 양쪽 모두 fullness 비율이 이 값 이상이어야 번식
CAPTURE_RADIUS = 0.7  # 포식자가 사냥감을 잡을 수 있는 거리(타일)
INTERACT_RADIUS = 0.9  # 일반 상호작용(탈취/짓밟기 등) 거리(타일)
BREED_RADIUS = 1.2  # 번식 가능 거리(타일)
BREED_COOLDOWN = 18.0  # 번식 후 재번식까지 대기(초)
HUNT_DETECTION_MULT = 1.2  # 사냥 시 기본 인지 범위 보정
HUNT_CHASE_SPEED_MULT = 1.12  # 사냥 중 추격 속도 보정
HUNT_LEAD_MULT = 0.45  # 도망가는 방향을 예측해서 앞질러 쫓는 정도
SPRINT_STAMINA_COST = 25.0  # 스킬 사용 시 초당 stamina 소모

# --- 타일 / 식물 / 물 ---
PLANT_MAX = 100.0
PLANT_REGEN = 4.0  # 식물 매초 재생량 (rainy면 RAIN_PLANT_BONUS 배)
RAIN_PLANT_BONUS = 2.0
WATER_TILE_MAX = 100.0
SUNNY_WATER_LOSS = 2.0  # sunny 날씨에서 물 타일 매초 감소
RAIN_WATER_GAIN = 5.0  # rainy 날씨에서 물 타일 매초 증가

# --- 날씨 ---
WEATHER_SWITCH_SEC = 20.0  # 날씨 전환 주기(초)

# --- 똥 / 사체 ---
DUNG_PRODUCE_SEC = 24.0  # 동물이 배설하는 주기(초)
DUNG_AMOUNT = 2.0  # 한 번 배설량
DUNG_BEETLE_COLLECT_AMOUNT = 4.0  # 쇠똥구리가 한 번에 모으는 최대 배설물 양
DUNG_BALL_EAT_SIZE = 4.0  # 쇠똥구리 공 크기가 이 값 이상이면 섭취
DEAD_BODY_DECAY = 30.0  # 사체 부패 시간(초)

# --- 루프 ---
MS_PER_FRAME = 16  # 목표 프레임 간격(ms) ≈ 60fps
