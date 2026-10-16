"""Seed script to load data/schemes.json into MongoDB schemes collection."""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pymongo
from pymongo.errors import PyMongoError

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


def main():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/scheme_finder")
    
    # Locate data/schemes.json
    candidates = [
        Path(__file__).resolve().parents[2] / "data" / "schemes.json",
        Path.cwd() / "data" / "schemes.json",
        Path.cwd().parent / "data" / "schemes.json",
    ]
    data_file = None
    for p in candidates:
        if p.exists():
            data_file = p
            break

    if not data_file or not data_file.exists():
        print(f"❌ Error: data/schemes.json not found in search paths: {[str(p) for p in candidates]}")
        sys.exit(1)

    print(f"📖 Reading scheme data from: {data_file}")
    with open(data_file, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    if not isinstance(schemes, list):
        print("❌ Error: schemes.json must contain a JSON array of scheme objects.")
        sys.exit(1)

    print(f"Loaded {len(schemes)} scheme definitions from file.")
    print(f"Connecting to MongoDB at: {mongo_uri} ...")

    try:
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        # Test connection
        client.admin.command("ping")
    except Exception as exc:
        print(f"❌ Could not connect to MongoDB: {exc}")
        print("💡 Hint: Ensure MongoDB is running locally (e.g., via Docker: 'docker run -d -p 27017:27017 mongo')")
        print("   or set MONGO_URI in .env to a MongoDB Atlas cluster URI.")
        sys.exit(1)

    # Determine database name
    try:
        db = client.get_default_database()
        if db is None:
            db = client["scheme_finder"]
    except Exception:
        db = client["scheme_finder"]

    schemes_coll = db["schemes"]
    
    # Ensure unique index on id
    schemes_coll.create_index([("id", pymongo.ASCENDING)], unique=True)

    upserted_count = 0
    for scheme in schemes:
        scheme_id = scheme.get("id")
        if not scheme_id:
            continue
        result = schemes_coll.update_one(
            {"id": scheme_id},
            {"$set": scheme},
            upsert=True,
        )
        upserted_count += 1
        action = "Created" if result.upserted_id else "Updated"
        print(f"  ✓ [{action}] {scheme_id} - {scheme.get('name')}")

    print(f"✅ Successfully seeded {upserted_count} schemes into MongoDB collection '{db.name}.schemes'!")


if __name__ == "__main__":
    main()
