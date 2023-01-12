FROM python:3.10.9-slim-buster

WORKDIR /usr/src

COPY req.txt ./

RUN pip install --no-cache-dir -r req.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]