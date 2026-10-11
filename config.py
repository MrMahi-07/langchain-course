from os import getenv as __getenv
from dotenv import load_dotenv as __load_env
from pathlib import Path

__load_env()


def get_env(name: str, default=None) -> str:
    value = __getenv(name, default)
    if not value:
        raise ValueError(f"Variable {name} not found.")

    return value


GOOGLE_PROJECT_NAME = get_env("GOOGLE_PROJECT_NAME")
PROJECT_ROOT_PATH = Path(get_env("PROJECT_ROOT", str(Path(__file__).resolve().parent)))
DATA_ROOT_PATH = PROJECT_ROOT_PATH / "data"
