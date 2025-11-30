FROM node:25.2.1-alpine AS deps
FROM node:25.2.1-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:25.2.1-alpine AS build
FROM node:25.2.1-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG VITE_API_BASE_URL=http://backend:8000/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginx:1.29.3-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist .
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

