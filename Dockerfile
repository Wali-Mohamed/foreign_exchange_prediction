FROM python:3.10
WORKDIR /exchange
COPY . /exchange


RUN pip install -r requirements.txt
EXPOSE 3000

CMD ["python", "./app.py"]