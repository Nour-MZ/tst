from flask import Flask, request, jsonify
import os
import json
import requests
import numpy as np
from datetime import datetime

import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

import mysql.connector  # instead of psycopg2
import os

DB_HOST = os.getenv('DB_HOST', 'db')  # 'db' matches the service name in docker-compose.yml
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'eece798')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

def get_db_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        date_of_birth = data.get('date')  # Frontend sends 'date' but schema expects 'date_of_birth'
        password = data.get('password')
        user_type = data.get('user_type', 'applicant')  # Default to 'applicant' if not provided

        # Validate required fields
        if not all([first_name, last_name, email, phone_number, date_of_birth, password]):
            return jsonify({"status": "error", "message": "All fields are required."}), 400

        # Hash the password (use a secure hashing method)
        # For example, using bcrypt:
        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Email already registered."}), 409

        # Insert the new user
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password, date_of_birth, phone_number, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (first_name, last_name, email, password, date_of_birth, phone_number, user_type))  # Use hashed_password here

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "User registered successfully."}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')  # In production, compare hashed passwords
        register_option = data.get('register_option')  # This is the user_type from the frontend

        if not email or not password or not register_option:
            return jsonify({"status": "error", "message": "All fields are required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check different tables based on register_option
        if register_option == 'company':
            # Check in departments table
            cursor.execute("""
                SELECT id, email, name FROM departments 
                WHERE email = %s AND password = %s;
            """, (email, password))
            
            user = cursor.fetchone()
            
            if user:
                cursor.close()
                conn.close()
                return jsonify({
                    "status": "success",
                    "user_id": user[0],
                    "register_option": "company"
                }), 200
        else:
            # Check in users table
            cursor.execute("""
                SELECT id, email, user_type FROM users 
                WHERE email = %s AND password = %s;
            """, (email, password))
            
            user = cursor.fetchone()
            
            if user:
                cursor.close()
                conn.close()
                return jsonify({
                    "status": "success",
                    "user_id": user[0],
                    "register_option": user[2]  # Return user_type as register_option
                }), 200

        # If we get here, no user was found
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    


@app.route('/check_db', methods=['GET'])
def check_db():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "success", "message": "Database connection successful!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, full_name, username, email, user_type FROM users;")
        users = cursor.fetchall()

        # Format the result as a list of dictionaries
        users_list = []
        for user in users:
            users_list.append({
                "id": user[0],
                "full_name": user[1],
                "username": user[2],
                "email": user[3],
                "user_type": user[4]
            })

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "users": users_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
 
    

@app.route('/add_applicant', methods=['POST'])
def add_application():
    try:
        data = request.json
        cv_data = data.get('cv_data', {})
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"status": "error", "message": "User ID is required."}), 400

        # Extract fields from cv_data
        education = json.dumps(cv_data.get('education', []))
        skills = json.dumps(cv_data.get('skills', []))
        experience = json.dumps(cv_data.get('experience', []))
        projects = json.dumps(cv_data.get('projects', []))
        certifications = json.dumps(cv_data.get('certifications', []))
        experience_years = sum(
            float(exp['years']) 
            for exp in cv_data.get('experience', []) 
            if isinstance(exp.get('years'), (int, float)) or (isinstance(exp.get('years'), str) and exp['years'].replace('.', '', 1).isdigit())
        )
        print("years", experience_years)


        # Database insertion
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already has a CV
        cursor.execute("SELECT id FROM applicant_cv WHERE user_id = %s", (user_id,))
        existing_cv = cursor.fetchone()

        if existing_cv:
            # Update existing CV
            cursor.execute("""
                UPDATE applicant_cv 
                SET education = %s, skills = %s, experience = %s, 
                    experience_years = %s, projects = %s, certifications = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s;
            """, (
                education, skills, experience, experience_years, 
                projects, certifications, user_id
            ))
            message = "CV updated successfully."
        else:
            # Insert new CV
            cursor.execute("""
                INSERT INTO applicant_cv (
                    user_id, education, skills, experience, 
                    experience_years, projects, certifications
                ) VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                user_id, education, skills, experience, 
                experience_years, projects, certifications
            ))
            message = "CV added successfully."

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": message}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_applicant/<int:user_id>', methods=['GET'])
def get_applicant_cv(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get CV data for the specific user
        cursor.execute("""
            SELECT id, education, skills, experience, 
                   experience_years, projects, certifications,
                   created_at, updated_at
            FROM applicant_cv
            WHERE user_id = %s;
        """, (user_id,))
        
        cv = cursor.fetchone()
        
        if not cv:
            return jsonify({"status": "error", "message": "CV not found"}), 404
            
        # Format the result as a dictionary that matches the frontend's expected format
        cv_data = {
            "education": json.loads(cv[1]) if cv[1] else [],
            "skills": json.loads(cv[2]) if cv[2] else [],
            "experience": json.loads(cv[3]) if cv[3] else [],
            "experience_years":cv[4],
            "projects": json.loads(cv[5]) if cv[5] else [],
            "certifications": json.loads(cv[6]) if cv[6] else []
        }

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "cv_data": cv_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user data
        cursor.execute("""
            SELECT id, first_name, last_name, email, 
                   phone_number, date_of_birth
            FROM users
            WHERE id = %s;
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
            
        # Format the result as a dictionary
        user_data = {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "phone_number": user[4],
            "date_of_birth": user[5].isoformat() if user[5] else None
        }

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "user": user_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_offered_job', methods=['GET'])
def get_offered_jobs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.id, j.title, j.job_level, j.years_experience, 
                   j.requirements, j.responsibilities, j.required_certifications,
                   j.status, j.date_offered, j.created_at, j.department_id,
                   d.name as department_name
            FROM jobs j
            JOIN departments d ON j.department_id = d.id
            ORDER BY j.created_at DESC;
        """)
        
        jobs = []
        for job in cursor.fetchall():
            jobs.append({
                "id": job[0],  # Changed to uppercase to match frontend
                "job_title": job[1],
                "job_level": job[2],
                "years_experience": job[3],
                "requirements": json.loads(job[4]) if job[4] else [],
                "responsibilities": json.loads(job[5]) if job[5] else [],
                "required_certifications": json.loads(job[6]) if job[6] else [],
                "status": job[7],
                "date_offered": job[8].isoformat() if job[8] else None,
                "created_at": job[9].isoformat() if job[9] else None,
                "dept_id": job[10],
                "department_name": job[11]  # Already included from the join
            })

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "jobs": jobs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/get_offered_job/<int:job_id>', methods=['GET'])
def get_offered_job(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get a specific job with department information
        cursor.execute("""
            SELECT j.id, j.title, j.job_level, j.years_experience, 
                   j.requirements, j.responsibilities, j.required_certifications,
                   j.status, j.date_offered, j.created_at, j.department_id,
                   d.name as department_name
            FROM jobs j
            JOIN departments d ON j.department_id = d.id
            WHERE j.id = %s;
        """, (job_id,))
        
        job = cursor.fetchone()
        
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404
            
        job_data = {
            "id": job[0],
            "title": job[1],
            "job_level": job[2],
            "years_experience": job[3],
            "requirements": json.loads(job[4]) if job[4] else [],
            "responsibilities": json.loads(job[5]) if job[5] else [],
            "required_certifications": json.loads(job[6]) if job[6] else [],
            "status": job[7],
            "date_offered": job[8].isoformat() if job[8] else None,
            "created_at": job[9].isoformat() if job[9] else None,
            "dept_id": job[10],
            "department_name": job[11]
        }

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "job": job_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/get_offered_job_by_dept/<int:dept_id>', methods=['GET'])
def get_offered_job_by_dept(dept_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                j.id, 
                j.title, 
                j.job_level, 
                j.years_experience, 
                j.requirements, 
                j.responsibilities, 
                j.required_certifications,
                j.status, 
                j.date_offered, 
                j.created_at, 
                j.department_id,
                d.name as department_name
            FROM jobs j
            JOIN departments d ON j.department_id = d.id
            WHERE j.department_id = %s
            ORDER BY j.created_at DESC;
        """
        
        cursor.execute(query, (dept_id,))
        jobs = cursor.fetchall()
        
        if not jobs:
            return jsonify({"status": "success", "jobs": [], "message": "No jobs found for this department"}), 200
            
        for job in jobs:
            if 'date_offered' in job and job['date_offered']:
                job['date_offered'] = job['date_offered'].isoformat()
            if 'created_at' in job and job['created_at']:
                job['created_at'] = job['created_at'].isoformat()
            if 'requirements' in job:
                job['requirements'] = json.loads(job['requirements']) if job['requirements'] else []
            if 'responsibilities' in job:
                job['responsibilities'] = json.loads(job['responsibilities']) if job['responsibilities'] else []
            if 'required_certifications' in job:
                job['required_certifications'] = json.loads(job['required_certifications']) if job['required_certifications'] else []

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "jobs": jobs}), 200
        
    except Exception as e:
        app.logger.error(f"Error in get_offered_job_by_dept: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": "Internal server error",
            "details": str(e)
        }), 500
