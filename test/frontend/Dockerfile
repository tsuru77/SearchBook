# Multi-stage Dockerfile for React + Vite Frontend

# =====================================
# Stage 1: Build (Vite build)
# =====================================
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* yarn.lock* ./

# Install dependencies
RUN npm ci --omit=dev

# Copy source code
COPY . .

# Build with Vite
# Replace API_URL placeholder if provided
ARG API_URL=http://localhost/api
RUN sed -i "s|http://localhost:8000|${API_URL}|g" vite.config.ts src/lib/api.ts || true

# Build application
RUN npm run build

# =====================================
# Stage 2: Runtime (Nginx serving static files)
# =====================================
FROM nginx:1.25-alpine

# Copy built app to Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx config for SPA (all routes → index.html)
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # SPA: route tous les 404 vers index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets (js, css, images)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # No cache for HTML
    location ~* \.html$ {
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 256;
}
EOF

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Nginx runs by default
