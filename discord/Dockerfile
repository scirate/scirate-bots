FROM python:3.9-slim-buster
WORKDIR /scirate
COPY ./ ./
RUN pip3 pipenv
RUN pipenv install \
    discord \
    beautifulsoup4 
CMD ["pipenv", "run", "python3", "index.py"]    
