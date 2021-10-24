FROM python:3.7

RUN mkdir -p /app
ADD simple_http_server.py /app/
WORKDIR /app

EXPOSE 8080
CMD ["python", "simple_http_server.py"]