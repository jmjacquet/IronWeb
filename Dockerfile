FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /ironweb
WORKDIR /ironweb
COPY reqs.txt /ironweb/
# Install requirements
RUN pip install --upgrade pip
RUN pip install -r reqs.txt
COPY . /ironweb/
RUN apt-get update && apt-get install mc -y && apt-get install vim -y

