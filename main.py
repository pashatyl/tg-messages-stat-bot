import os

from app import App


def main():
    token = os.environ["TOKEN"]
    app = App(token)
    app.start()


if __name__ == "__main__":
    main()
