import argparse
import dataclasses
import subprocess
import sys
import time
from datetime import timedelta


ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_BLUE = "\033[94m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"


@dataclasses.dataclass
class TimerConfig:
    work_minutes: int = 90
    rest_minutes: int = 20
    cycles: int = 1
    demo: bool = False
    sound: bool = True
    notifications: bool = True


def format_duration(seconds: int) -> str:
    return str(timedelta(seconds=seconds))


def play_sound(sound_enabled: bool) -> None:
    if not sound_enabled:
        return

    sound_paths = [
        "/System/Library/Sounds/Glass.aiff",
        "/System/Library/Sounds/Pop.aiff",
        "/System/Library/Sounds/Submarine.aiff",
    ]

    for path in sound_paths:
        try:
            subprocess.run(["afplay", path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except FileNotFoundError:
            break
        except subprocess.CalledProcessError:
            continue

    # Fallback to terminal bell when afplay is not available.
    print("\a", end="", flush=True)


def send_notification(title: str, message: str, notifications_enabled: bool) -> None:
    if not notifications_enabled:
        return

    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Silently ignore when notifications are unavailable (non-macOS or restricted envs).
        return


def print_banner(title: str, accent_color: str) -> None:
    bar = f"{accent_color}{'=' * 50}{ANSI_RESET}"
    print(bar)
    print(f"{accent_color}{ANSI_BOLD}{title.center(50)}{ANSI_RESET}")
    print(bar)


def run_phase(name: str, seconds: int, config: TimerConfig) -> None:
    phase_color = ANSI_GREEN if name.lower() == "work" else ANSI_BLUE
    print_banner(f"{name} for {format_duration(seconds)}", phase_color)

    remaining = seconds
    last_line_length = 0

    while remaining >= 0:
        status_line = f"  Remaining: {format_duration(remaining)}"
        padding = " " * max(0, last_line_length - len(status_line))
        print(f"\r{phase_color}{status_line}{padding}{ANSI_RESET}", end="", flush=True)
        last_line_length = len(status_line)
        time.sleep(1)
        remaining -= 1

    print()  # Move to next line after countdown.
    print_banner(f"{name} session complete", ANSI_YELLOW)
    play_sound(config.sound)
    send_notification("90/20 Timer", f"{name} session complete", config.notifications)


def calculate_seconds(minutes: int, demo: bool) -> int:
    return minutes if demo else minutes * 60


def run_timer(config: TimerConfig) -> None:
    for cycle in range(1, config.cycles + 1):
        header = f"Cycle {cycle}/{config.cycles}"
        print_banner(header, ANSI_CYAN)

        run_phase("Work", calculate_seconds(config.work_minutes, config.demo), config)

        if cycle == config.cycles:
            print_banner("All cycles finished", ANSI_GREEN)
            break

        run_phase("Rest", calculate_seconds(config.rest_minutes, config.demo), config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple 90/20 (work/rest) timer for macOS")
    parser.add_argument("--work", type=int, default=90, help="Work duration in minutes (default: 90)")
    parser.add_argument("--rest", type=int, default=20, help="Rest duration in minutes (default: 20)")
    parser.add_argument("--cycles", type=int, default=1, help="Number of work/rest cycles to run")
    parser.add_argument("--demo", action="store_true", help="Treat duration values as seconds for quick demos")
    parser.add_argument("--no-sound", action="store_true", help="Disable completion sounds")
    parser.add_argument(
        "--no-notifications",
        action="store_true",
        help="Disable macOS notifications (osascript)",
    )
    return parser


def validate_config(config: TimerConfig) -> None:
    if config.work_minutes <= 0:
        raise ValueError("Work duration must be greater than zero")
    if config.rest_minutes < 0:
        raise ValueError("Rest duration cannot be negative")
    if config.cycles <= 0:
        raise ValueError("Cycles must be at least 1")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = TimerConfig(
        work_minutes=args.work,
        rest_minutes=args.rest,
        cycles=args.cycles,
        demo=args.demo,
        sound=not args.no_sound,
        notifications=not args.no_notifications,
    )

    try:
        validate_config(config)
    except ValueError as error:
        parser.error(str(error))

    try:
        run_timer(config)
    except KeyboardInterrupt:
        print("\nTimer interrupted. Bye!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
