# Pobranie oficjalnego obrazu Python 3.8
FROM python:3.8-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Aktualizacja systemu i instalacja zależności
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalacja Apache Airflow 2.2.0
RUN pip install --upgrade pip && pip install \
    apache-airflow==2.2.0 \
    psycopg2-binary
COPY dags /root/airflow/dags
# Inicjalizacja Airflow
RUN airflow initdb

# Skopiowanie przykładowych plików konfiguracyjnych
COPY airflow.cfg /root/airflow/airflow.cfg
COPY entrypoint.sh /entrypoint.sh

# Ustawienie zmiennej środowiskowej dla Airflow
ENV AIRFLOW_HOME=/root/airflow

# Otwarcie portu, na którym będzie działać Airflow
EXPOSE 8080

# Uruchomienie skryptu entrypoint.sh po uruchomieniu kontenera
ENTRYPOINT ["/entrypoint.sh"]
