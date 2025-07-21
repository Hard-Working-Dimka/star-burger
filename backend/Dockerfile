FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8081", "star_burger.wsgi:application"]