# Elemental Tower

A tower defense game based on the five elements.

## Requirements

- Python 3.10+
- Pygame 2.5+

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/steph-koopmanschap/elemental_tower.git
cd tower-defense

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the game
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| `ESC` | Quit |

## Project Structure

```
tower_defense/
├── main.py          # Entry point
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   ├── images/
│   └── sounds/
└── src/
    ├── settings.py  # Constants (screen size, colors, grid)
    └── game.py      # Main Game class
```

## Roadmap

- [ ] Map / path system
- [ ] Enemy waves
- [ ] Tower placement
- [ ] Projectile system
- [ ] Score & lives UI