# 🧟 Quarantine Zone

**2D Text-Based Survival RPG** built with **pygame-ce**

A tense post-apocalyptic survival game where you wake up in an abandoned police station during a deadly outbreak. Explore, fight infected, craft items, manage infection, and try to reach the evacuation point.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-000000?style=for-the-badge&logo=pygame&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)

## ✨ Features

- **QTE-based combat system** with different enemy attack patterns
- **Progressive infection mechanic** — every decision matters
- **Deep crafting system** with unlockable recipes
- **Rich story** told through collectible notes
- **Interactive map** with progress tracking
- **Save/Load system** (2 slots + quick save)
- **Mutation skills** that use infection as a resource
- **Search mini-game** with QTE
- **Polished UI** with panels, colors, and visual feedback

## 🎮 Screenshots

## Main Menu
<img width="1588" height="893" alt="1" src="https://github.com/user-attachments/assets/efd2ad17-98b4-4ee1-8065-cf23b0c604c5" />

## Exploration
<img width="1587" height="895" alt="2" src="https://github.com/user-attachments/assets/b12903f4-26ac-41c8-ad30-7d0a3b743222" />

## QTE while search and Fights
<img width="1200" height="675" alt="Дизайн без названия" src="https://github.com/user-attachments/assets/7ca5e5e3-c74e-47df-b9e4-fdcbe0dff741" />

## Fight menu
<img width="1597" height="882" alt="3" src="https://github.com/user-attachments/assets/819c074f-c704-4e07-9abf-94ed95b27a26" />

## Battle Log
<img width="1576" height="888" alt="4" src="https://github.com/user-attachments/assets/02f982f7-b529-49d6-ba2c-5cf2c739ab42" />

## Map
<img width="1597" height="896" alt="5" src="https://github.com/user-attachments/assets/efaac224-9990-48cb-896f-bc36dccf9ab1" />

## Crafting Menu
<img width="1596" height="886" alt="6" src="https://github.com/user-attachments/assets/a46548f3-315d-40da-b4d3-fc44624e4dda" />

## Inventory
<img width="1600" height="895" alt="7" src="https://github.com/user-attachments/assets/218b03f2-9bdb-4730-9651-410a02380e9e" />


## 🚀 Quick Start

### Option 1: Run from source

```bash
git clone https://github.com/CorvusDemon/quarantine-zone.git
cd quarantine-zone

# Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Option 2: Build executable (Windows)

Run `build.bat` — it will create a standalone `.exe` in the `dist/` folder.

## 🎯 Controls

### Exploration
- **1-9** — Move to location
- **Q-Y** — Special actions
- **S** — Search location (QTE)
- **I** — Inventory
- **C** — Crafting
- **N** — Notes
- **M** — Map
- **F5** — Quick Save
- **F9** — Quick Load
- **ESC** — Pause

### Combat
- **1** — Attack (QTE)
- **2** — Use item
- **3** — Mutation skills
- **4** — Flee
- **SPACE** — Stop QTE marker
- **1/2/3** — Dodge / Block / Counter

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Engine**: pygame-ce 2.5.7
- **Data**: JSON (locations, items, enemies, recipes, notes)
- **Architecture**: Clean modular structure with systems, screens, and models
- **Testing**: pytest + data validation

## 📁 Project Structure

```bash
quarantine-zone/
├── main.py
├── settings.py
├── requirements.txt
├── build.bat
├── validate_data.py
├── data/                  # All game content (JSON)
├── assets/
│   └── sounds/            # Optional audio
├── src/
│   ├── game.py
│   ├── player.py
│   ├── enemy.py
│   ├── screens/
│   └── systems/
├── tests/                 # pytest suite
└── README.md
```

## 🎓  Highlights

This project demonstrates:
- Complex game state management
- QTE (Quick Time Event) mechanics
- Data-driven design using JSON
- Modular architecture and separation of concerns
- Player progression, crafting, and resource management
- Save system with validation
- Clean, maintainable code with tests
