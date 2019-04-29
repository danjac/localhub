FROM node:11
ADD . /app
WORKDIR /app
RUN npm install

COPY ./docker/webpack/start /start
RUN chmod +x /start
