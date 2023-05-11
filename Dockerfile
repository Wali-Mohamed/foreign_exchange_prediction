FROM python:3.10

ADD app.py .
RUN pip install flask pandas numpy glob datetime joblib sqlite arch requests

CMD ["python", "./app.py"]