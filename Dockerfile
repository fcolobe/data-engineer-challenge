FROM python:3.11.4

WORKDIR /app

ARG source_dir="fichiers source"
ARG target_dir="/app/fichiers source"

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY exo_1.py /app/exo_1.py
COPY exo_2.py /app/exo_2.py
COPY script.py /app/script.py
COPY ["${source_dir}", "${target_dir}"]
COPY drwh.db /app/drwh.db

CMD ["python", "script.py"]
