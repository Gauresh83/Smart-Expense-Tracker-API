FROM node:18-alpine AS builder

WORKDIR /app

# ✅ Copy BOTH files (VERY IMPORTANT)
COPY package.json ./

# ✅ Clean + install exact versions
RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]