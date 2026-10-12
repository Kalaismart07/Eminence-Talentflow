import re


def calculate_education_score(education_requirements, candidate_text):
    """
    Calculate education compatibility.
    Related degree terms are treated as compatible.
    """

    if not education_requirements:
        return 100

    text = candidate_text.lower()

    # Related education groups
    degree_groups = {
        "bachelor": [
            "bachelor",
            "b.tech",
            "b.e",
            "b.sc",
            "bca"
        ],
        "computer science": [
            "computer science",
            "cse"
        ],
        "information technology": [
            "information technology",
            "information science",
            "it"
        ],
        "artificial intelligence": [
            "artificial intelligence",
            "ai"
        ],
        "data science": [
            "data science",
            "data analytics"
        ]
    }

    matched_groups = 0
    checked_groups = set()

    for requirement in education_requirements:

        requirement = requirement.lower().strip()

        matched = False

        for group, keywords in degree_groups.items():

            if requirement == group:

                if any(keyword in text for keyword in keywords):
                    matched = True

                checked_groups.add(group)
                break

        if matched:
            matched_groups += 1

    if not education_requirements:
        return 100

    return round(
        (matched_groups / len(education_requirements)) * 100,
        2
    )


def extract_experience_details(text):
    """
    Extract explicit years of experience and internship information.
    """

    text_lower = text.lower()

    years = 0

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+in"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text_lower)

        if matches:

            try:
                years = max(
                    float(value)
                    for value in matches
                )

            except ValueError:
                pass

    internship = any(
        word in text_lower
        for word in [
            "internship",
            "intern",
            "trainee"
        ]
    )

    return years, internship


def calculate_experience_match(
    required_experience,
    candidate_text
):
    """
    Calculate experience compatibility.

    Full-time experience gets full weight.
    Internship/trainee experience receives partial credit.
    """

    if required_experience <= 0:
        return 100

    years, has_internship = extract_experience_details(
        candidate_text
    )

    # Candidate already meets requirement
    if years >= required_experience:
        return 100

    # Partial full-time experience
    if years > 0:
        return round(
            (years / required_experience) * 100,
            2
        )

    # Internship / trainee experience
    if has_internship:
        return 50

    return 0


def generate_candidate_score(
    skill_score,
    education_score,
    experience_score,
    relevance_score
):
    """
    Final recruitment screening score.

    Skills       = 50%
    Education    = 20%
    Experience   = 20%
    Relevance    = 10%
    """

    score = (
        skill_score * 0.50
        + education_score * 0.20
        + experience_score * 0.20
        + relevance_score * 0.10
    )

    return round(score, 2)


def get_candidate_status(score):

    if score >= 75:
        return "Shortlisted"

    elif score >= 60:
        return "Under Review"

    else:
        return "Not Recommended"