FROM python:3.11-slim

WORKDIR /app
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

ENV FLASK_APP=backend/app.py
EXPOSE 1996

VOLUME ["/comics"]
ENV COMICS_DIR=/comics

CMD ["flask", "run", "--host=0.0.0.0", "--port=1996"]