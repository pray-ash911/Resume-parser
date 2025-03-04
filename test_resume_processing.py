import resume_processing

# Sample resume text
sample_resume = """
**Name:** Pray ash rawal

**Education:**
**Bachelor of Science in Computer Science**
  - XYZ University
  - Graduated: 2023
  
**Skills:**
1. **java:**
   - Proficient in greeting people warmly and establishing friendly interactions.
  
2. **python:**
   - Capable of taking on and fulfilling different roles within a team or project.
  
3. **ai:**
   - Demonstrates heroic qualities, such as bravery and selflessness, in challenging situations.

**Experience:**
- **Ai Developer Intern**
  - ABC Company
  - June 2022 - August 2022
  - Responsibilities:
    - Developed and maintained web applications using Python and Django.
    - Collaborated with the team to design and implement new features.
    - Participated in code reviews and provided constructive feedback.

- **Project Manager**
  - DEF Organization
  - September 2021 - May 2022
  - Responsibilities:
    - Led a team of 5 in developing a healthcare bot for symptom-based diagnosis.
    - Managed project timelines and ensured timely delivery of milestones.
    - Conducted weekly meetings to track progress and address any issues.
"""

# Test the extraction functions
def test_resume_processing():
    name = resume_processing.extract_name(sample_resume)
    skills = resume_processing.extract_skills(sample_resume)
    experience = resume_processing.extract_experience(sample_resume)
    education = resume_processing.extract_education(sample_resume)

    # Test the match_jobs function
    extracted_skills = skills
    match_scores = resume_processing.match_jobs(extracted_skills)

    # Print the results
    print("Extracted Name:", name)
    print("Extracted Skills:", skills)
    print("Extracted Experience:", experience)
    print("Extracted Education:", education)
    print("Match Scores:", match_scores)

test_resume_processing()
