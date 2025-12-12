import re
from docx import Document
from PyPDF2 import PdfReader

class ResumeParser:
    """Extract skills, experience, and education from resumes"""

    # Add your skill keywords here or load from a JSON
    SKILLS_KEYWORDS = [
        "Python", "Django", "Flask", "JavaScript", "React", "Node.js", "MongoDB",
        "SQL", "Flutter", "Unity", "C++", "Java", "Git", "Docker", "AWS"
    ]

    EDUCATION_KEYWORDS = [
        "Bachelor", "Master", "B.Tech", "B.E", "M.Tech", "MBA", "PhD", "Diploma"
    ]

    EXPERIENCE_REGEX = r'(\d+)\s+(?:years|yrs|year)'

    @staticmethod
    def extract_text(file):
        """Extract text from PDF or DOCX file"""
        if file.name.endswith('.pdf'):
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif file.name.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        else:
            return ""

    @classmethod
    def parse_resume(cls, file):
        text = cls.extract_text(file)
        text_lower = text.lower()

        # Extract skills
        skills = [skill for skill in cls.SKILLS_KEYWORDS if skill.lower() in text_lower]

        # Extract experience
        experience_matches = re.findall(cls.EXPERIENCE_REGEX, text_lower)
        experience_years = max([int(e) for e in experience_matches], default=0) if experience_matches else None

        # Extract education
        education = []
        for keyword in cls.EDUCATION_KEYWORDS:
            if keyword.lower() in text_lower:
                education.append(keyword)

        return {
            "skills": skills,
            "experience_years": experience_years,
            "education": ", ".join(education)
        }
