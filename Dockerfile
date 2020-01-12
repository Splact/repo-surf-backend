FROM python:3.8

RUN pip install poetry

# set poetry to not manage virtualenvs
RUN poetry config virtualenvs.create false

COPY . /app/
WORKDIR /app

RUN poetry install --no-dev

EXPOSE 5000

CMD python manage.py
