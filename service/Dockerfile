FROM python:alpine3.7
RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

#RUN pip install -r requirements.txt
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies
COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "start.py" ]