FROM python:3.9

WORKDIR /app

EXPOSE 5555

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "3", "-b", "127.0.0.1:8081", "star_burger.wsgi:application"]