FROM python:3.7.2-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3306
CMD [ "python3","wsgi.py" ]
