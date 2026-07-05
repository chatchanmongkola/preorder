# Dev-only image. Runs the Vite dev server against source mounted from the
# host by docker-compose. Not used for the Vercel production deploy (Vercel
# builds the static site directly).
FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
