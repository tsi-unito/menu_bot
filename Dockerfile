FROM python:3.10

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./bot.py .
COPY ./scraper.py .
COPY ./config.json .

CMD [ "python3", "bot.py"]
