FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home lounge && mkdir -p /app/instance && chown -R lounge:lounge /app
USER lounge
EXPOSE 5066
CMD ["gunicorn", "--bind", "0.0.0.0:5066", "--workers", "2", "--timeout", "120", "wsgi:app"]
