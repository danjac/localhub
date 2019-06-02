FROM node:11
ADD . /app
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY ./docker/local/webpack/start /start
RUN chmod +x /start
