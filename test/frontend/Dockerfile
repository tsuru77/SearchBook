# Multi-stage Dockerfile for React + Vite Frontend

# Stage 1: Dependencies
FROM node:20-alpine as deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build (Vite build)
FROM node:20-alpine as build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG VITE_API_BASE_URL=http://backend:8000/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# Stage 3: Runtime (Nginx serving static files)
FROM nginx:1.25-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist .
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
