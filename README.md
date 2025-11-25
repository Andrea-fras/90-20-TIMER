# 90/20 Timer (macOS-friendly)

Choose between a quick terminal timer or a clean desktop app for 90-minute work sessions followed by 20-minute rest breaks. The desktop app provides big visuals, color cues, and optional sounds/notifications so you can launch it straight from Finder.

## Desktop app
```bash
python desktop_timer.py
```

**Controls**
- Start/Pause and Reset buttons
- Work, Rest, and Cycle inputs (defaults: 90/20, 1 cycle)
- Demo toggle (treats values as seconds for quick previews)

**Visual cues**
- Large countdown clock and progress bar
- Color changes for work (green), rest (blue), and finished (purple)
- macOS sounds (`afplay`) and notifications (`osascript`) when available

Tips: On macOS you can save a shortcut that runs `python desktop_timer.py` or create an Automator app to launch it from your dock.

## Terminal timer
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
- **Visuals:** Colorful terminal banners or desktop colors clearly show when a session starts and completes.
- **Notifications:** Uses `osascript` to trigger a native macOS notification when available.

## Interrupting
Press `Ctrl+C` at any time to exit the terminal timer early.
