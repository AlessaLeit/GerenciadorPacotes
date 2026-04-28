# Estágio de Build
FROM node:20-slim AS build-stage
WORKDIR /app
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=${VITE_API_URL}
COPY package*.json ./
RUN rm -f package-lock.json && npm install
COPY . .
RUN npm run build

# Estágio de Produção
FROM nginx:stable-alpine as production-stage
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
