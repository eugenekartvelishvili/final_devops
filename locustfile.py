from locust import HttpUser, task, between

class DevopsUser(HttpUser):
    # Пауза между запросами одного "пользователя"
    wait_time = between(0.2, 1.0)

    @task(3)
    def health(self):
        # Часто проверяем /health, чтобы видеть стабильность
        self.client.get("/health", name="health")

    @task(1)
    def produce(self):
        # Реже, но жёстче бьём по бизнес-эндпоинту
        self.client.post(
            "/produce",
            json={"message": "load_test_message"},
            name="produce"
        )