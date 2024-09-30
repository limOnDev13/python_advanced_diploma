FROM python:3.12

RUN apt-get update && apt-get install -y python3-dev && rm -rf /var/lib/apt/lists/*

COPY /src /src
RUN pip install -r /src/requirements.txt
ENV PYTHONPATH $PYTHONPATH:/src
ENV ENV $ENV
ENV DB_URL $DB_URL
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
