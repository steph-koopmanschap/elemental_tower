from src.game import Game


def main():
    game = Game()
    try:
        game.run()
    finally:
        game.quit()


if __name__ == "__main__":
    main()
