import os

import dotenv


def load_env():
    """Get the path to the .env file and load it."""
    env_file = os.path.join(os.path.dirname(__file__), os.pardir, ".env")
    dotenv.read_dotenv(env_file)
