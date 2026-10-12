from resume_parser import parse_resume
from jd_parser import parse_job_description
from matching_engine import (
    calculate_skill_match,
    calculate_text_relevance
)
from scoring import (
    calculate_education_score,
    calculate_experience_match,
    generate_candidate_score,
    get_candidate_status
)


# -----------------------------
# 1. LOAD RESUME
# -----------------------------

file_path = "../data/resumes/KALAIYARASU_S_Resume_Fresh.pdf.pdf"

with open(file_path, "rb") as file:
    candidate = parse_resume(file)


# -----------------------------
# 2. JOB DESCRIPTION
# -----------------------------

jd_text = """
Junior Data Analyst

Requirements:
Bachelor's degree in Computer Science,
Artificial Intelligence, Data Science or related field.

Required skills:
Python, SQL, Excel, Power BI and Data Analysis.

Candidates should have 1 year of experience.
"""


# -----------------------------
# 3. PARSE JD
# -----------------------------

job = parse_job_description(jd_text)


# -----------------------------
# 4. CALCULATE MATCHING
# -----------------------------

skill_score = calculate_skill_match(
    job["required_skills"],
    candidate["skills"]
)

education_score = calculate_education_score(
    job["education_requirements"],
    candidate["text"]
)

experience_score = calculate_experience_match(
    job["required_experience"],
    candidate["text"]
)

relevance_score = calculate_text_relevance(
    job["job_description"],
    candidate["text"]
)


# -----------------------------
# 5. FINAL SCORE
# -----------------------------

final_score = generate_candidate_score(
    skill_score,
    education_score,
    experience_score,
    relevance_score
)

status = get_candidate_status(final_score)


# -----------------------------
# 6. DISPLAY RESULT
# -----------------------------

print("\n======================================")
print("       RECRUITFLOW SCREENING")
print("======================================")

print("\nCandidate:")
print(candidate["name"])

print("\nRequired Skills:")
print(job["required_skills"])

print("\nCandidate Skills:")
print(candidate["skills"])

print("\n--------------------------------------")
print("MATCHING RESULTS")
print("--------------------------------------")

print(f"Skill Match       : {skill_score}%")
print(f"Education Match   : {education_score}%")
print(f"Experience Match  : {experience_score}%")
print(f"Text Relevance    : {relevance_score}%")

print("--------------------------------------")

print(f"FINAL MATCH SCORE  : {final_score}%")
print(f"RECOMMENDATION     : {status}")

print("======================================")