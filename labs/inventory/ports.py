from typing import Protocol
from .domain import Reservation


class ReservationStore(Protocol):
    def reserve(self, reservation: Reservation) -> Reservation:
        """Atomically check idempotency, deduct stock and record reservation.

        Replaying the same request returns its reservation without deducting stock.
        Reusing an ID with different data raises InventoryError.
        Failure must leave both stock and reservations unchanged.
        """
        ...
