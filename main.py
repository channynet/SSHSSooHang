from env import Env
import ui
import time

MS_PER_FRAME = 10

if __name__ == "__main__":
    env = Env()
    while True:
        time.sleep(MS_PER_FRAME / 1_000_000)
        env.update(MS_PER_FRAME)
        ui.draw(env)
