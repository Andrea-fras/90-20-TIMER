# 90/20 Timer (macOS-friendly)

A simple terminal timer for 90-minute work sessions followed by 20-minute rest breaks. It plays clear sounds using macOS `afplay` and shows colorful banners when a session ends.

## Requirements
- Python 3.10+
- macOS for sounds/notifications (other platforms fall back to a terminal bell and text banners)

## Usage
```bash
python timer.py
```
This runs one 90-minute work session and stops. Use the flags below to customize your routine.

### Common options
- `--cycles N` – Number of work/rest cycles to run.
- `--work MINUTES` – Work duration in minutes (default: 90).
- `--rest MINUTES` – Rest duration in minutes (default: 20).
- `--demo` – Treat the durations as seconds for quick testing.
- `--no-sound` – Turn off completion sounds.
- `--no-notifications` – Disable macOS notifications.

### Examples
Run the classic 90/20 split for three cycles:
```bash
python timer.py --cycles 3
```
Quickly preview the alerts (90 seconds work, 20 seconds rest):
```bash
python timer.py --demo
```
Use shorter 50/10 sprints with two cycles and no sounds:
```bash
python timer.py --work 50 --rest 10 --cycles 2 --no-sound
```

## How it alerts you
- **Sound:** Attempts to play built-in macOS sounds with `afplay`, falling back to a terminal bell when unavailable.
- **Visuals:** Colorful terminal banners clearly show when a session starts and completes.
- **Notifications:** Uses `osascript` to trigger a native macOS notification when available.

## Interrupting
Press `Ctrl+C` at any time to exit the timer early.
