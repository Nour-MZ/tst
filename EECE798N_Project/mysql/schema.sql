-- Create and use the database

CREATE DATABASE IF NOT EXISTS eece798;
USE eece798;



-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    user_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applicant CV table
CREATE TABLE IF NOT EXISTS applicant_cv (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    education JSON,
    skills JSON,
    experience JSON,
    experience_years INT,
    projects JSON,
    certifications JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    job_level VARCHAR(100) NOT NULL,
    years_experience VARCHAR(50) NOT NULL,
    requirements JSON NOT NULL,
    responsibilities JSON NOT NULL,
    required_certifications JSON,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    date_offered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    CONSTRAINT chk_status CHECK (status IN ('open', 'closed'))
);

-- Applied jobs table
CREATE TABLE IF NOT EXISTS applied_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    job_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    scores JSON,
    thresholds JSON,
    meets_threshold JSON,
    passed_criteria VARCHAR(10),
    qualified_cv BOOLEAN,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE (applicant_id, job_id)
);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    job_id INT NOT NULL,
    meeting_title VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    questions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE (applicant_id, job_id, date, start_time)
);

-- Interview answers
CREATE TABLE IF NOT EXISTS interview_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    answers JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

-- Answer evaluations
CREATE TABLE IF NOT EXISTS answer_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    answer_id INT NOT NULL,
    avg_score_requirements FLOAT,
    avg_score_responsibilities FLOAT,
    full_evaluation TEXT,
    qualified_interview BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (answer_id) REFERENCES interview_answers(id) ON DELETE CASCADE
);

-- Technical interviews
CREATE TABLE IF NOT EXISTS technical_interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    job_id INT NOT NULL,
    meeting_title VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE (applicant_id, job_id, date, start_time)
);

-- Best matches
CREATE TABLE IF NOT EXISTS best_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    job_id INT NOT NULL,
    evaluation JSON,
    match_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Pending decisions
CREATE TABLE IF NOT EXISTS pending_decisions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    job_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE (applicant_id, job_id)
);
