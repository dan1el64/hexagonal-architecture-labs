from dataclasses import dataclass


class InventoryError(ValueError):
    pass


class InsufficientStock(InventoryError):
    pass


@dataclass(frozen=True)
class Reservation:
    request_id: str
    sku: str
    quantity: int

    def __post_init__(self):
        if not self.request_id.strip() or not self.sku.strip():
            raise InventoryError("request_id and sku are required")
        if type(self.quantity) is not int or self.quantity <= 0:
            raise InventoryError("quantity must be a positive integer")
