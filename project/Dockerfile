FROM python:2.7
COPY ./techtrends /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 3111
RUN python init_db.py
CMD ["python", "app.py"]
