from src.server import create_app
import sys

app = create_app()

if __name__ == "__main__":
    app.run()