FROM python:3.10.4

WORKDIR /app

COPY setup.py .
COPY app.py .
RUN pip install --no-cache-dir -e .
RUN pip install --upgrade pip .



ARG APP_PORT=80
ENV FLASK_RUN_PORT=${APP_PORT}

ENTRYPOINT ["flask", "run"]
CMD ["--host", "0.0.0.0"]
