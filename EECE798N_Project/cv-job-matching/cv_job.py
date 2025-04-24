from flask import Flask, request, jsonify
import numpy as np
import requests
from datetime import datetime

app = Flask(__name__)

# HuggingFace Configuration
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
HF_TOKEN = "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" 

def get_embeddings(texts):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": texts, "options": {"wait_for_model": True}}
    )
    response.raise_for_status()
    return response.json()

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def evaluate(cv_data, job_data):
    # Prepare all texts for embedding
    cv_responsibilities_texts = [
    resp for exp in cv_data.get("experience", []) for resp in exp.get("responsibilities", [])
]

    texts = (
        cv_data["skills"] + 
        [", ".join(edu["degree"] for edu in cv_data.get("education", []))] +  # join degrees as education text
        cv_responsibilities_texts +
        [job_data["title"]] + 
        job_data["requirements"] + 
        job_data["responsibilities"] +
        [f"{cv_data.get('years_experience', 0)} years experience"]
    )
    
    # Get real embeddings
    embeddings = get_embeddings(texts)
    
    # Split embeddings
    ptr = 0
    cv_skills = embeddings[ptr:ptr+len(cv_data["skills"])]
    ptr += len(cv_data["skills"])
    cv_education = embeddings[ptr]
    ptr += 1
    cv_responsibilities = embeddings[ptr:ptr+len(cv_responsibilities_texts)]
    ptr += len(cv_responsibilities_texts)
    job_title = embeddings[ptr]
    ptr += 1
    job_reqs = embeddings[ptr:ptr+len(job_data["requirements"])]
    ptr += len(job_data["requirements"])
    job_resps = embeddings[ptr:ptr+len(job_data["responsibilities"])]
    ptr += len(job_data["responsibilities"])
    exp_embedding = embeddings[ptr]
    
    # Calculate all similarity scores
    scores = {
        # 1. CV Skills vs Job Requirements
        "skills_vs_requirements": max(
            [cosine_similarity(skill, req) 
             for skill in cv_skills for req in job_reqs],
            default=0
        ),
        # 2. Education vs Job Title
        "education_vs_title": cosine_similarity(cv_education, job_title),
        # 3. Responsibilities vs Skills
        "responsibilities_vs_skills": max(
            [cosine_similarity(resp, skill) 
             for resp in cv_responsibilities for skill in cv_skills],
            default=0
        ),
        # 4. Responsibilities vs Experience
        "responsibilities_vs_experience": max(
            [cosine_similarity(resp, job_resp) 
             for resp in cv_responsibilities for job_resp in job_resps],
            default=0
        ),
        # 5. Years of Experience match
        "experience_years_match": min(
            cv_data.get("years_experience", 0) / job_data.get("required_experience_years", 1), 
            1.0
        ),
        # 6. Job Title vs Experience
        "title_vs_experience": cosine_similarity(job_title, exp_embedding)
    }
    
    # Evaluation thresholds
    thresholds = {
        "skills_vs_requirements": 0.3,
        "education_vs_title": 0.4,
        "responsibilities_vs_skills": 0.3,
        "responsibilities_vs_experience": 0.3,
        "experience_years_match": 0.5,  # Must have ≥80% of required years
        "title_vs_experience": 0.2
    }
    
    # Convert scores to pass/fail
    meets_threshold = {k: v >= thresholds[k] for k, v in scores.items()}
    passed = sum(meets_threshold.values())
    total = len(thresholds)
    qualified = passed / total >= 0.5  # 50% criteria met
    
    return {
        "scores": {k: round(float(v), 2) for k, v in scores.items()},  # Ensure JSON serializable
        "thresholds": thresholds,
        "meets_threshold": {k: bool(v) for k, v in meets_threshold.items()},  # Convert numpy bools
        "passed_criteria": f"{passed}/{total}",
        "qualified": bool(qualified),
        "reason": "Qualified: ≥50% criteria met" if qualified 
                 else f"Disqualified: Only {passed}/{total} criteria met"
    }

@app.route('/cv-job-match', methods=['POST'])
def evaluate_endpoint():
    try:
        data = request.json
        print(data)
        required_fields = ['cv', 'job']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {required_fields}",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        result = evaluate(data['cv'], data['job'])

        return jsonify({
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003)