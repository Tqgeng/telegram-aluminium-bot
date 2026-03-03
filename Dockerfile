FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip wheel

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x fastapi-application/prestart.sh

WORKDIR /app/fastapi-application

ENTRYPOINT ["./prestart.sh"]

CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


