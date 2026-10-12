from jd_parser import parse_job_description


jd = """
We are looking for a Junior Python Developer.

Requirements:
Bachelor's degree in Computer Science or Information Technology.

Required skills:
Python, SQL, Flask, Git and MySQL.

Candidates should have 1 year of experience.
"""


result = parse_job_description(jd)


print("\n==============================")
print("       JD PARSER TEST")
print("==============================")

print("\nRequired Skills:")
for skill in result["required_skills"]:
    print(" -", skill)

print("\nRequired Experience:",
      result["required_experience"], "years")

print("\nEducation Requirements:")
for education in result["education_requirements"]:
    print(" -", education)