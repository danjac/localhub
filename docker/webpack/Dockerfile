FROM node:latest
ADD . /app
WORKDIR /app
RUN npm install

COPY ./docker/webpack/start /start
RUN chmod +x /start
