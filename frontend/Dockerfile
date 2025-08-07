# build env
FROM node:21.7.1-alpine
WORKDIR /app

COPY package*.json ./

RUN npm install
# RUN npm ci

COPY . ./
RUN npm run build
# CMD cp -r build/* /app/result_build/
CMD tail -f /dev/null
