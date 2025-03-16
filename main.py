import environment

def main():
    environment.Game().run()

if __name__ == "__main__":
    main()
# The main function is the entry point of the program. It creates an instance of the Game class from environment.py and starts the game loop by calling the run method. The game loop will continue running until the running attribute of the Game instance is set to False, which happens when the user closes the window by clicking the close button.