@app.route('/check_cv_exists/<int:user_id>', methods=['GET'])
def check_cv_exists(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if the table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'applicant_cv'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "success",
                "cv_exists": False,
                "message": "CV table does not exist"
            }), 200
        
        # Check if CV exists for this user
        cursor.execute("SELECT 1 FROM applicant_cv WHERE user_id = %s", (user_id,))
        cv_exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "cv_exists": cv_exists,
            "message": "CV found" if cv_exists else "No CV found"
        }), 200
        
    except Exception as e:
        # Ensure connections are closed even if error occurs
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
        return jsonify({
            "status": "error",
            "cv_exists": False,
            "message": str(e)
        }), 500
    
@app.route('/check_if_applied/<int:user_id>/<int:job_id>', methods=['GET'])
def check_if_applied(user_id, job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the applied_jobs table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'applied_jobs'
        """)
        table_exists = cursor.fetchone()[0] > 0

        if not table_exists:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "success",
                "already_applied": False,
                "message": "Application table does not exist"
            }), 200

        # Check if the user already applied for the job
        cursor.execute("SELECT 1 FROM applied_jobs WHERE applicant_id = %s AND job_id = %s", (user_id, job_id))
        applied = cursor.fetchone() is not None

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "already_applied": applied,
            "message": "Already applied" if applied else "Not yet applied"
        }), 200

    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

        return jsonify({
            "status": "error",
            "already_applied": False,
            "message": str(e)
        }), 500

@app.route('/get_department/<int:dept_id>', methods=['GET'])
def get_department(dept_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get department details
        cursor.execute("""
            SELECT id, name, email, created_at
            FROM departments
            WHERE id = %s;
        """, (dept_id,))
        
        dept = cursor.fetchone()
        
        if not dept:
            return jsonify({"status": "error", "message": "Department not found"}), 404
            
        dept_data = {
            "id": dept[0],
            "department_name": dept[1],
            "email": dept[2],
            "created_at": dept[3].isoformat() if dept[3] else None
        }

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "department": dept_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_dashboard_stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count all jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]

        # Count active jobs
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'open'")
        active_jobs = cursor.fetchone()[0]

        # Count closed jobs
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status != 'open'")
        closed_jobs = cursor.fetchone()[0]

        # Count total applications
        cursor.execute("SELECT COUNT(*) FROM applied_jobs")
        total_applications = cursor.fetchone()[0]

        # Count unique applicants
        cursor.execute("SELECT COUNT(DISTINCT applicant_id) FROM applied_jobs")
        unique_applicants = cursor.fetchone()[0]

        return jsonify({
            "status": "success",
            "stats": {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "closed_jobs": closed_jobs,
                "total_applications": total_applications,
                "unique_applicants": unique_applicants
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/add_applied_job', methods=['POST'])
def add_applied_job():
    try:
        data = request.json
        required_fields = ['applicant_id', 'job_id', 'status', 'result']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if job exists and is open
        cursor.execute("""
            SELECT status FROM jobs 
            WHERE id = %s;
        """, (data['job_id'],))
        
        job = cursor.fetchone()
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404
            
        if job[0].lower() != 'open':
            return jsonify({"status": "error", "message": "This job is no longer available"}), 400

        # Check if user has already applied for this job
        cursor.execute("""
            SELECT id FROM applied_jobs 
            WHERE applicant_id = %s AND job_id = %s;
        """, (data['applicant_id'], data['job_id']))
        
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "You have already applied for this job"}), 400

        # Insert the application
        cursor.execute(""" 
            INSERT INTO applied_jobs (
                applicant_id, job_id, status, scores, 
                thresholds, meets_threshold, passed_criteria, 
                qualified_cv, reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['applicant_id'],
            data['job_id'],
            data['status'],
            json.dumps(data['result'].get('scores', {})),
            json.dumps(data['result'].get('thresholds', {})),
            json.dumps(data['result'].get('meets_threshold', {})),
            data['result'].get('passed_criteria', ''),
            data['result'].get('qualified_cv', False),
            data['result'].get('reason', '')
        ))

        application_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Application submitted successfully",
            "application_id": application_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/update_application_status', methods=['PUT'])
