FROM python:3.12

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install gunicorn==20.1.0 --no-cache-dir

# COPY requirements ./requirements/  # FIXME:
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x entrypoint.sh
CMD ["sh", "entrypoint.sh"]
