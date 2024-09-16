FROM python:3.11

WORKDIR movies_service/src

COPY requirements.txt /movies_service/requirements.txt

RUN pip install --no-cache-dir -r /movies_service/requirements.txt

COPY src /movies_service/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
