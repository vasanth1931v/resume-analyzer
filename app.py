from flask import Flask, render_template, request, jsonify
import os
import re
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Ensure uploads folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- TEXT EXTRACTION ---------------- #

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


# ---------------- SIMPLE TEXT PREPROCESS ---------------- #

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text


# ---------------- SKILL EXTRACTION ---------------- #

def extract_skills(text):
    skills_db = [
        "python", "java", "c++", "html", "css", "javascript",
        "machine learning", "deep learning", "nlp",
        "flask", "django", "react", "node", "sql",
        "mongodb", "aws", "docker"
    ]

    text = text.lower()
    found_skills = []

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))


# ---------------- ROLE SUGGESTION ---------------- #

def suggest_roles(skills):
    roles = []

    if "python" in skills and "flask" in skills:
        roles.append("Python Developer")

    if "html" in skills and "css" in skills and "javascript" in skills:
        roles.append("Frontend Developer")

    if "machine learning" in skills or "nlp" in skills:
        roles.append("Machine Learning Engineer")

    if "sql" in skills or "mongodb" in skills:
        roles.append("Backend Developer")

    if "aws" in skills or "docker" in skills:
        roles.append("Cloud Engineer")

    if not roles:
        roles.append("Software Engineer")

    return roles[:3]


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "")

    if resume_file.filename == "":
        return jsonify({"error": "Empty file name"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
    resume_file.save(file_path)

    # Extract text
    if file_path.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        resume_text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    # Preprocess
    resume_clean = preprocess(resume_text)
    jd_clean = preprocess(job_description)

    # Similarity Calculation
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_clean, jd_clean])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    match_percentage = round(similarity * 100, 2)

    # Skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    missing_skills = list(set(jd_skills) - set(resume_skills))
    suggested_roles = suggest_roles(resume_skills)

    return jsonify({
        "match_percentage": match_percentage,
        "resume_skills": resume_skills,
        "missing_skills": missing_skills,
        "suggested_roles": suggested_roles
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
