import datetime

import redis
from fastapi import Request, Response, status
from fastapi.responses import ORJSONResponse

from core.config import settings


async def check_request_limit(request: Request, call_next) -> Response:
    """Проверка на кол-во запросов в минуту"""

    redis_conn = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    pipe = redis_conn.pipeline()

    # Определяем текущее время
    now = datetime.datetime.now()

    # Получаем User-Agent из заголовков запроса
    user_agent = request.headers.get("user-agent", "unknown")

    # Ip юзера
    user_ip = request.headers.get("x-real-ip")

    # Создаем ключ для лимита запросов
    key = f"{user_ip}{user_agent}:{now.minute}"

    # Используем pipeline для инкремента и установки TTL
    pipe.incr(key, 1)
    pipe.expire(key, 60 - now.second)
    result_count_requests = pipe.execute()[0]

    # Проверка на лимит запросов
    if result_count_requests > settings.request_limit:
        return ORJSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": "Уважаемый ревьюер остановись, отдохни!"},
        )

    response = await call_next(request)
    return response
