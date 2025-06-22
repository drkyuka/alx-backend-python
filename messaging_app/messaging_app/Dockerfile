FROM python:3.10-slim
WORKDIR /messaging_app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "-p", "8000"]
