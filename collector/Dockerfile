FROM python:3.12-alpine

WORKDIR /app
COPY app.py ./app.py

ENV COLLECTOR_PORT=9100 \
    COLLECTOR_FILE=/data/messages.json

VOLUME ["/data"]
EXPOSE 9100

CMD ["python3", "app.py"]