def update_application_status():
    try:
        # Get the JSON data from the request
        data = request.json
        required_fields = ['applicant_id', 'job_id', 'status']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the application exists for the given applicant_id and job_id
        cursor.execute(""" 
            SELECT id, status FROM applied_jobs 
            WHERE applicant_id = %s AND job_id = %s;
        """, (data['applicant_id'], data['job_id']))
        
        application = cursor.fetchone()
        if not application:
            return jsonify({"status": "error", "message": "Application not found"}), 404

        # Check if the current status is already the same as the one being updated
        if application[1].lower() == data['status'].lower():
            return jsonify({"status": "error", "message": "Status is already the same"}), 400

        # Update the application status
        cursor.execute("""
            UPDATE applied_jobs
            SET status = %s
            WHERE id = %s;
        """, (data['status'], application[0]))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Application status updated to {data['status']}"
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_all_applicants/<job_ids>', methods=['POST'])
def get_all_applicants(job_ids):
    try:
        # Convert job_ids string to list of integers
        job_id_list = [int(id) for id in job_ids.strip('[]').split(',') if id.strip()]
        
        if not job_id_list:
            return jsonify({"status": "error", "message": "No job IDs provided"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get applicants with their application details and CV information
        cursor.execute("""
            SELECT 
                aj.id as application_id,
                aj.applicant_id,
                aj.job_id,
                aj.status as application_status,
                aj.scores,
                aj.thresholds,
                aj.meets_threshold,
                aj.passed_criteria,
                aj.qualified_cv,
                aj.reason,
                aj.created_at as application_date,
                u.first_name,
                u.last_name,
                u.email,
                u.phone_number,
                ac.education,
                ac.skills,
                ac.experience,
                ac.experience_years,
                ac.projects,
                ac.certifications,
                j.title as job_title,
                j.job_level,
                j.years_experience as required_years,
                d.name as department_name
            FROM applied_jobs aj
            JOIN users u ON aj.applicant_id = u.id
            LEFT JOIN applicant_cv ac ON u.id = ac.user_id
            JOIN jobs j ON aj.job_id = j.id
            JOIN departments d ON j.department_id = d.id
            WHERE aj.job_id = ANY(%s)
            ORDER BY aj.created_at DESC;
        """, (job_id_list,))
        
        applicants = []
        for row in cursor.fetchall():
            applicant = {
                "application_id": row[0],
                "applicant_id": row[1],
                "job_id": row[2],
                "application_status": row[3],
                "scores": json.loads(row[4]) if row[4] else {},
                "thresholds": json.loads(row[5]) if row[5] else {},
                "meets_threshold": json.loads(row[6]) if row[6] else {},
                "passed_criteria": row[7],
                "qualified_cv": row[8],
                "reason": row[9],
                "application_date": row[10].isoformat() if row[10] else None,
                "applicant": {
                    "first_name": row[11],
                    "last_name": row[12],
                    "email": row[13],
                    "phone_number": row[14]
                },
                "cv": {
                    "education": json.loads(row[15]) if row[15] else [],
                    "skills": json.loads(row[16]) if row[16] else [],
                    "experience": json.loads(row[17]) if row[17] else [],
                    "experience_years": row[18],
                    "projects": json.loads(row[19]) if row[19] else [],
                    "certifications": json.loads(row[20]) if row[20] else []
                },
                "job": {
                    "title": row[21],
                    "job_level": row[22],
                    "required_years": row[23],
                    "department_name": row[24]
                }
            }
            applicants.append(applicant)

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "applicants": applicants}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/add_interview', methods=['POST'])
def add_interview():
    try:
        data = request.json
        required_fields = ['interview', 'questions']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        interview_data = data['interview']
        questions_data = data['questions']
        
        # Validate interview data
        interview_required_fields = ['applicant_id', 'job_id', 'meeting_title', 'meeting_date', 'start_time', 'end_time']
        if not all(field in interview_data for field in interview_required_fields):
            return jsonify({"status": "error", "message": "Missing required interview fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if applicant exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (interview_data['applicant_id'],))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Applicant not found"}), 404

        # Check if job exists and is open
        cursor.execute("SELECT status FROM jobs WHERE id = %s", (interview_data['job_id'],))
        job = cursor.fetchone()
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404
            
        if job[0].lower() != 'open':
            return jsonify({"status": "error", "message": "This job is no longer available"}), 400

        # Check if interview already scheduled for this time slot
        cursor.execute("""
            SELECT id FROM interviews 
            WHERE applicant_id = %s AND job_id = %s AND date = %s AND start_time = %s;
        """, (
            interview_data['applicant_id'], 
            interview_data['job_id'], 
            interview_data['meeting_date'], 
            interview_data['start_time']
        ))
        
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "An interview is already scheduled for this time slot"}), 400

        # Insert the interview
        cursor.execute("""
            INSERT INTO interviews (
                applicant_id, job_id, meeting_title, date, 
                start_time, end_time, questions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            interview_data['applicant_id'],
            interview_data['job_id'],
            interview_data['meeting_title'],
            interview_data['meeting_date'],
            interview_data['start_time'],
            interview_data['end_time'],
            json.dumps(questions_data)
        ))

        interview_id = cursor.lastrowid  
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Interview scheduled successfully",
            "interview_id": interview_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@app.route('/add_offer_job', methods=['POST'])
def add_offer_job():
    try:
        data = request.json
        
        # Validation
        if 'department_id' not in data or 'job_description' not in data:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        job_desc = data['job_description']

        required_fields = ['job_title', 'job_level', 'years_experience']
        if not all(field in job_desc for field in required_fields):
            missing = [f for f in required_fields if f not in job_desc]
            return jsonify({"status": "error", "message": f"Missing fields in job_description: {missing}"}), 400

        # Prepare data for insertion
        insert_data = {
            'department_id': data['department_id'],
            'title': job_desc['job_title'],
            'job_level': job_desc['job_level'],
            'years_experience': job_desc['years_experience'],
            'requirements': json.dumps(job_desc.get('requirements', [])),
            'responsibilities': json.dumps(job_desc.get('responsibilities', [])),
            'required_certifications': json.dumps(job_desc.get('required_certifications', [])),
            'status': job_desc.get('status', 'open'),
            'date_offered': datetime.now()
        }
        
        logging.debug(f"💾 Prepared insert data: {insert_data}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Modified INSERT query for MySQL
        cursor.execute("""
            INSERT INTO jobs (
                department_id, title, job_level, years_experience,
                requirements, responsibilities, required_certifications,
                status, date_offered
            ) VALUES (%(department_id)s, %(title)s, %(job_level)s, %(years_experience)s,
                      %(requirements)s, %(responsibilities)s, %(required_certifications)s,
                      %(status)s, %(date_offered)s)
        """, insert_data)

        # Get the last inserted ID for MySQL
        job_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "status": "success",
            "job_id": job_id,
            "message": "Job posted successfully"
        }), 201

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({
            "status": "error",
            "message": str(e),
            "type": type(e).__name__
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/get_applicants/<int:job_id>', methods=['GET'])
def get_applicants(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First check if the job exists
        cursor.execute("""
            SELECT id, department_id, title, job_level, years_experience
            FROM jobs
            WHERE id = %s
        """, (job_id,))
        
        job = cursor.fetchone()
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404

        # Get all applicants who applied for this job
        cursor.execute("""
            SELECT 
                u.id,
                u.first_name,
                u.last_name,
                u.email,
                u.phone_number,
                ac.experience_years,
                ac.skills,
                ac.experience,
                ac.education,
                aj.scores,
                aj.status
            FROM applied_jobs aj
            JOIN users u ON aj.applicant_id = u.id
            LEFT JOIN applicant_cv ac ON u.id = ac.user_id
            WHERE aj.job_id = %s
            ORDER BY ac.experience_years DESC
        """, (job_id,))
        
        applicants = []
        for row in cursor.fetchall():
            # Parse JSON fields
            skills = json.loads(row[6]) if row[6] else []
            experience = json.loads(row[7]) if row[7] else []
            education = json.loads(row[8]) if row[8] else {}
            scores = json.loads(row[9]) if row[9] else {}
            status= row[10]
            applicant = {
                "id": row[0],
                "name": f"{row[1]} {row[2]}",
                "email": row[3],
                "phone_number": row[4],
                "exp_years": row[5] or 0,
                "skills": skills,
                "experience": experience,
                "education": education,
                "match_score": scores,
                "status": status
            }
            applicants.append(applicant)

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success", 
            "job_id": job_id,
            "applications": applicants
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/get_applied_job/<int:job_id>', methods=['GET'])
def get_applied_job(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First check if the job exists
        cursor.execute("""
            SELECT id FROM jobs
            WHERE id = %s
        """, (job_id,))
        
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Job not found"}), 404

        # Get all applications for this job
        cursor.execute("""
            SELECT 
                aj.id,
                aj.applicant_id,
                aj.status,
                aj.scores,
                aj.thresholds,
                aj.meets_threshold,
                aj.passed_criteria,
                aj.qualified_cv,
                aj.reason,
                aj.created_at
            FROM applied_jobs aj
            WHERE aj.job_id = %s
            ORDER BY aj.created_at DESC
        """, (job_id,))
        
        applications = []
        for row in cursor.fetchall():
            # Parse JSON fields
            scores = json.loads(row[3]) if row[3] else {}
            thresholds = json.loads(row[4]) if row[4] else {}
            meets_threshold = json.loads(row[5]) if row[5] else {}
            
            application = {
                "id": row[0],
                "applicant_id": row[1],
                "status": row[2],
                "scores": scores,
                "thresholds": thresholds,
                "meets_threshold": meets_threshold,
                "passed_criteria": row[6],
                "qualified_cv": row[7],
                "reason": row[8],
                "created_at": row[9].isoformat() if row[9] else None
            }
            applications.append(application)

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success", 
            "job_id": job_id,
            "applications": applications
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/update_interview/<int:meeting_id>', methods=['PUT'])
def update_interview(meeting_id):
    try:
        data = request.json
        required_fields = ['meeting_title', 'meeting_date', 'start_time', 'end_time']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if interview exists
        cursor.execute("""
            SELECT id FROM interviews 
            WHERE id = %s
        """, (meeting_id,))
        
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Interview not found"}), 404

        # Update the interview
        cursor.execute("""
            UPDATE interviews 
            SET meeting_title = %s, date = %s, start_time = %s, end_time = %s
            WHERE id = %s
        """, (
            data['meeting_title'],
            data['meeting_date'],
            data['start_time'],
            data['end_time'],
            meeting_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Interview updated successfully"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/update_technical_interview/<int:meeting_id>', methods=['PUT'])
def update_technical_interview(meeting_id):
    try:
        data = request.json
        required_fields = ['meeting_title', 'meeting_date', 'start_time', 'end_time']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if technical interview exists
        cursor.execute("""
            SELECT id FROM technical_interviews 
            WHERE id = %s
        """, (meeting_id,))
        
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Technical interview not found"}), 404

        # Update the technical interview
        cursor.execute("""
            UPDATE technical_interviews 
            SET meeting_title = %s, interview_date = %s, start_time = %s, end_time = %s
            WHERE id = %s
        """, (
            data['meeting_title'],
            data['meeting_date'],
            data['start_time'],
            data['end_time'],
            meeting_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Technical interview updated successfully"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/add_technical_interview', methods=['POST'])
def add_technical_interview():
    try:
        data = request.json
        required_fields = ['interview']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        interview_data = data['interview']
        
        # Validate interview data
        interview_required_fields = ['applicant_id', 'job_id', 'meeting_title', 'meeting_date', 'start_time', 'end_time']
        if not all(field in interview_data for field in interview_required_fields):
            return jsonify({"status": "error", "message": "Missing required interview fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if applicant exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (interview_data['applicant_id'],))
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Applicant not found"}), 404

        # Check if job exists and is open
        cursor.execute("SELECT status FROM jobs WHERE id = %s", (interview_data['job_id'],))
        job = cursor.fetchone()
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404
            
        if job[0].lower() != 'open':
            return jsonify({"status": "error", "message": "This job is no longer available"}), 400

        # Check if interview already scheduled for this time slot
        cursor.execute("""
            SELECT id FROM technical_interviews 
            WHERE applicant_id = %s AND job_id = %s AND interview_date = %s AND start_time = %s;
        """, (
            interview_data['applicant_id'], 
            interview_data['job_id'], 
            interview_data['meeting_date'], 
            interview_data['start_time']
        ))
        
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "A technical interview is already scheduled for this time slot"}), 400

        # Insert the technical interview
        cursor.execute("""
            INSERT INTO technical_interviews (
                applicant_id, job_id, meeting_title, interview_date, 
                start_time, end_time
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            interview_data['applicant_id'],
            interview_data['job_id'],
            interview_data['meeting_title'],
            interview_data['meeting_date'],
            interview_data['start_time'],
            interview_data['end_time']
        ))

        interview_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Technical interview scheduled successfully",
            "interview_id": interview_id
        }), 201

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
import traceback
from datetime import timedelta
def safe_serialize_time(val):
    if isinstance(val, timedelta):
        return str(val)
    elif hasattr(val, 'isoformat'):
        return val.isoformat()
    return val
