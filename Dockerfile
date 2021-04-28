FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app/mangaloid_instance

CMD [ "python", "-u", "main.py" ]
