import environ
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env_path = BASE_DIR / '.env'
print(f"Looking for .env at: {env_path}")
if env_path.exists():
    print(".env file exists!")
    env.read_env(env_path)
else:
    print(".env file NOT found!")
print('DB_NAME:', env('DB_NAME', default='NOT_FOUND'))
print('DB_HOST:', env('DB_HOST', default='NOT_FOUND'))