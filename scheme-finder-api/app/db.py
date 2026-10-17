"""Database connection and scheme retrieval with graceful JSON fallback."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import pymongo
from pymongo.errors import PyMongoError

logger = logging.getLogger("scheme_finder.db")

_client: Optional[pymongo.MongoClient] = None


def get_mongo_uri() -> str:
    """Get MongoDB connection URI from environment variable."""
    return os.getenv("MONGO_URI", "mongodb://localhost:27017/scheme_finder")


def get_schemes_file_path() -> Path:
    """Locate data/schemes.json file across execution directories."""
    here = Path(__file__).resolve()
    candidates = []
    data_dir_env = os.getenv("DATA_DIR")
    if data_dir_env:
        candidates.append(Path(data_dir_env) / "schemes.json")

    candidates.extend([
        here.parents[2] / "data" / "schemes.json" if len(here.parents) > 2 else here.parent / "data" / "schemes.json",
        here.parents[1] / "data" / "schemes.json" if len(here.parents) > 1 else here.parent / "data" / "schemes.json",
        Path.cwd() / "data" / "schemes.json",
        Path.cwd() / "scheme-finder" / "data" / "schemes.json",
        Path.cwd().parent / "data" / "schemes.json",
    ])
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]




def load_schemes_from_file() -> List[Dict[str, Any]]:
    """Load scheme records directly from data/schemes.json."""
    path = get_schemes_file_path()
    if not path.exists():
        logger.warning("schemes.json not found at %s", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Failed to load schemes from file %s: %s", path, exc)
        return []


def get_mongo_client() -> Optional[pymongo.MongoClient]:
    """Get or initialize MongoDB client with short timeout."""
    global _client
    if _client is not None:
        return _client

    uri = get_mongo_uri()
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=1200)
        # Test connection with a quick ping
        client.admin.command("ping")
        _client = client
        return _client
    except Exception as exc:
        logger.info("MongoDB not available (%s); falling back to file-backed scheme store.", exc)
        return None


def get_db():
    """Get MongoDB database object or None if unavailable."""
    client = get_mongo_client()
    if client is None:
        return None
    # Parse DB name from URI or default to 'scheme_finder'
    try:
        default_db = client.get_default_database()
        if default_db is not None:
            return default_db
    except Exception:
        pass
    return client["scheme_finder"]


def fetch_all_schemes() -> List[Dict[str, Any]]:
    """Fetch all schemes from MongoDB, falling back to data/schemes.json."""
    db = get_db()
    if db is not None:
        try:
            records = list(db["schemes"].find({}, {"_id": 0}))
            if records:
                return records
        except PyMongoError as err:
            logger.warning("MongoDB query failed (%s); using file fallback.", err)

    return load_schemes_from_file()


def fetch_scheme_by_id(scheme_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single scheme by its kebab-case ID."""
    db = get_db()
    if db is not None:
        try:
            record = db["schemes"].find_one({"id": scheme_id}, {"_id": 0})
            if record:
                return record
        except PyMongoError as err:
            logger.warning("MongoDB find_one failed (%s); using file fallback.", err)

    schemes = load_schemes_from_file()
    for s in schemes:
        if s.get("id") == scheme_id:
            return s
    return None
