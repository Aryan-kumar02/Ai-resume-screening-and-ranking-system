from flask import Flask, request, jsonify
import os
import pdfplumber
import spacy
import re
from docx import Document
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

REQUIRED_SKILLS = {"python", "machine learning", "data analysis", "flask", "deep learning", "nlp"}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract experience in years
def extract_experience(text):
    exp_match = re.findall(r'(\d+)\+?\s*years?', text.lower())
    return max(map(int, exp_match), default=0)  # Return max found experience

# Match keywords
def keyword_match(resume_text, required_skills):
    doc = nlp(resume_text.lower())
    matched_skills = {skill for skill in required_skills if skill in doc.text}
    return len(matched_skills), matched_skills

# Calculate ATS Score
def calculate_score(resume_text):
    matched_count, matched_skills = keyword_match(resume_text, REQUIRED_SKILLS)
    experience_years = extract_experience(resume_text)
    
    keyword_score = matched_count * 2  # Assign 2 points per matched skill
    experience_score = min(10, experience_years * 2)  # Max 10 points for experience
    total_score = keyword_score + experience_score
    
    return total_score, matched_skills, experience_years

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resumes' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('resumes')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No selected files"}), 400
    
    parsed_resumes = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"Processing file: {filename}")  # Added logging
            
            if filename.endswith('.pdf'):
                resume_text = extract_text_from_pdf(file_path)
            elif filename.endswith('.docx') or filename.endswith('.doc'):
                resume_text = extract_text_from_docx(file_path)
            else:
                continue  # Skip unsupported file types
            
            score, skills, experience = calculate_score(resume_text)
            parsed_resumes.append({
                "filename": filename,
                "score": score,
                "matched_skills": list(skills),
                "experience_years": experience
            })
    
    # Sort resumes based on ATS score
    sorted_resumes = sorted(parsed_resumes, key=lambda x: x['score'], reverse=True)
    
    print(f"Ranked Resumes: {sorted_resumes}")  # Added logging to display ranked resumes
    return jsonify({"ranked_resumes": sorted_resumes})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
