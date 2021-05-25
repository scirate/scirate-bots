FROM python:3.9-slim-buster
WORKDIR /scirate
COPY ./ ./
RUN pip install \
    discord \
    beautifulsoup4 
CMD ["python3", "index.py"]
