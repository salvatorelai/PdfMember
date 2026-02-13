# Backend Base
FROM python:3.9-slim as backend-base
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend Dev
FROM backend-base as backend-dev
COPY backend .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Backend Prod
FROM backend-base as backend-prod
COPY backend .
RUN pip install gunicorn
# Use gunicorn with uvicorn workers for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "300"]

# Frontend Base
FROM node:20-slim as frontend-base
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

# Frontend Dev
FROM frontend-base as frontend-dev
COPY frontend .
CMD ["npm", "run", "dev", "--", "--host"]

# Frontend Build
FROM frontend-base as frontend-build
COPY frontend .
RUN npm run build

# Nginx Production
FROM nginx:alpine as production-web
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