@app.route('/get_interview', methods=['GET'])
def get_interview():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all interviews
        cursor.execute("""
            SELECT 
                id,
                applicant_id,
                job_id,
                meeting_title,
                date,
                start_time,
                end_time,
                created_at,
                questions       
            FROM interviews
            ORDER BY date, start_time
        """)
        
        interviews = []
        for row in cursor.fetchall():
            interview = {
                "id": row[0],
                "applicant_id": row[1],
                "job_id": row[2],
                "meeting_title": row[3],
                "meeting_date": row[4].isoformat() if hasattr(row[4], 'isoformat') else row[4],
                "start_time": safe_serialize_time(row[5]),
                "end_time": safe_serialize_time(row[6]),
                "created_at": safe_serialize_time(row[7]),
                "questions": json.loads(row[8]) if row[8] else [],
            }
            interviews.append(interview)

        # Get all technical interviews
        cursor.execute("""
            SELECT 
                id,
                applicant_id,
                job_id,
                meeting_title,
                date,
                start_time,
                end_time,
                created_at
            FROM technical_interviews
            ORDER BY date, start_time
        """)
        
        technical_interviews = []
        for row in cursor.fetchall():
            interview = {
                "id": row[0],
                "applicant_id": row[1],
                "job_id": row[2],
                "meeting_title": row[3],
                "meeting_date": row[4].isoformat() if hasattr(row[4], 'isoformat') else row[4],
                "start_time": safe_serialize_time(row[5]),
                "end_time": safe_serialize_time(row[6]),
                "created_at": safe_serialize_time(row[7]),
                "is_technical": True
            }
            technical_interviews.append(interview)

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success", 
            "interviews": interviews + technical_interviews
        }), 200

    except Exception as e:
        traceback.print_exc() 
        return jsonify({"status": "error", "message": str(e)}), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


