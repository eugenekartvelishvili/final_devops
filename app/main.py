from fastapi import FastAPI
from pydantic import BaseModel
from faststream.redis import RedisBroker

# ---------- Event-driven слой: RedisBroker от FastStream ----------
# "redis" — имя сервиса Redis из docker-compose.
broker = RedisBroker("redis://redis:6379")

# ---------- HTTP слой FastAPI ----------
app = FastAPI(title="DevOps Final Service")


class ProduceRequest(BaseModel):
    message: str


@app.on_event("startup")
async def startup_event():
    """
    При старте приложения подключаемся к брокеру Redis.
    Без этого broker.publish упадёт с ошибкой IncorrectState.
    """
    await broker.start()


@app.on_event("shutdown")
async def shutdown_event():
    """
    При остановке приложения аккуратно закрываем соединение с брокером.
    """
    await broker.close()


@app.get("/health")
async def health():
    """
    Простой healthcheck: используется Docker healthcheck, CI и Locust.
    """
    return {"status": "ok"}


@app.post("/produce")
async def produce(body: ProduceRequest):
    """
    Принимаем сообщение по HTTP и публикуем его в брокер событий (Redis)
    через FastStream RedisBroker.
    """
    await broker.publish(body.message, channel="events_channel")
    return {"published": True, "message": body.message}