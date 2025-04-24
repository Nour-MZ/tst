from flask import Flask, request, jsonify
from openai import OpenAI
import json
import logging
import requests
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure OpenAI
OPENAI_API_KEY = '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'
client = OpenAI(api_key=OPENAI_API_KEY)
    
@app.route('/generate-job-description', methods=['POST'])
def generate_job_description():
    try:
        # Validate input
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        logger.debug(f"Received request data: {data}")

        required_fields = ['job_title', 'job_level', 'years_experience', 'additional_info' ]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Construct GPT prompt
        prompt = f"""
        Generate a comprehensive job description in JSON format based on these details:
        - Job Title: {data['job_title']}
        - Job Level: {data['job_level']}
        - Years of Experience: {data['years_experience']}
        - Additional Details: {data['additional_info']}

        The JSON structure must include:
        {{
            "job_title": "",
            "job_level": "(must match input: junior/mid/senior/lead/etc)",
            "years_experience": "(must match input)",
            "responsibilities": [
                "5-10 bullet points",
                "Action-oriented statements",
                "Each starting with a verb"
            ],
            "requirements": [
                "5-10 bullet points",
                "Include technical and soft skills",
                "Education requirements if needed"
            ],
            "required_certifications": [
                "Only certification names",
                "Leave empty if none required"
            ]
        }}

        Important rules:
        1. Responsibilities and requirements must align with job level
        2. Years of experience must match the input exactly
        3. Job level should match the input exactly
        4. Job Title should match the input exactly if it was good or adjust it 
        5. Return ONLY valid JSON with no additional text
        """

        # Call GPT-4-o-mini
        logger.debug("Sending request to OpenAI")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert HR assistant that generates perfect job descriptions in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )

        # Log the raw response
        json_str = response.choices[0].message.content

        # Clean the response by removing markdown code blocks
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]  # Remove ```json
        if json_str.startswith("```"):
            json_str = json_str[3:]  # Remove ```
        if json_str.endswith("```"):
            json_str = json_str[:-3]  # Remove trailing ```
        json_str = json_str.strip()

        # Try to parse JSON with error handling
        try:
            job_description = json.loads(json_str)
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error: {str(json_err)}")
            return jsonify({
                "error": "Failed to parse OpenAI response",
                "details": str(json_err),
                "raw_response": json_str
            }), 500
        
        return jsonify({
            "status": "success",
            "job_description": job_description
        })


    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)