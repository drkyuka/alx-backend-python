FROM python:3.10
WORKDIR /messaging_app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
