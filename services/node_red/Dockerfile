FROM nodered/node-red:latest

USER root

COPY flows.json /usr/src/node-red/flows.json

COPY package.json /data/package.json

RUN npm install --only=prod --legacy-peer-deps --prefix /data \
 && npm cache clean --force \
 && chown -R node-red:node-red /data

USER node-red


