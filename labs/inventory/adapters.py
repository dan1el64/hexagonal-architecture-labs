import sqlite3
from threading import Lock
from .domain import InventoryError, InsufficientStock, Reservation


class MemoryStore:
    def __init__(self, stock: dict[str, int]):
        if any(type(q) is not int or q < 0 for q in stock.values()):
            raise InventoryError("stock must be non-negative integers")
        self.stock = dict(stock)
        self.reservations: dict[str, Reservation] = {}
        self._lock = Lock()

    def reserve(self, reservation: Reservation) -> Reservation:
        with self._lock:
            previous = self.reservations.get(reservation.request_id)
            if previous is not None:
                if previous != reservation:
                    raise InventoryError("request_id already used with different data")
                return previous
            if self.stock.get(reservation.sku, 0) < reservation.quantity:
                raise InsufficientStock(reservation.sku)
            self.stock[reservation.sku] -= reservation.quantity
            self.reservations[reservation.request_id] = reservation
            return reservation


class SQLiteStore:
    """A connection belongs to its creating thread. Use one store per worker."""

    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS stock (
                sku TEXT PRIMARY KEY, quantity INTEGER NOT NULL CHECK(quantity >= 0)
            );
            CREATE TABLE IF NOT EXISTS reservations (
                request_id TEXT PRIMARY KEY, sku TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0)
            );
        """)

    def seed(self, sku: str, quantity: int):
        if type(quantity) is not int or quantity < 0:
            raise InventoryError("stock must be a non-negative integer")
        # Initialization is deliberately insert-only: a repeated CLI invocation
        # must not replenish inventory that has already been reserved.
        self.connection.execute("INSERT OR IGNORE INTO stock VALUES (?, ?)", (sku, quantity))

    def reserve(self, reservation: Reservation) -> Reservation:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT request_id, sku, quantity FROM reservations WHERE request_id = ?",
                (reservation.request_id,),
            ).fetchone()
            if row:
                previous = Reservation(*row)
                if previous != reservation:
                    raise InventoryError("request_id already used with different data")
                self.connection.commit()
                return previous
            cursor = self.connection.execute(
                "UPDATE stock SET quantity = quantity - ? WHERE sku = ? AND quantity >= ?",
                (reservation.quantity, reservation.sku, reservation.quantity),
            )
            if cursor.rowcount != 1:
                raise InsufficientStock(reservation.sku)
            self.connection.execute(
                "INSERT INTO reservations VALUES (?, ?, ?)",
                (reservation.request_id, reservation.sku, reservation.quantity),
            )
            self.connection.commit()
            return reservation
        except Exception:
            self.connection.rollback()
            raise

    def remaining(self, sku: str) -> int:
        row = self.connection.execute("SELECT quantity FROM stock WHERE sku = ?", (sku,)).fetchone()
        return row[0] if row else 0

    def close(self):
        self.connection.close()
