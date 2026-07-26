import pytest


def test_create_and_retrieve_inventory_item(client):
    create_response = client.post(
        "/api/items",
        json={"name": "IPv6 Security Appliance", "quantity": 4, "status": "active"},
    )

    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created["id"] > 0
    assert created["name"] == "IPv6 Security Appliance"

    get_response = client.get(f"/api/items/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.get_json() == created


@pytest.mark.parametrize(
    ("payload", "field", "message"),
    [
        ({"name": "", "quantity": 1}, "name", "Name is required."),
        ({"name": "Router", "quantity": -1}, "quantity", "Quantity must be zero or greater."),
        ({"name": "Router", "quantity": "ten"}, "quantity", "Quantity must be an integer."),
        (
            {"name": "Router", "quantity": 1, "status": "unknown"},
            "status",
            "Status must be active or discontinued.",
        ),
    ],
)
def test_create_item_rejects_invalid_payloads(client, payload, field, message):
    response = client.post("/api/items", json=payload)

    assert response.status_code == 422
    assert response.get_json()["errors"][field] == message


def test_create_item_requires_json_content_type(client):
    response = client.post("/api/items", data="name=Router&quantity=2")

    assert response.status_code == 415
    assert "application/json" in response.get_json()["error"]


def test_list_items_returns_items_in_creation_order(client):
    payloads = [
        {"name": "API Gateway", "quantity": 2},
        {"name": "DNS Resolver", "quantity": 5, "status": "discontinued"},
    ]
    for payload in payloads:
        assert client.post("/api/items", json=payload).status_code == 201

    response = client.get("/api/items")

    assert response.status_code == 200
    assert [item["name"] for item in response.get_json()["items"]] == [
        "API Gateway",
        "DNS Resolver",
    ]


def test_delete_item_and_verify_it_is_no_longer_available(client):
    created = client.post(
        "/api/items",
        json={"name": "Temporary Test Device", "quantity": 1},
    ).get_json()

    delete_response = client.delete(f"/api/items/{created['id']}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/items/{created['id']}").status_code == 404


def test_get_unknown_item_returns_404(client):
    response = client.get("/api/items/99999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Item not found."}

