# Stage 1: Build
FROM node:20-slim AS build

WORKDIR /app

# 複製 package.json 和 lock
COPY package*.json ./
RUN npm install

# 複製其餘代碼
COPY . .

# 構建專案
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# 複製構建後的內容至 Nginx 路徑
COPY --from=build /app/dist /usr/share/nginx/html

# 複製自定義 Nginx 配置 (選配，若有 SPA 路由需求)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
