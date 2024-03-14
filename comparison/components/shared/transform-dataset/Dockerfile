FROM maven:3.8.6-openjdk-11-slim

WORKDIR /

COPY java /java

RUN cd /java; \
    mvn package -Dmaven.test.skip=true
