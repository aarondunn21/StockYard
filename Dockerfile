FROM python:3.11-buster

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8 

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]

CMD [ "app.py" ]