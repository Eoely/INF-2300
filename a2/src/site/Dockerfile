#Base image
FROM node:lts-alpine

# Set the working directory
WORKDIR /app

COPY package*.json ./

RUN npm install 

# Copy the project files
COPY . ./

# Executables
CMD [ "npm", "run", "dev", "--", "--host", "0.0.0.0" ]