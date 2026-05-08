from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class OrderDetails(BaseModel):
    orderNumber: int | None = None
    productCode: str | None = None
    quantityOrdered: int | None = None
    priceEach: Decimal | None = None
    orderLineNumber: int | None = None


class OrderDetailsCollection(BaseModel):
    items: list[OrderDetails] = Field(default_factory=list)


class OrderDetailsResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(
            {
                **cfg,
                "table_name": cfg.get("table_name", "orderdetails"),
                "primary_key_fields": cfg.get(
                    "primary_key_fields", ["orderNumber", "productCode"]
                ),
            }
        )

    def _primary_key(self, order_number: str, product_code: str) -> str:
        return f"{order_number}:{product_code}"

    def get(self, template: dict) -> OrderDetailsCollection:
        rows = self._service.retrieveByTemplate(template)
        return OrderDetailsCollection(
            items=[OrderDetails.model_validate(row) for row in rows]
        )

    def get_by_id(self, id: str) -> OrderDetails:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No order detail with key {id!r}")
        return OrderDetails.model_validate(row)

    def get_by_order_and_product(
        self, order_number: str, product_code: str
    ) -> OrderDetails:
        return self.get_by_id(self._primary_key(order_number, product_code))

    def post(self, new_data: OrderDetails) -> str:
        return self._service.create(new_data.model_dump(exclude_none=True))

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))

    def delete_by_order_and_product(self, order_number: str, product_code: str) -> int:
        return self.delete(self._primary_key(order_number, product_code))

    def put(self, detail_id: str, new_data: OrderDetails) -> int:
        data = new_data.model_dump(exclude_unset=True)
        order_number, product_code = str(detail_id).split(":", 1)
        data["orderNumber"] = int(order_number)
        data["productCode"] = product_code
        return self._service.updateByPrimaryKey(detail_id, data)

    def put_by_order_and_product(
        self, order_number: str, product_code: str, new_data: OrderDetails
    ) -> int:
        return self.put(self._primary_key(order_number, product_code), new_data)
