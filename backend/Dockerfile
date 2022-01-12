FROM python:3.7.12-slim

ENV PYTHONUNBUFFERED 1 
ENV TZ=America

RUN apt-get update && apt-get install -y python3-pip 
RUN pip3 install --upgrade openai

RUN mkdir -p /app
WORKDIR /app

COPY app/bertopic_trained_alex_1026 /app
COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["python3", "server.py"]
