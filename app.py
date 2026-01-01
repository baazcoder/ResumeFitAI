from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sentence_transformers import SentenceTransformer, util
import os
import json
import re
from collections import Counter
from datetime import datetime
import PyPDF2
import docx
import requests

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")

# Load model
MODEL_PATH = "resume_ats_model"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model folder not found at {MODEL_PATH}")
model = SentenceTransformer(MODEL_PATH)

# Ollama API endpoint (runs locally)
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2" 

# History file
HISTORY_FILE = "analysis_history.json"


def check_ollama_available():
    """Check if Ollama is running locally"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def extract_text_from_file(file_content, filename):
    """Extract text from TXT, PDF, or DOCX files"""
    try:
        if filename.endswith('.txt'):
            return file_content.decode('utf-8')
        elif filename.endswith('.pdf'):
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif filename.endswith('.docx'):
            import io
            doc = docx.Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def extract_keywords(text, top_n=15):
    """Extract important keywords from text"""
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                  'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    filtered_words = [w for w in words if w not in stop_words]
    word_freq = Counter(filtered_words)
    return word_freq.most_common(top_n)


def analyze_sections(resume_text, job_desc):
    """Analyze different sections of resume vs job description"""
    sections = {
        'skills': r'(?i)(skills?|technical skills?|core competencies)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n[A-Z]|$)',
        'experience': r'(?i)(experience|work history|employment)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n[A-Z]|$)',
        'education': r'(?i)(education|academic|qualifications?)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|\n[A-Z]|$)'
    }
    
    section_scores = {}
    for section_name, pattern in sections.items():
        match = re.search(pattern, resume_text, re.MULTILINE | re.DOTALL)
        if match:
            section_text = match.group(2)
            section_emb = model.encode(section_text, convert_to_tensor=True)
            job_emb = model.encode(job_desc, convert_to_tensor=True)
            score = util.pytorch_cos_sim(section_emb, job_emb).item()
            section_scores[section_name] = round(score * 100, 2)
        else:
            section_scores[section_name] = 0
    
    return section_scores


def get_ai_suggestions_ollama(resume_text, job_desc, similarity_score):
    """Get AI-powered suggestions using local Ollama"""
    if not check_ollama_available():
        return """⚠️ Ollama is not running. 

To enable AI suggestions:
1. Install Ollama from: https://ollama.com/download
2. Run: ollama pull llama3.2
3. Ollama will start automatically

The app works fine without AI suggestions!"""
    
    try:
        prompt = f"""Analyze this resume against the job description and provide 5-7 specific, actionable suggestions to improve the ATS match score (currently {similarity_score}%).

Job Description (first 800 chars):
{job_desc[:800]}

Resume (first 1200 chars):
{resume_text[:1200]}

Provide suggestions in this format:
1. [Title]: [Specific actionable advice]

Focus on:
- Missing keywords to add
- Skills to emphasize
- Experience to highlight
- Quantifiable achievements
- Format improvements

Keep it concise and actionable."""

        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No suggestions generated')
        else:
            return f"Error: Ollama returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏱️ AI suggestion timed out. Try again or continue without AI suggestions."
    except Exception as e:
        return f"Error getting AI suggestions: {str(e)}\n\nThe app works fine without AI suggestions!"


def save_to_history(data):
    """Save analysis to history file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(data)
        
        # Keep only last 50 entries
        history = history[-50:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")


def load_history():
    """Load analysis history"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading history: {e}")
        return []


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    history = load_history()
    ollama_status = check_ollama_available()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "history": history,
        "ollama_status": ollama_status
    })


@app.post("/process", response_class=HTMLResponse)
async def process(request: Request, resume: UploadFile, job_desc: str = Form(...)):
    # Read resume text
    file_content = await resume.read()
    resume_text = extract_text_from_file(file_content, resume.filename)
    
    if resume_text.startswith("Error") or resume_text == "Unsupported file format":
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": resume_text,
            "history": load_history()
        })
    
    # Compute embeddings
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_desc, convert_to_tensor=True)
    
    # Overall similarity
    similarity = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
    similarity = round(similarity * 100, 2)
    
    # Extract keywords
    resume_keywords = extract_keywords(resume_text, top_n=20)
    job_keywords = extract_keywords(job_desc, top_n=20)
    
    # Find matching and missing keywords
    resume_kw_set = set([kw[0] for kw in resume_keywords])
    job_kw_set = set([kw[0] for kw in job_keywords])
    
    matching_keywords = list(resume_kw_set & job_kw_set)[:10]
    missing_keywords = list(job_kw_set - resume_kw_set)[:10]
    
    # Section analysis
    section_scores = analyze_sections(resume_text, job_desc)
    
    # AI suggestions using Ollama
    ai_suggestions = get_ai_suggestions_ollama(resume_text, job_desc, similarity)
    
    # Save to history
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "filename": resume.filename,
        "similarity": similarity,
        "section_scores": section_scores
    }
    save_to_history(history_entry)
    
    history = load_history()
    ollama_status = check_ollama_available()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "resume_text": resume_text,
        "job_desc": job_desc,
        "similarity": similarity,
        "resume_keywords": resume_keywords[:10],
        "job_keywords": job_keywords[:10],
        "matching_keywords": matching_keywords,
        "missing_keywords": missing_keywords,
        "section_scores": section_scores,
        "ai_suggestions": ai_suggestions,
        "history": history,
        "ollama_status": ollama_status
    })


@app.get("/history")
async def get_history():
    """API endpoint to get history"""
    return JSONResponse(load_history())


@app.post("/clear-history")
async def clear_history():
    """Clear analysis history"""
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return JSONResponse({"status": "success"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


@app.get("/check-ollama")
async def check_ollama():
    """Check if Ollama is running"""
    return JSONResponse({"available": check_ollama_available()})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)