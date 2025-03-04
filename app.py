from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from routes.auth import auth_bp

import os
import nltk
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk
import PyPDF2
from docx import Document
import re
import json
from resume_processing import extract_skills, extract_experience, extract_education, extract_name, score_resume

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

def download_nltk_resources():
    print("Attempting to download NLTK resources...")  # Log the attempt

    resources = [
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'punkt',
        'omw-1.4'
    ]
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)  # Attempt to download resource
        except Exception as e:
            print(f"Error downloading {resource}: {str(e)}")  # Log the error

# Download NLTK resources at startup
download_nltk_resources()

app = Flask(__name__)
app.secret_key = 'd2f1e5b8c9a7f4e3d6c8b9a5f3e2d1c7a6b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2'  # Setting a secret key for session management

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['resume']
    if not file or file.filename == '':
        return "No file selected", 400

    allowed_extensions = {'.txt', '.doc', '.docx', '.pdf'}
    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in allowed_extensions:
        return f"Error: Only {', '.join(allowed_extensions)} files are allowed", 400

    try:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Extract text from different file types
        if file_ext == '.pdf':
            try:
                reader = PyPDF2.PdfReader(file_path)
                resume_text = '\n'.join(page.extract_text() for page in reader.pages)
            except Exception as e:
                return f"Error reading PDF file: {str(e)}", 400
        elif file_ext == '.docx':
            doc = Document(file_path)
            resume_text = '\n'.join(para.text for para in doc.paragraphs)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()

        # Clean up the file after processing
        os.remove(file_path)

        # Process the resume
        skills = sorted(list(extract_skills(resume_text)))
        experience = extract_experience(resume_text)
        education = extract_education(resume_text)

        # Score the resume
        score_report = score_resume(resume_text)

        # Format experience and education for response
        experience = [f"{entry['title']} at {entry['company']} ({entry['duration']})" for entry in experience]
        education = [f"Degree: {entry['degree']} from {entry['institution']} - Graduated: {entry['year']}" for entry in education]

        name = extract_name(resume_text)

        session['extracted_skills'] = skills  # Store extracted skills in session
        response = {
            'name': name,
            'skills': skills,
            'experience': experience,
            'education': education,
            'score_report': score_report  # Include score report in the response
        }

        # Print extraction results for debugging
        print(f"Extracted Name: {response['name']}")
        print(f"Extracted Skills: {response['skills']}")
        print(f"Extracted Experience: {experience}")
        print(f"Extracted Education: {education}")
        print(f"Score Report: {response['score_report']}")  # Log the score report

        # Insert into database if database_operations module is available
        try:
            from database_operations import insert_resume
            insert_resume(response)  # Insert parsed resume data into the database
        except ImportError:
            print("Warning: database_operations module not available. Skipping database insertion.")

        if skills:  # Ensure skills are extracted before rendering results
            return render_template('results.html', 
                                  name=response['name'], 
                                  skills=response['skills'], 
                                  experience=response['experience'], 
                                  education=response['education'],
                                  score_report=response['score_report'])  # Pass score report to the template

    except UnicodeDecodeError:
        return "Error: Could not decode file. Please ensure it's a text file with UTF-8 encoding.", 400
    except Exception as e:
        return f"Error processing file: {str(e)}", 500  # Ensure proper error handling


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/get-match-scores')
def get_match_scores():
    # Load job requirements
    with open('job_requirements.json') as f:
        job_requirements = json.load(f)

    # Retrieve skills from session
    extracted_skills = session.get('extracted_skills', [])
    if not extracted_skills:  # Check if skills are available
        return jsonify({"error": "No skills found. Please process your resume."}), 400

    print(f"Extracted Skills from Session: {extracted_skills}")  # Debugging line to log extracted skills

    matchScores = {}
    for job_title, required_skills in job_requirements.items():
        score = sum(skill in extracted_skills for skill in required_skills)
        matched_skills = [skill for skill in required_skills if skill in extracted_skills]
        matchScores[job_title] = {
            'score': score,
            'matched_skills': matched_skills
        }

    return render_template('match_scores.html', matchScores=matchScores)  # Pass match scores to the template


if __name__ == '__main__':
    app.run(debug=True)
