from fastapi import FastAPI, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from google import genai
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from utils import create_pdf_from_string
from prompts import question_prompt, resume_prompt, resume_standalone_prompt

from fastapi.staticfiles import StaticFiles
# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
UPLOAD_FOLDER = Path("static/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Initialize Gemini API client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def LLM_call(prompt: str):
    prompt = prompt[:17576]

    try:
        # Make request to Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        
        # Log the raw response for debugging
        # print(f"Gemini API response: {response.text}")
        
        # Check if the response is empty or invalid
        if not response.text:
            raise ValueError("Received empty response from Gemini API")

        return response.text
    except Exception as e:
        # Log any error for further debugging
        print(f"Error in LLM_call: {str(e)}")
        return f"Error: {str(e)}"




    
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_FOLDER / file.filename
        with file_path.open("wb") as f:
            f.write(await file.read())

        reader = PdfReader(str(file_path))
        text = "".join([page.extract_text() for page in reader.pages])

        response = await LLM_call(question_prompt + text + "```")

        # Clean the response by removing any extraneous markdown or other non-JSON characters
        response = response.replace("```json", "").replace("```", "").strip()

        # Ensure the response is valid JSON
        if not response.startswith("{"):
            raise ValueError("Invalid JSON response format")

        # Attempt to load the JSON response
        json_response = json.loads(response)
        
        return {"ok": True, "response": json_response, "file_name": str(file_path)}

    except Exception as e:
        return {"ok": False, "error": f"Error processing PDF file: {str(e)}"}



@app.post("/resume")
async def resume(file_path: str = Form(...), wrong_questions: str = Form("")):
    try:
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() for page in reader.pages])

        filled_prompt = resume_prompt.replace("{questions}", wrong_questions).replace("{file}", text)
        response = await LLM_call(filled_prompt)

        pdf_path = create_pdf_from_string(response)

        return {"ok": True, "response": response, "file_name": file_path, "pdf_path": pdf_path}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/resume_standalone")
async def resume_standalone(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_FOLDER / file.filename
        with file_path.open("wb") as f:
            f.write(await file.read())

        reader = PdfReader(str(file_path))
        text = "".join([page.extract_text() for page in reader.pages])

        response = await LLM_call(resume_standalone_prompt.replace("{file}", text))

        return {"ok": True, "response": response, "file_name": str(file_path)}
    except Exception as e:
        return {"ok": False, "error": f"Error processing PDF file: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
