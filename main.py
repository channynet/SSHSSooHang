import config
import ui
from setup import build_env


def main() -> None:
    env = build_env()
    ui.init(env)

    running = True
    while running:
        env.update(config.MS_PER_FRAME)
        running = ui.draw(env)

    ui.finish(env)
    if env.collapsed:
        print(env.collapse_reason)


if __name__ == "__main__":
    main()
