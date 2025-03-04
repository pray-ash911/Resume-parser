import json
import re
import nltk
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk

# Common technical skills and frameworks
TECHNICAL_SKILLS = {
    'languages': {'python', 'java', 'javascript', 'c++', 'ruby', 'php', 'swift', 'kotlin', 'golang', 'typescript', 'c#', 'r', 'scala', 'perl', 'matlab', 'bash', 'sql'},
    'frameworks': {'django', 'flask', 'react', 'angular', 'vue', 'spring', 'laravel', 'express', 'bootstrap', 'jquery', 'node.js', 'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scikit-learn', 'next.js', 'gatsby', 'symfony', 'rails', 'xamarin', 'flutter', 'ionic'},
    'databases': {'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'oracle', 'sql server', 'dynamodb', 'cassandra', 'couchbase', 'mariadb', 'neo4j', 'firebase', 'supabase'},
    'tools': {'git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'linux', 'nginx', 'ansible', 'terraform', 'jira', 'figma', 'photoshop', 'illustrator', 'sketch', 'salesforce', 'tableau', 'power bi', 'grafana', 'prometheus', 'elasticsearch', 'kibana', 'logstash'},
    'other': {'rest api', 'graphql', 'microservices', 'ci/cd', 'agile', 'scrum', 'kanban', 'devops', 'machine learning', 'artificial intelligence', 'data science', 'cloud computing', 'responsive design', 'web accessibility', 'pwa', 'seo'}
}

def download_nltk_resources():
    resources = [
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'punkt',
        'omw-1.4'
    ]
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Error downloading {resource}: {str(e)}")

def match_jobs(extracted_skills):
    total_required_skills = 0
    total_matched_skills = 0

    matched_skills = {}

    """Match extracted skills against job requirements."""
    with open('job_requirements.json', 'r') as f:
        job_requirements = json.load(f)

    match_scores = {}
    for job_title, required_skills in job_requirements.items():
        score = sum(skill in extracted_skills for skill in required_skills)
        matched_skills[job_title] = {
            'matched': [skill for skill in required_skills if skill in extracted_skills],
            'total_required': len(required_skills)
        }
        total_required_skills += len(required_skills)
        total_matched_skills += len(matched_skills[job_title]['matched'])

        match_scores[job_title] = score, matched_skills[job_title]


    match_percentage = (total_matched_skills / total_required_skills * 100) if total_required_skills > 0 else 0
    return match_scores, total_matched_skills, total_required_skills, match_percentage


def extract_skills(text):

    """Extract technical skills from text using predefined lists and patterns.
    This function now allows for more flexible matching of skills, including handling descriptions and synonyms.
    """

    skills = set()  # Initialize an empty set to store extracted skills
    skill_descriptions = {
        'java': 'Proficient in greeting people warmly and establishing friendly interactions.',
        'python': 'Capable of taking on and fulfilling different roles within a team or project.',
        'ai': 'Demonstrates heroic qualities, such as bravery and selflessness, in challenging situations.'
    }

    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    # Try to load external skills database if it exists
    try:
        with open('skills_database.json', 'r') as f:
            skills_db = set(json.load(f))
        
        # Extract skills from database
        for skill in skills_db:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                skills.add(skill)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, continue with predefined skills
        pass
    
    # Extract skills from all categories and descriptions
    for category in TECHNICAL_SKILLS.values():
        for skill in category:
            # Use word boundary matching to avoid partial matches
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills.add(skill)
    
    # Look for version numbers attached to skills (e.g., Python 3.8)
    version_pattern = r'\b(\w+)\s+\d+(\.\d+)*\b'
    version_matches = re.finditer(version_pattern, text_lower)
    for match in version_matches:
        skill = match.group(1).lower()
        if any(skill in category for category in TECHNICAL_SKILLS.values()):
            skills.add(match.group(0))
    
    # Add skills from descriptions if they match
    for skill, description in skill_descriptions.items():
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            skills.add(skill)
    
    return skills  # Return the set of extracted skills



def extract_experience(text):
    """Extract work experience with improved detection.
    This function now captures responsibilities and formats them appropriately.
    """

    experience_entries = []  # Initialize an empty list to store experience entries

    # Pattern to identify experience sections
    experience_section_pattern = r'(?:Experience|Employment|Work Experience|Professional Experience).*?(?:\n\n|\Z)'
    experience_sections = re.findall(experience_section_pattern, text, re.DOTALL | re.IGNORECASE)
    
    # If no sections found, use the whole text
    if not experience_sections:
        experience_sections = [text]
    
    # For each section, look for experience entries
    for section in experience_sections:
        # Pattern for job title - company - duration format
        experience_pattern = r'(?:^|\n)\s*-\s*\*\*(?P<title>[A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Specialist|Consultant|Intern|Lead))\*\*\s*(?:-|at|with|for)?\s*(?:\*\*)?(?P<company>[A-Z][A-Za-z\s]+)(?:\*\*)?\s*(?:-|,|\n)?\s*(?:(?P<start_date>\w+\s+\d{4})\s*(?:-|to|–|until)\s*(?P<end_date>\w+\s+\d{4}|[Pp]resent|[Cc]urrent))?'
        
        # Find all experience entries
        exp_matches = list(re.finditer(experience_pattern, section, re.MULTILINE | re.IGNORECASE))
        
        # Process each experience match
        for match in exp_matches:
            exp_info = {}
            if match.group('title'):
                exp_info['title'] = match.group('title').strip()
            if match.group('company'):
                exp_info['company'] = match.group('company').strip()
            if match.group('start_date') and match.group('end_date'):
                exp_info['duration'] = f"{match.group('start_date')} - {match.group('end_date')}"
            
            # Extract responsibilities from text following the job entry
            match_end = match.end()
            next_match_start = len(section) if match == exp_matches[-1] else exp_matches[exp_matches.index(match) + 1].start()
            responsibilities_text = section[match_end:next_match_start]
            
            # Find bullet points as responsibilities
            responsibilities = re.findall(r'(?:^|\n)\s*[•\-*]\s*(.+?)(?=\n\s*[•\-*]|\n\n|\Z)', responsibilities_text, re.DOTALL)
            if responsibilities:
                exp_info['responsibilities'] = [resp.strip() for resp in responsibilities]
            
            if exp_info:
                experience_entries.append(exp_info)
    
    # Format experience entries correctly
    formatted_experience = []
    for entry in experience_entries:
        formatted_entry = {
            'title': entry.get('title', ''),
            'company': entry.get('company', ''),
            'duration': entry.get('duration', ''),
            'responsibilities': ", ".join(entry.get('responsibilities', []))
        }
        formatted_experience.append(formatted_entry)
    
    return formatted_experience  # Return the formatted experience entries



def extract_education(text):
    """Extract education information with improved detection.
    This function ensures it captures the degree, institution, and graduation year accurately.
    """

    education_entries = []  # Initialize an empty list to store education entries

    # Pattern to identify education sections
    education_section_pattern = r'(?:Education|Academic Background|Qualifications).*?(?:\n\n|\Z)|(?:\*\*Education\*\*).*?(?:\n\n|\Z)'
    education_sections = re.findall(education_section_pattern, text, re.DOTALL | re.IGNORECASE)
    
    # If no sections found, use the whole text
    if not education_sections:
        education_sections = [text]
    
    # For each section, look for education entries
    for section in education_sections:
        # Pattern for degree - institution - date format
        education_pattern = r'(?:^|\n)\s*-\s*\*\*(?P<degree>[A-Za-z\s]+(?:Bachelor|Master|PhD|BSc|MSc|MBA|BE|BTech|MTech|B\.S\.|M\.S\.))\*\*\s*(?:-|at|from)?\s*(?:\*\*)?(?P<institution>[A-Z][A-Za-z\s]+(?:University|College|Institute|School))(?:\*\*)?\s*(?:-|,|\n)?\s*(?:(?:Graduated|Graduation):?\s*(?P<year>\d{4}))?'
        
        # Find all education entries
        edu_matches = list(re.finditer(education_pattern, section, re.MULTILINE | re.IGNORECASE))
        
        # Process each education match
        for match in edu_matches:
            edu_info = {}
            if match.group('degree'):
                edu_info['degree'] = match.group('degree').strip()
            if match.group('institution'):
                edu_info['institution'] = match.group('institution').strip()
            if match.group('year'):
                edu_info['year'] = match.group('year').strip()
            
            if edu_info:
                education_entries.append(edu_info)
    
    # Format education entries correctly
    formatted_education = []
    for entry in education_entries:
        formatted_entry = f"Degree: {entry.get('degree', '')} from {entry.get('institution', '')} - Graduated: {entry.get('year', '')}"
        formatted_education.append(formatted_entry)
    
    return formatted_education  # Return the formatted education entries


def extract_name(text):
    """Extract name with improved detection.
    This function ensures it captures names in various formats.
    """

    # Look for "Name:" pattern first
    name_pattern = r'(?:^|\n)(?:\*\*)?[Nn]ame(?:\*\*)?:?\s*(?:\*\*)?([A-Z][a-zA-Z\s]+(?:\s[A-Z][a-zA-Z]+)*)?(?:\*\*)?'




    name_match = re.search(name_pattern, text)
    if name_match:
        return name_match.group(1)  # Removed strip()
    
    # Try to find name at the beginning of the resume
    first_lines = text.split('\n')[:5]
    for line in first_lines:
        # Look for a line with 2-3 words, all capitalized or starting with capital
        words = line.strip().split()
        if 2 <= len(words) <= 3 and all(word[0].isupper() for word in words if word):
            name_candidate = ' '.join(words)
            # Avoid returning section headers or dates
            if not any(term in name_candidate.lower() for term in ['resume', 'cv', 'education', 'experience', 'skills']):
                return name_candidate
    
    # Fallback to NLTK named entity recognition
    try:
        download_nltk_resources()  # Make sure NLTK resources are downloaded
        tokens = word_tokenize(text[:500])  # Only check the beginning
        entities = ne_chunk(pos_tag(tokens))
        for chunk in entities:
            if isinstance(chunk, nltk.Tree) and chunk.label() == 'PERSON':
                person_name = ' '.join([c[0] for c in chunk.leaves()])
                # Avoid single names or very long names
                if ' ' in person_name and len(person_name.split()) <= 3:
                    return person_name
    except Exception as e:
        print(f"Error in NLTK processing: {str(e)}")
    
    return 'Not found'

# Example usage function
def score_resume(resume_text):
    """Score a resume based on matched skills against job requirements."""
    skills = extract_skills(resume_text)
    match_scores, total_matched, total_required, match_percentage = match_jobs(skills)
    
    return {
        'match_scores': match_scores,
        'total_matched': total_matched,
        'total_required': total_required,
        'match_percentage': match_percentage
    }

def process_resume(resume_text):

    """Process a resume text and extract key information."""
    name = extract_name(resume_text)
    skills = extract_skills(resume_text)
    experience = extract_experience(resume_text)
    education = extract_education(resume_text)
    
    return {
        'name': name,
        'skills': list(skills),
        'experience': experience,
        'education': education
    }
