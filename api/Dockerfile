FROM python:3.7.6-alpine3.11

COPY ./api /app
WORKDIR /app

RUN pip install -r requirements.txt

RUN ["chmod", "+x", "/app/wait-for.sh"]

CMD echo "Waiting for $NEO4J_HOST:$NEO4J_PORT and $ES_HOST:$ES_PORT ..." && \
    /app/wait-for.sh -t 75 $NEO4J_HOST:$NEO4J_PORT && \
    sleep 15 && \
    python app.py