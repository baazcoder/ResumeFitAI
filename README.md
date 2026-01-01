# ResumeFitAI

**AI-Powered ATS Resume Matcher & Improvement Tool**  

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green)](https://fastapi.tiangolo.com/) [![PyTorch](https://img.shields.io/badge/PyTorch-2.1.0-red)](https://pytorch.org/)  

**GitHub Repo:** [https://github.com/baazcoder/ResumeFitAI](https://github.com/baazcoder/ResumeFitAI)

---

## Project Overview

**ResumeFitAI** is an AI-powered tool that evaluates resumes against job descriptions to compute ATS (Applicant Tracking System) match scores. It uses **NLP embeddings** and **LLM-based suggestions** to provide actionable advice for improving resumes.  

This system is built for **freshers, job seekers, and recruiters** to quickly assess resumes, highlight missing skills, and suggest improvements for better job matches.

---

## Key Features

- Compute **semantic similarity** between resume and job description using **Sentence-BERT embeddings**  
- Section-wise scoring: **Skills, Experience, Education**  
- **Keyword gap analysis**: Identify missing important skills from the resume  
- **LLM-based suggestions**: Integrated with **LLaMA / Ollama** to provide actionable resume improvement tips  
- Supports **PDF, DOCX, and TXT** file uploads  
- Stores **analysis history** for tracking improvements  

---

## Tech Stack

- **Python** – Core language  
- **FastAPI** – Backend API  
- **Sentence-Transformers** – NLP embeddings  
- **PyTorch** – For embeddings similarity computation  
- **Ollama / LLaMA** – Large language model for AI suggestions  
- **PyPDF2 & python-docx** – File parsing  
- **Jinja2** – HTML templating  
- **JSON** – History tracking  

---

## Screenshots

*(Add screenshots of your app running here — FastAPI output, HTML page, AI suggestions, keyword analysis, etc.)*

---
## Setup Instructions



1. **Clone the repository**

```bash
git clone https://github.com/baazcoder/ResumeFitAI.git
cd ResumeFitAI

2. **Create a virtual environment (optional but recommended)

python -m venv env
# Windows
env\Scripts\activate
# Linux / Mac
source env/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Install and run Ollama (for AI suggestions)

Download Ollama: https://ollama.com/download

Pull LLaMA model:

ollama pull llama3.2


Start Ollama server (if not running automatically):

ollama run llama3.2


5. Run the FastAPI app

uvicorn app:app --reload


6. Open in browser: http://127.0.0.1:8000

How It Works

Resume and Job Description are uploaded / entered

Text is extracted (PDF / DOCX / TXT)

Sentence embeddings are computed for both resume and JD

Cosine similarity is calculated → Overall ATS match score

Keyword gaps and section-wise analysis are generated

LLM (Ollama) provides actionable suggestions to improve resume

Project Roadmap / Future Enhancements

Deploy as cloud app (Heroku / Render / Railway)

Add multi-resume batch analysis

Add visual charts for skills matching

Integrate grammar & clarity suggestions using LLM

Usage

Upload a resume (PDF, DOCX, TXT)

Paste the job description

View match score, keywords, section analysis, and AI suggestions

Track improvement using history tab

License

This project is for learning purposes. You may freely use, modify, and share it.


---

If you want, I can also **write a perfect, recruiter-ready resume entry** for this project that will make it **stand out for AI/ML jobs in India**.  

Do you want me to do that?

