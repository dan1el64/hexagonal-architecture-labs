import argparse
import json
from dataclasses import asdict
from .adapters import MemoryStore, SQLiteStore
from .application import ReserveStock
from .domain import InventoryError


def main():
    parser = argparse.ArgumentParser(description="Reserve synthetic inventory using a replaceable adapter")
    parser.add_argument("--adapter", choices=("memory", "sqlite"), default="memory")
    parser.add_argument("--database", default="inventory.sqlite3")
    parser.add_argument("--request-id", default="demo-001")
    parser.add_argument("--quantity", type=int, default=2)
    args = parser.parse_args()
    store = SQLiteStore(args.database) if args.adapter == "sqlite" else MemoryStore({"SENSOR-01": 10})
    try:
        if isinstance(store, SQLiteStore):
            store.seed("SENSOR-01", 10)
        result = ReserveStock(store).execute(args.request_id, "SENSOR-01", args.quantity)
        remaining = store.remaining("SENSOR-01") if isinstance(store, SQLiteStore) else store.stock["SENSOR-01"]
        print(json.dumps({"reservation": asdict(result), "remaining": remaining}, sort_keys=True))
    except InventoryError as error:
        parser.exit(2, f"reservation rejected: {error}\n")
    finally:
        if isinstance(store, SQLiteStore):
            store.close()


if __name__ == "__main__":
    main()
