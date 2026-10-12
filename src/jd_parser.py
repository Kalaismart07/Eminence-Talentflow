import re


SKILL_LIBRARY = [
    "Python",
    "SQL",
    "MySQL",
    "Power BI",
    "Excel",
    "Machine Learning",
    "Data Analysis",
    "Data Visualization",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Flask",
    "Git",
    "Streamlit",
    "TensorFlow",
    "XGBoost",
    "Java",
    "C++",
    "JavaScript",
    "React",
    "HTML",
    "CSS",
]


def extract_required_skills(jd_text):
    """Find known technical skills mentioned in the JD."""

    jd_lower = jd_text.lower()

    found_skills = []

    for skill in SKILL_LIBRARY:
        if skill.lower() in jd_lower:
            found_skills.append(skill)

    return found_skills


def extract_experience_requirement(jd_text):
    """Extract required years of experience."""

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",
        r"minimum\s+(\d+(?:\.\d+)?)\s*years?",
        r"at least\s+(\d+(?:\.\d+)?)\s*years?"
    ]

    jd_lower = jd_text.lower()

    for pattern in patterns:
        match = re.search(pattern, jd_lower)

        if match:
            return float(match.group(1))

    return 0


def extract_education_requirement(jd_text):
    """Identify common education requirements."""

    education_keywords = [
        "b.tech",
        "b.e",
        "be",
        "bachelor",
        "b.sc",
        "bca",
        "m.tech",
        "m.e",
        "master",
        "m.sc",
        "mca",
        "computer science",
        "information technology",
        "artificial intelligence",
        "data science"
    ]

    jd_lower = jd_text.lower()

    found = []

    for keyword in education_keywords:

        if keyword in jd_lower:
            found.append(keyword)

    return list(dict.fromkeys(found))


def parse_job_description(jd_text):

    return {
        "required_skills": extract_required_skills(jd_text),
        "required_experience": extract_experience_requirement(jd_text),
        "education_requirements": extract_education_requirement(jd_text),
        "job_description": jd_text
    }