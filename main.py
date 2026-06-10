import config
import ui
from setup import build_env


def main() -> None:
    env = build_env()
    ui.init(env)

    running = True
    paused = True
    while running:
        running, paused = ui.draw(env, paused)
        if running and not paused:
            env.update(config.MS_PER_FRAME)

    ui.finish(env, keep_open=env.collapsed)
    if env.collapsed:
        print(env.collapse_reason)


if __name__ == "__main__":
    main()
