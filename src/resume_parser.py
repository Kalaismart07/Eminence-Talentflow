import re
import pymupdf


def extract_text_from_pdf(file):
    """Extract text from a PDF resume."""

    pdf_bytes = file.read()

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    for page in document:
        text = page.get_text("text")

        if text:
            pages.append(text)

    document.close()

    return "\n".join(pages).strip()


def clean_text(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def extract_email(text):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern, text)

    return match.group(0) if match else "Not found"


def extract_phone(text):
    pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    return match.group(0) if match else "Not found"


def extract_candidate_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:10]:

        if (
            len(line.split()) <= 5
            and not any(char.isdigit() for char in line)
            and "@" not in line
            and not line.lower().startswith(
                ("linkedin", "github", "www")
            )
        ):
            return line

    return "Name not found"


def extract_skills(text):

    skill_list = [
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
        "XGBoost"
    ]

    text_lower = text.lower()

    found_skills = []

    for skill in skill_list:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def parse_resume(file):

    raw_text = extract_text_from_pdf(file)

    text = clean_text(raw_text)

    return {
        "name": extract_candidate_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "text": text
    }