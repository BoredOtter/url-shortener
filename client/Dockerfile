FROM node:22-alpine@sha256:4d64b49e6c891c8fc821007cb1cdc6c0db7773110ac2c34bf2e6960adef62ed3 AS build

WORKDIR /app

RUN corepack enable

COPY package.json yarn.lock .yarnrc.yml ./
RUN yarn install --immutable

COPY . .
RUN yarn test
RUN yarn build

FROM nginxinc/nginx-unprivileged:1.29-alpine@sha256:0c79d56aee561a1d81c63f00eee5fb5fe29279560cdc55e91425133104c7fbe6

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
