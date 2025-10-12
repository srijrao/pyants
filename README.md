# Pyants

**Pyants** is an interactive ant colony simulation written in Python, featuring real-time graphics and a variety of controls to explore emergent behavior in ant colonies. The simulation models ants, anthills, food sources, and pheromone trails, allowing users to observe and manipulate the colony dynamics.

## Features

- Real-time graphical simulation using pygame
- Entities: ants, anthills, food, pheromone dots (trails)
- Interactive controls to add/remove entities, pause, reset, and toggle debug/visualization modes
- Customizable simulation parameters via `settings.json` or `settings.py`
- Debug mode for additional information and visualization

## Requirements

- Python 3.7+
- [pygame](https://www.pygame.org/) (`pip install pygame-ce`)

## Installation

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install pygame
   ```

## Usage

Run the simulation with:
```bash
python main.py
```
A window will open displaying the ant colony simulation. The simulation continues until you close the window or press the 'q' key.

## Controls

- **q**: Quit simulation
- **s**: Reduce pheromone dots (simulate evaporation)
- **a**: Add a new anthill
- **f**: Add a new food source
- **r**: Reset simulation
- **k**: Reduce ant population
- **p**: Pause/unpause simulation
- **d**: Toggle debug mode
- **SPACE**: Create new ants at anthill(s)
- **c**: Toggle pheromone dot visibility
- **UP arrow**: Add an ant at the first anthill

## Customization

Simulation parameters (window size, population, colors, etc.) can be adjusted in `settings.json` (created automatically) or by editing `settings.py` for defaults.

## Project Structure

- `main.py`: Entry point for the simulation
- `game_state.py`: Main game loop and state management
- `ants.py`, `antcolony.py`: Ant and colony logic
- `food.py`, `dots.py`: Food and pheromone dot logic
- `graphics.py`: Rendering and drawing
- `input_handler.py`: Keyboard controls
- `settings.py`: Default simulation settings
- `entity_manager.py`, `spatial_grid.py`: Entity management and spatial partitioning

## License

[Specify your license here, e.g., MIT, GPL, etc.]
