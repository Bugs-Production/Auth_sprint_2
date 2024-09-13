from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)


async def request_id_middleware(request: Request, call_next):
    # Извлекаем request_id
    request_id = request.headers.get("X-Request-Id")
    request_url = str(request.url)

    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )

    # Начинаем новый спан и добавляем request_id в качестве атрибута
    with tracer.start_as_current_span(request_url) as span:
        span.set_attribute("http.request_id", request_id)

        try:
            response = await call_next(request)
            span.set_status(Status(status_code=StatusCode.OK))
        except Exception as ex:
            span.set_status(Status(status_code=StatusCode.ERROR, description=str(ex)))
            raise
        finally:
            span.end()

        return response
