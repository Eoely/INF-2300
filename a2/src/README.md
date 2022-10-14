# INF-2300 Assignment 2

## How to run using docker(recommended)
1. Make sure you have docker installed and running
2. Naviagte to /src folder (same directory as docker-compose.yml)
3. run "docker compose up" in terminal

## How to run without docker
### Run server (Requires python 3)
1. "cd server"
2. "pip install -r requirements.txt" to download necessary pip packages
3. "python(3) app.py"
4. Should now be running on port 5000

### Run client (Requires node 16+)
1. "cd site"
2. "npm install"
3. "npm run dev"
4. Site should now be running on port 5173 and connected to server
    - http://localhost:5173/