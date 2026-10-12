import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_skill(skill):
    """Normalize skill names for comparison."""
    return skill.lower().strip()


def calculate_skill_match(required_skills, candidate_skills):
    """Calculate percentage of required skills found in candidate profile."""

    if not required_skills:
        return 0

    required = {
        normalize_skill(skill)
        for skill in required_skills
    }

    candidate = {
        normalize_skill(skill)
        for skill in candidate_skills
    }

    matched = required.intersection(candidate)

    score = (len(matched) / len(required)) * 100

    return round(score, 2)


def extract_years_of_experience(text):
    """
    Extract simple year-based experience mentions.
    Returns 0 if no experience information is found.
    """

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience",
        r"(\d+(?:\.\d+)?)\+?\s*years?"
    ]

    text_lower = text.lower()

    for pattern in patterns:

        matches = re.findall(pattern, text_lower)

        if matches:
            try:
                return max(float(value) for value in matches)
            except ValueError:
                pass

    return 0


def calculate_experience_match(required_experience, candidate_text):
    """Compare required experience with candidate experience."""

    if required_experience <= 0:
        return 100

    candidate_experience = extract_years_of_experience(candidate_text)

    if candidate_experience >= required_experience:
        return 100

    if candidate_experience > 0:
        return round(
            (candidate_experience / required_experience) * 100,
            2
        )

    return 0


def calculate_text_relevance(jd_text, candidate_text):
    """Calculate semantic text similarity using TF-IDF."""

    if not jd_text.strip() or not candidate_text.strip():
        return 0

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        [jd_text, candidate_text]
    )

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return round(similarity * 100, 2)


def calculate_final_score(
    skill_score,
    education_score,
    experience_score,
    relevance_score
):
    """
    Calculate final candidate score.

    Weight:
    Skills       = 50%
    Education    = 20%
    Experience   = 20%
    Relevance    = 10%
    """

    final_score = (
        skill_score * 0.50
        + education_score * 0.20
        + experience_score * 0.20
        + relevance_score * 0.10
    )

    return round(final_score, 2)


def get_recommendation(score):

    if score >= 80:
        return "Shortlisted"

    if score >= 60:
        return "Under Review"

    return "Not Recommended"