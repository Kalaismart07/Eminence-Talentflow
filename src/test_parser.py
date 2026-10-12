from resume_parser import parse_resume



file_path = "../data/resumes/KALAIYARASU_S_Resume_Fresh.pdf.pdf"


with open(file_path, "rb") as file:

    result = parse_resume(file)


print("\n==============================")
print("     RESUME SCREENING TEST")
print("==============================")

print("\nCandidate Name :", result["name"])
print("Email          :", result["email"])
print("Phone          :", result["phone"])

print("\nSkills Found:")
for skill in result["skills"]:
    print(" -", skill)

print("\nResume Text Preview:")
print("------------------------------")
print(result["text"][:1000])
print("------------------------------")