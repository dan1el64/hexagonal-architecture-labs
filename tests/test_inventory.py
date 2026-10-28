import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from labs.inventory.adapters import MemoryStore, SQLiteStore
from labs.inventory.application import ReserveStock
from labs.inventory.domain import InventoryError, InsufficientStock


class InventoryContracts(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryStore({"sensor": 5})
        self.sqlite = SQLiteStore(":memory:")
        self.sqlite.seed("sensor", 5)

    def tearDown(self):
        self.sqlite.close()

    def remaining(self, store):
        return store.stock["sensor"] if isinstance(store, MemoryStore) else store.remaining("sensor")

    def test_adapters_obey_idempotency_contract(self):
        for store in (self.memory, self.sqlite):
            with self.subTest(adapter=type(store).__name__):
                service = ReserveStock(store)
                first = service.execute("request-1", "sensor", 3)
                self.assertEqual(first, service.execute("request-1", "sensor", 3))
                self.assertEqual(2, self.remaining(store))

    def test_conflicting_replay_does_not_mutate_stock(self):
        for store in (self.memory, self.sqlite):
            service = ReserveStock(store)
            service.execute("request-1", "sensor", 2)
            with self.assertRaises(InventoryError):
                service.execute("request-1", "sensor", 1)
            self.assertEqual(3, self.remaining(store))

    def test_insufficient_stock_is_atomic_and_request_can_retry(self):
        for store in (self.memory, self.sqlite):
            service = ReserveStock(store)
            with self.assertRaises(InsufficientStock):
                service.execute("retry", "sensor", 6)
            self.assertEqual(5, self.remaining(store))
            service.execute("retry", "sensor", 1)
            self.assertEqual(4, self.remaining(store))

    def test_unknown_product_is_rejected(self):
        for store in (self.memory, self.sqlite):
            with self.assertRaises(InsufficientStock):
                ReserveStock(store).execute("unknown", "missing", 1)

    def test_invalid_quantity_is_rejected_before_storage(self):
        for quantity in (0, -1, True, 1.5):
            with self.subTest(quantity=quantity), self.assertRaises(InventoryError):
                ReserveStock(self.memory).execute("bad", "sensor", quantity)
        self.assertEqual(5, self.memory.stock["sensor"])

    def test_blank_identifiers_are_rejected(self):
        with self.assertRaises(InventoryError):
            ReserveStock(self.memory).execute(" ", "sensor", 1)

    def test_sqlite_persists_reservation_without_reseeding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "stock.db")
            store = SQLiteStore(path)
            store.seed("sensor", 5)
            ReserveStock(store).execute("persisted", "sensor", 2)
            store.close()
            store = SQLiteStore(path)
            try:
                store.seed("sensor", 5)
                ReserveStock(store).execute("persisted", "sensor", 2)
                self.assertEqual(3, store.remaining("sensor"))
            finally:
                store.close()

    def test_concurrent_sqlite_reservations_cannot_oversell(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "stock.db")
            store = SQLiteStore(path)
            store.seed("sensor", 1)
            store.close()

            def reserve(request_id):
                worker = SQLiteStore(path)
                try:
                    ReserveStock(worker).execute(request_id, "sensor", 1)
                    return True
                except InsufficientStock:
                    return False
                finally:
                    worker.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(reserve, ["a", "b"]))
            self.assertEqual(1, sum(results))
