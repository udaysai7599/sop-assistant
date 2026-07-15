import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs):
        return False


BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = BASE_DIR.parent
DEFAULT_SQLITE_PATH = WORKSPACE_ROOT / "instance" / "sop_db.sqlite"
DEFAULT_BACKEND_SQLITE_PATH = BASE_DIR / "instance" / "sop_db.sqlite"

# Load local environment overrides from a .env file when present.
load_dotenv(BASE_DIR / ".env")
load_dotenv(WORKSPACE_ROOT / ".env")


def get_database_uri():
    """Resolve the database URI from environment variables or local defaults."""
    configured_uri = os.getenv("DATABASE_URL")
    if configured_uri:
        return configured_uri

    if DEFAULT_SQLITE_PATH.exists():
        return f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

    DEFAULT_BACKEND_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_BACKEND_SQLITE_PATH.as_posix()}"


def get_jwt_secret_key():
    """Return the JWT signing secret from the environment."""
    return os.getenv("JWT_SECRET_KEY", "sop-assistant-super-secret-key-2026")


def get_admin_secret():
    """Return the admin bootstrap secret from the environment."""
    return os.getenv("ADMIN_SECRET", "change-me-in-production")


def get_flask_debug_mode():
    """Return whether Flask should run in debug mode."""
    return os.getenv("FLASK_DEBUG", "1") == "1"


def get_app_host():
    return os.getenv("APP_HOST", "0.0.0.0")


def get_app_port():
    return int(os.getenv("APP_PORT", "5000"))
