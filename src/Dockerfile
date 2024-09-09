FROM python:3.12

RUN mkdir /src
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:./src"

COPY __init__.py /src/__init__.py
COPY main.py /src/main.py
COPY ./api /src/api
COPY ./config /src/config
COPY ./database /src/database
COPY ./schemas /src/schemas
CMD ["python3", "./src/main.py"]