from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

if __package__ in (None, ""):
    # Supports running this file directly (e.g., PyCharm "main.py" debug config).
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from app.resources.CustomerResource import Customer, CustomerCollection, CustomerResource
    from app.resources.OrderDetailsResource import (
        OrderDetails,
        OrderDetailsCollection,
        OrderDetailsResource,
    )
    from app.resources.OrderResource import Order, OrderCollection, OrderResource
else:
    from .resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from .resources.CustomerResource import Customer, CustomerCollection, CustomerResource
    from .resources.OrderDetailsResource import (
        OrderDetails,
        OrderDetailsCollection,
        OrderDetailsResource,
    )
    from .resources.OrderResource import Order, OrderCollection, OrderResource


def _get_app_name() -> str:
    # Keep settings minimal in this starter; use environment variables when needed.
    return os.getenv("APP_NAME", "Starter FastAPI App")


app = FastAPI(title=_get_app_name(), version="0.1.0")
harry_potter_resource = HarryPotterResource()
customer_resource = CustomerResource()
order_resource = OrderResource()
order_details_resource = OrderDetailsResource()


class EchoRequest(BaseModel):
    message: str


def _template_from_params(**params) -> dict:
    return {key: value for key, value in params.items() if value is not None}


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/echo", tags=["echo"])
def echo(payload: EchoRequest) -> EchoRequest:
    return payload


@app.get("/harry-potter", tags=["harry-potter"])
def get_harry_potter_characters(
    first_name: str | None = None,
    last_name: str | None = None,
    house_name: str | None = None,
) -> HarryPotterCollection:
    template: dict = {}
    if first_name is not None:
        template["first_name"] = first_name
    if last_name is not None:
        template["last_name"] = last_name
    if house_name is not None:
        template["house_name"] = house_name
    return harry_potter_resource.get(template)


