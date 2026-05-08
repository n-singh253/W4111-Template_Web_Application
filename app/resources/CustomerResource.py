from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Customer(BaseModel):
    customerNumber: int | None = None
    customerName: str | None = None
    contactLastName: str | None = None
    contactFirstName: str | None = None
    phone: str | None = None
    addressLine1: str | None = None
    addressLine2: str | None = None
    city: str | None = None
    state: str | None = None
    postalCode: str | None = None
    country: str | None = None
    salesRepEmployeeNumber: int | None = None
    creditLimit: Decimal | None = None


class CustomerCollection(BaseModel):
    items: list[Customer] = Field(default_factory=list)


class CustomerResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        self._service = MySQLDataService(
            {
                **cfg,
                "table_name": cfg.get("table_name", "customers"),
                "primary_key_field": cfg.get("primary_key_field", "customerNumber"),
            }
        )

    def get(self, template: dict) -> CustomerCollection:
        rows = self._service.retrieveByTemplate(template)
        return CustomerCollection(items=[Customer.model_validate(row) for row in rows])

    def get_by_id(self, id: str) -> Customer:  # noqa: A002
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No customer with customerNumber {id!r}")
        return Customer.model_validate(row)

    def post(self, new_data: Customer) -> str:
        return self._service.create(new_data.model_dump(exclude_none=True))

    def delete(self, id: str) -> int:  # noqa: A002
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, customer_id: str, new_data: Customer) -> int:
        data = new_data.model_dump(exclude_unset=True)
        data["customerNumber"] = int(customer_id)
        return self._service.updateByPrimaryKey(customer_id, data)
