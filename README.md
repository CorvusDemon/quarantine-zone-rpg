# Quarantine Zone

A 2D survival horror RPG built with pygame-ce.

> ⚠️ This is a **local pygame application**, not a Google Colab notebook.

---

## Installation & Running

### Option 1 — Run from source (requires Python 3.10+)

```
# 1. Open the quarantine_zone/ folder in terminal or editor

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Run the game
python main.py
```

### Option 2 — Build executable (no Python required to run)

```
# Build the .exe (requires Python + pip)
build.bat

# Then run
dist\QuarantineZone\QuarantineZone.exe
```

---

## Running Tests

```
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Data Validation

```
python validate_data.py
```

---

## Controls

### Exploration
| Key | Action |
|-----|--------|
| 1-9 | Move to location |
| Q-Y | Special action |
| S | Search (QTE) |
| I | Inventory |
| C | Crafting |
| N | Notes |
| M | Map |
| F5 | Quick Save |
| F9 | Quick Load |
| ESC | Pause |

### Battle
| Key | Action |
|-----|--------|
| 1 | Attack (QTE) |
| 2 | Use item |
| 3 | Mutation skill |
| 4 | Flee |
| SPACE | Stop QTE marker |
| 1/2/3 | Dodge / Block / Counter |

---

## Project Structure

```
quarantine_zone/
├── main.py
├── settings.py
├── requirements.txt
├── README.md
├── build.bat
├── validate_data.py
├── data/               JSON game data
├── assets/sounds/      OGG audio (optional)
├── src/
│   ├── game.py         Main controller
│   ├── player.py       Player model
│   ├── enemy.py        Enemy model
│   ├── save_manager.py Save/Load with validation
│   ├── sound_manager.py Audio
│   ├── screens/        UI renderers
│   └── systems/        Game logic
└── tests/              pytest test suite
```

---

## Known Limitations

- Fixed resolution 1280×720
- Sound files not bundled — runs silently without them
- Tested on Windows, Python 3.13 / 3.14, pygame-ce 2.5.7