from .domain import Reservation
from .ports import ReservationStore


class ReserveStock:
    def __init__(self, store: ReservationStore):
        self.store = store

    def execute(self, request_id: str, sku: str, quantity: int) -> Reservation:
        return self.store.reserve(Reservation(request_id, sku, quantity))
