FROM ubuntu:20.04
WORKDIR /app
COPY . .
ENV TZ=America/Chicago
RUN apt-get update && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
&& apt-get install -y python3 python3-pip openssh-client
RUN pip3 install -r requirements.txt
CMD python3 main.py
