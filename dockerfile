FROM python:3.11.2
WORKDIR /app
COPY . .
RUN python3 -m pip install pip==22.3.1
RUN python3 -m pip install -r requirements.txt
EXPOSE 3000
CMD [ "python3", "./server.py" ]
