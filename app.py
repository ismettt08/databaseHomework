from src.server import create_app
import sys

if __name__ == "__main__":
    app = create_app()
    app.run()