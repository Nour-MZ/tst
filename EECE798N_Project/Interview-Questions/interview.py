from flask import Flask, request, jsonify
import requests
from mistralai import Mistral
import json
app = Flask(__name__)

# Configuration
MISTRAL_API_KEY = "DgPbZl3NaH3ai9xd8ruJBy4qCfqLQSxE"
mistral_client = Mistral(api_key=MISTRAL_API_KEY)
MODEL_NAME = "ft:open-mistral-7b:c099368a:20250414:4d9d311e"

def generate_interview_questions(cv_data, job_data):
    """Generate questions using Mistral"""
    prompt = f"""
    You are an expert recruitment AI assistant tasked with generating interview questions tailored to a specific candidate's profile and job posting.Given the following JSON representation of CV:
    
    Candidate CV:
    {{
        "education": {cv_data.get('education', [])},
        "experience": {cv_data.get('experience', [])},
        "skills": {cv_data.get('skills', [])},
        "projects": {cv_data.get('projects', [])}
    }}
    
    and Job Posting:
    {{
        "title": "{job_data.get('job_title', '')}",
        "requirements": {job_data.get('requirements', [])},
        "responsibilities": {job_data.get('responsibilities', [])},
        "experience_needed": "{job_data.get('experience', '')}"
    }}
    
   Based on the given candidate information encoded in the JSON above, create a structured response in JSON format. Here is the structure of the JSON:{{  \"general\": [\"5 questions about the candidate's background, motivation, and role interest.\"],  \"technical\": [\"5 questions focusing on the candidate's specific skills and job requirements.\"],  \"behavioral\": [\"3 questions to evaluate teamwork, problem-solving, and situational responses.\"].Each object should independently follow the structure above, and ensure the total number of interview questions across all categories does not exceed 15. Ensure each category (`general`, `technical`, `behavioral`) contains at least one question where applicable.Focus on tailoring the questions specifically to the candidate's CV and the job posting.Use professional and conversational language aligned with real-world interview scenarios. Ensure only to return the format mentioned above and nothing else."}}
    """
    
    response = mistral_client.chat.complete(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    print("res", response)
    try:
        raw_content = response.choices[0].message.content
        print("Raw AI response:", repr(raw_content))  # Add this for debugging
        questions = json.loads(raw_content)
        return questions
    except json.JSONDecodeError as e:
        print("JSON decoding failed:", e)
        raise Exception("Failed to parse questions from AI response")

@app.route('/generate-questions', methods=['POST'])
def handle_question_generation():
    try:
        # Validate input
        data = request.json
        print("data", data)
        required_fields = ['cv', 'job']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing candidate_id or job_id"}), 400
        
        # Generate questions
        questions = generate_interview_questions(data['cv'], data['job'])
        print("quest", questions)
        return jsonify({
            "status": "success",
            "questions": questions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3004, debug=True)  # Running on different port