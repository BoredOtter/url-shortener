FROM node:24-alpine@sha256:2bdb65ed1dab192432bc31c95f94155ca5ad7fc1392fb7eb7526ab682fa5bf14 AS build

WORKDIR /app

RUN corepack enable

COPY package.json yarn.lock .yarnrc.yml ./
RUN yarn install --immutable

COPY . .
RUN yarn test
RUN yarn build

FROM nginxinc/nginx-unprivileged:1.31-alpine@sha256:aa8c9087d36d93e9d650c5365f883b421e8214aedbad24ade52b844c583358f1

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

USER nginx

EXPOSE 8080