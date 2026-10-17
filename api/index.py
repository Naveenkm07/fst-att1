"""Vercel Serverless Function entrypoint for FastAPI backend."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add scheme-finder-api to sys.path so app modules are resolvable
repo_root = Path(__file__).resolve().parent.parent
api_dir = repo_root / "scheme-finder-api"
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

# Ensure data directory is discoverable
os.environ.setdefault("DATA_DIR", str(repo_root / "data"))

# Load environment variables
for env_file in [repo_root / ".env", api_dir / ".env"]:
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)

from app.main import app

