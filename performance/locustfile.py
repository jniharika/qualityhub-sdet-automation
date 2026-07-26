from locust import HttpUser, between, task


class InventoryApiUser(HttpUser):
    wait_time = between(0.2, 1.0)

    @task(4)
    def list_inventory(self):
        with self.client.get("/api/items", name="GET /api/items", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def create_inventory_item(self):
        payload = {
            "name": "Load Test Item",
            "quantity": 1,
            "status": "active",
        }
        with self.client.post(
            "/api/items",
            json=payload,
            name="POST /api/items",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Unexpected status: {response.status_code}")