@app.get("/harry-potter/{character_id}", tags=["harry-potter"])
def get_harry_potter_character_by_id(character_id: str) -> HarryPotterCharacter:
    try:
        return harry_potter_resource.get_by_id(character_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/harry-potter", tags=["harry-potter"])
def create_harry_potter_character(new_data: HarryPotterCharacter) -> str:
    new_id = harry_potter_resource.post(new_data)
    return str(new_id)


@app.put("/harry-potter/{character_id}", tags=["harry-potter"])
def update_harry_potter_character(
    character_id: str, new_data: HarryPotterCharacter
) -> dict[str, int]:
    try:
        updated = harry_potter_resource.put(character_id, new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"updated": updated}


@app.delete("/harry-potter/{character_id}", tags=["harry-potter"])
def delete_harry_potter_character(character_id: str) -> dict[str, int]:
    deleted = harry_potter_resource.delete(character_id)
    return {"deleted": deleted}


@app.get("/customers", tags=["customers"])
def get_customers(
    customerNumber: int | None = None,
    customerName: str | None = None,
    contactLastName: str | None = None,
    contactFirstName: str | None = None,
    phone: str | None = None,
    addressLine1: str | None = None,
    addressLine2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postalCode: str | None = None,
    country: str | None = None,
    salesRepEmployeeNumber: int | None = None,
    creditLimit: Decimal | None = None,
) -> CustomerCollection:
    return customer_resource.get(
        _template_from_params(
            customerNumber=customerNumber,
            customerName=customerName,
            contactLastName=contactLastName,
            contactFirstName=contactFirstName,
            phone=phone,
            addressLine1=addressLine1,
            addressLine2=addressLine2,
            city=city,
            state=state,
            postalCode=postalCode,
            country=country,
            salesRepEmployeeNumber=salesRepEmployeeNumber,
            creditLimit=creditLimit,
        )
    )


@app.get("/customers/{customerNumber}", tags=["customers"])
def get_customer_by_id(customerNumber: int) -> Customer:
    try:
        return customer_resource.get_by_id(str(customerNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/customers", tags=["customers"])
def create_customer(new_data: Customer) -> str:
    try:
        return str(customer_resource.post(new_data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/customers/{customerNumber}", tags=["customers"])
def update_customer(customerNumber: int, new_data: Customer) -> dict[str, int]:
    try:
        updated = customer_resource.put(str(customerNumber), new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"updated": updated}


@app.delete("/customers/{customerNumber}", tags=["customers"])
def delete_customer(customerNumber: int) -> dict[str, int]:
    deleted = customer_resource.delete(str(customerNumber))
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"deleted": deleted}


@app.get("/orders", tags=["orders"])
def get_orders(
    orderNumber: int | None = None,
    orderDate: date | None = None,
    requiredDate: date | None = None,
    shippedDate: date | None = None,
    status: str | None = None,
    comments: str | None = None,
    customerNumber: int | None = None,
) -> OrderCollection:
    return order_resource.get(
        _template_from_params(
            orderNumber=orderNumber,
            orderDate=orderDate,
            requiredDate=requiredDate,
            shippedDate=shippedDate,
            status=status,
            comments=comments,
            customerNumber=customerNumber,
        )
    )


@app.get("/orders/{orderNumber}", tags=["orders"])
def get_order_by_id(orderNumber: int) -> Order:
    try:
        return order_resource.get_by_id(str(orderNumber))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/orders", tags=["orders"])
def create_order(new_data: Order) -> str:
    try:
        return str(order_resource.post(new_data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}", tags=["orders"])
def update_order(orderNumber: int, new_data: Order) -> dict[str, int]:
    try:
        updated = order_resource.put(str(orderNumber), new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"updated": updated}


@app.delete("/orders/{orderNumber}", tags=["orders"])
def delete_order(orderNumber: int) -> dict[str, int]:
    deleted = order_resource.delete(str(orderNumber))
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"deleted": deleted}


@app.get("/orderdetails", tags=["orderdetails"])
def get_orderdetails(
    orderNumber: int | None = None,
    productCode: str | None = None,
    quantityOrdered: int | None = None,
    priceEach: Decimal | None = None,
    orderLineNumber: int | None = None,
) -> OrderDetailsCollection:
    return order_details_resource.get(
        _template_from_params(
            orderNumber=orderNumber,
            productCode=productCode,
            quantityOrdered=quantityOrdered,
            priceEach=priceEach,
            orderLineNumber=orderLineNumber,
        )
    )


@app.post("/orderdetails", tags=["orderdetails"])
def create_orderdetail(new_data: OrderDetails) -> str:
    try:
        return str(order_details_resource.post(new_data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/orders/{orderNumber}/orderdetails", tags=["orderdetails"])
def get_orderdetails_for_order(
    orderNumber: int, productCode: str | None = None
) -> OrderDetailsCollection:
    template = {"orderNumber": orderNumber}
    if productCode is not None:
        template["productCode"] = productCode
    return order_details_resource.get(template)


@app.get("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def get_orderdetail_by_id(orderNumber: int, productCode: str) -> OrderDetails:
    try:
        return order_details_resource.get_by_order_and_product(
            str(orderNumber), productCode
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def update_orderdetail(
    orderNumber: int, productCode: str, new_data: OrderDetails
) -> dict[str, int]:
    try:
        updated = order_details_resource.put_by_order_and_product(
            str(orderNumber), productCode, new_data
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated == 0:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return {"updated": updated}


@app.put("/orders/{orderNumber}/orderdetails", tags=["orderdetails"])
def update_orderdetail_with_query_product_code(
    orderNumber: int, productCode: str, new_data: OrderDetails
) -> dict[str, int]:
    return update_orderdetail(orderNumber, productCode, new_data)


@app.delete("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def delete_orderdetail(orderNumber: int, productCode: str) -> dict[str, int]:
    deleted = order_details_resource.delete_by_order_and_product(
        str(orderNumber), productCode
    )
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return {"deleted": deleted}


@app.delete("/orders/{orderNumber}/orderdetails", tags=["orderdetails"])
def delete_orderdetail_with_query_product_code(
    orderNumber: int, productCode: str
) -> dict[str, int]:
    return delete_orderdetail(orderNumber, productCode)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)

