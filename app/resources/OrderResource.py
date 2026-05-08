from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Order(BaseModel):
    orderNumber: int | None = None
    orderDate: date | None = None
    requiredDate: date | None = None
    shippedDate: date | None = None
    status: str | None = None
    comments: str | None = None
    customerNumber: int | None = None


class OrderCollection(BaseModel):
    items: list[Order] = Field(default_factory=list)


class OrderResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(
            {
                **cfg,
                "table_name": cfg.get("table_name", "orders"),
                "primary_key_field": cfg.get("primary_key_field", "orderNumber"),
            }
        )

    def get(self, template: dict) -> OrderCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderCollection(items=[Order.model_validate(row) for row in rows])

    def get_by_id(self, id: str) -> Order:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No order with orderNumber {id!r}")
        return Order.model_validate(row)

    def post(self, new_data: Order) -> str:
        return self._service.create(new_data.model_dump(exclude_none=True))

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, order_id: str, new_data: Order) -> int:
        data = new_data.model_dump(exclude_unset=True)
        data["orderNumber"] = int(order_id)
        return self._service.updateByPrimaryKey(order_id, data)
