FROM node:17-slim

WORKDIR /app

COPY package*.json .

RUN npm ci --dev

COPY . .

CMD ["./node_modules/.bin/parcel", "build", "bundles-src/index.js", "--dist-dir", "bundles", "--public-url=./"]
