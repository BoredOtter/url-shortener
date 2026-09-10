FROM node:24-alpine@sha256:50c8e8ca1d27439048670df5883f32d57cf81cff6233222c893fd0d9884cbd81 AS build

WORKDIR /app

RUN corepack enable

COPY package.json yarn.lock .yarnrc.yml ./
RUN yarn install --immutable

COPY . .
RUN yarn test
RUN yarn build

FROM nginxinc/nginx-unprivileged:1.31-alpine@sha256:3707417e3304492667a63c90ac0103465330437f9cdfaa38f8cd19f9975cbeed

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

USER nginx

EXPOSE 8080