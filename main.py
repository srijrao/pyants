"""
Main Module for Ant Colony Simulation

This module serves as the entry point for the ant colony simulation.
It initializes and runs the main game loop by creating an instance
of the Game class from the game_state module.

Example:
    To run the simulation:
    
    $ python main.py

The simulation will continue until the user closes the window or
presses the 'q' key to quit.
"""

from game_state import Game

def main():
    """
    Initialize and run the ant colony simulation.

    Creates an instance of the Game class and starts the main simulation loop.
    The simulation will continue running until the user explicitly exits
    (by closing the window or pressing 'q').
    """
    Game(debug=True).run()

if __name__ == "__main__":
    main()
