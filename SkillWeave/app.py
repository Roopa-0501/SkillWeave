import re
import pickle
from flask import Flask, request, render_template
from PyPDF2 import PdfReader

from job_api import fetch_jobs
from job_matching import rank_jobs_by_percentage

# ======================= FLASK APP =====================
app = Flask(__name__)

# ======================= LOAD MODELS ===================
rf_classifier_categorization = pickle.load(open("models/rf_classifier_categorization.pkl", "rb"))
tfidf_vectorizer_categorization = pickle.load(open("models/tfidf_vectorizer_categorization.pkl", "rb"))

rf_classifier_job_recommendation = pickle.load(open("models/rf_classifier_job_recommendation.pkl", "rb"))
tfidf_vectorizer_job_recommendation = pickle.load(open("models/tfidf_vectorizer_job_recommendation.pkl", "rb"))

# ======================= SKILL DATABASE =================
SKILL_DB = {
    "software": [
        "python","java","c","c++","php","sql","html","css","javascript",
        "react","angular","node","django","flask","spring","spring boot",
        "mysql","mongodb","postgresql","aws","docker","kubernetes",
        "git","linux","api","rest","rest api","microservices"
    ],
    "banking": [
        "banking","finance","accounting","tally","gst","audit",
        "investment","loan","risk management","compliance","excel","sap"
    ],
    "designer": [
        "photoshop","illustrator","figma","canva","ui","ux","ui/ux",
        "graphic design","web design","branding","wireframing","prototyping"
    ],
    "healthcare": [
        "nursing","patient care","clinical","hospital","medical",
        "pharmacology","diagnosis","healthcare management"
    ],
    "teacher": [
        "teaching","lesson planning","curriculum","education",
        "assessment","classroom management","pedagogy"
    ],
    "law": [
        "advocate","legal","law","litigation","contracts",
        "criminal law","civil law","legal research"
    ],
    "generic": [
        "communication","teamwork","leadership","management",
        "problem solving","documentation","training"
    ]
}

# ======================= UTILITIES =====================
def clean_text(text):
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"@\S+", " ", text)
    text = re.sub(r"#\S+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def pdf_to_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ======================= ML ============================
def predict_category(text):
    text = clean_text(text)
    vec = tfidf_vectorizer_categorization.transform([text])
    return rf_classifier_categorization.predict(vec)[0]

def predict_job_role(text):
    text = clean_text(text)
    vec = tfidf_vectorizer_job_recommendation.transform([text])
    return rf_classifier_job_recommendation.predict(vec)[0]

# ======================= RESUME PARSING =================
def extract_name_from_resume(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    blacklist = ["career", "objective", "summary", "education", "skills", "experience"]

    for line in lines[:10]:
        if 2 <= len(line.split()) <= 4:
            if not any(b in line.lower() for b in blacklist):
                return line.title()

    return "Not Found"



def extract_contact_number_from_resume(text):
    text = text.replace("\n", " ")

    patterns = [
        r"\+\d{1,3}[\s-]?\d{6,12}",
        r"\b\d{10}\b",
        r"\b\d{5}\s\d{5}\b",
        r"\(\d{3}\)\s*\d{3}[-\s]?\d{4}",
        r"\b\d{3}[-\s]\d{3}[-\s]\d{4}\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()

    return "Not Found"


def extract_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group() if match else "Not Found"

def extract_skills(text):
    text = text.lower()
    found = set()
    for skills in SKILL_DB.values():
        for skill in skills:
            if re.search(rf"\b{re.escape(skill)}\b", text):
                found.add(skill)
    return list(found)

def extract_education(text):
    keywords = ["bachelor","master","b.tech","m.tech","b.sc","m.sc",
                "computer science","information technology","engineering"]
    edu = []
    for key in keywords:
        if re.search(rf"\b{key}\b", text.lower()):
            edu.append(key.title())
    return edu

# ======================= ROUTES ========================
@app.route("/")
def home():
    return render_template("resume.html")

@app.route("/pred", methods=["POST"])
def predict():
    if "resume" not in request.files:
        return render_template("resume.html", message="No resume uploaded")

    file = request.files["resume"]

    if file.filename.endswith(".pdf"):
        text = pdf_to_text(file)
    elif file.filename.endswith(".txt"):
        text = file.read().decode("utf-8")
    else:
        return render_template("resume.html", message="Upload PDF or TXT only")

    predicted_category = predict_category(text)
    recommended_job = predict_job_role(text)

    name = extract_name_from_resume(text)
    phone = extract_contact_number_from_resume(text)
    email = extract_email(text)
    skills = extract_skills(text)
    education = extract_education(text)

    # ================= JOB FETCHING (SKILLS-ONLY) =================
    search_queries = skills[:10] if skills else [predicted_category.lower()]

    all_jobs = []
    for skill in search_queries:
        all_jobs.extend(fetch_jobs(skill, limit=20))  # ~40 jobs

    unique_jobs = {
        (job["title"], job["company"]): job
        for job in all_jobs
    }.values()

    ranked_jobs = rank_jobs_by_percentage(skills, list(unique_jobs))

    return render_template(
        "resume.html",
        predicted_category=predicted_category,
        recommended_job=recommended_job,
        name=name,
        phone=phone,
        email=email,
        extracted_skills=skills,
        extracted_education=education,
        jobs=ranked_jobs,
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
