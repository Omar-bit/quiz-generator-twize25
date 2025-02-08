live demo: https://insightify-twise.netlify.app/

how to run the project
-clone the repo

-pip install -r requirements.txt
-create .env file inside server folder
-add GEMINI_API_KEY variable to the .env inside the server which is containing the gemini api key



-run npm i inside client folder
-create .env file inside client folder
-add VITE_BACKEND_URI variable to the .env inside the client

-run "npm run dev" inside the client
-run "uvicorn main:app --reload --port 8080" inside the server
