import streamlit as st
import sys
import os
import json
from src.database import (
    init_db,
    migrate_json_results,
    get_candidates,
    save_screening_candidates,
    update_candidate_stage,
)

# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

# ---------------------------------------------------------
# DATA STORAGE
# ---------------------------------------------------------

DATA_DIR = os.path.join(BASE_DIR, "data")

RESULTS_FILE = os.path.join(
    DATA_DIR,
    "screening_results.json"
)


def load_screening_results():

    if not os.path.exists(RESULTS_FILE):
        return []

    try:

        with open(
            RESULTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_screening_results(results):

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# ---------------------------------------------------------
# IMPORT PROJECT MODULES
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="RecruitFlow",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""

<style>
:root {
    --brand: #2563eb;
    --brand-dark: #1d4ed8;
    --page-bg: #f5f8fc;
    --surface: #ffffff;
    --text: #172033;
    --muted: #64748b;
    --border: #e2e8f0;
}

.stApp {
    background: var(--page-bg);
    color: var(--text);
}

[data-testid="stAppViewContainer"] {
    background: var(--page-bg);
}

[data-testid="stHeader"] {
    background: rgba(245, 248, 252, 0.92);
}

.block-container {
    max-width: 1500px;
    padding-top: 1.7rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

h1, h2, h3 {
    color: var(--text) !important;
    letter-spacing: -0.025em;
}

h1 {
    font-size: 2rem !important;
    font-weight: 750 !important;
}

h2 {
    font-size: 1.35rem !important;
}

h3 {
    font-size: 1.05rem !important;
}

p, label, [data-testid="stMarkdownContainer"] {
    color: var(--text);
}

[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.025);
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-size: 0.85rem;
}

[data-testid="stMetricValue"] {
    color: var(--text);
    font-weight: 750;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: 12px !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
    border-color: var(--border);
}

.stButton > button[kind="primary"] {
    background: var(--brand);
    color: #ffffff;
    border-color: var(--brand);
}

.stButton > button[kind="primary"]:hover {
    background: var(--brand-dark);
    border-color: var(--brand-dark);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 8px;
}

.candidate-card {
    background: var(--surface);
    color: var(--text);
    padding: 14px 18px;
    margin-bottom: 10px;
    border-radius: 10px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.025);
}

.candidate-card b {
    color: var(--text);
}

.candidate-card span {
    color: var(--muted);
}

.score {
    font-size: 26px;
    font-weight: 750;
    color: var(--brand);
}

.shortlisted {
    color: #15803d;
    font-weight: 700;
}

.review {
    color: #b45309;
    font-weight: 700;
}

.rejected {
    color: #b91c1c;
    font-weight: 700;
}

hr {
    border-color: var(--border);
}
</style>

""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## Eminence TalentFlow")
    st.caption("Recruitment Screening Platform")

    st.divider()

    

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Jobs",
            "Candidates",
            "Job Requirements",
            "Candidate Screening",
            "Shortlisted Candidates",
            "Reports",
        ],
    )

    st.divider()
    st.caption("Recruitment Automation")
    st.caption("Screening · Ranking · Pipeline")

    st.caption("Resume Screening • Ranking • Shortlisting")


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

# Initialize SQLite and import legacy JSON records once
init_db()

if "database_migrated" not in st.session_state:
    migrate_json_results()
    st.session_state.database_migrated = True

if "screening_results" not in st.session_state:
    st.session_state.screening_results = load_screening_results()

if "job_data" not in st.session_state:

    st.session_state.job_data = None


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("Recruitment Dashboard")

    st.write(
        "Monitor candidate screening and recruitment progress."
    )

    results = st.session_state.screening_results

    total_candidates = len(results)

    shortlisted = sum(
        1 for r in results
        if r["status"] == "Shortlisted"
    )

    under_review = sum(
        1 for r in results
        if r["status"] == "Under Review"
    )

    not_recommended = sum(
        1 for r in results
        if r["status"] == "Not Recommended"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Candidates Screened",
            total_candidates
        )

    with col2:
        st.metric(
            "Shortlisted",
            shortlisted
        )

    with col3:
        st.metric(
            "Under Review",
            under_review
        )

    with col4:
        st.metric(
            "Not Recommended",
            not_recommended
        )

    st.divider()


    st.subheader("Recent Candidates")
    st.caption("Latest resume screening outcomes")

    if results:
        import pandas as pd

        recent_rows = []
        for result in results[:5]:
            recent_rows.append({
                "Candidate": result.get("name", "Unknown"),
                "Email": result.get("email", ""),
                "Match Score": f'{float(result.get("final_score", 0)):.1f}%',
                "Recommendation": result.get("status", "Under Review"),
            })

        st.dataframe(
            pd.DataFrame(recent_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No candidates screened yet. "
            "Go to Candidate Screening to start."
        )



# =========================================================
# JOB REQUIREMENTS
# =========================================================

elif page == "Candidates":

    st.title("Candidates")
    st.caption("Manage applicants, review screening scores, and update recruitment stages.")

    candidates = get_candidates()

    if not candidates:
        st.info("No candidates in the database yet. Screen resumes to get started.")
    else:
        search_text = st.text_input(
            "Search candidates",
            placeholder="Search by candidate name, email, or skill"
        )

        stages = [
            "All stages", "Screening", "Shortlisted",
            "Interview", "Offer", "Hired", "Rejected"
        ]

        col_filter, col_sort = st.columns([2, 2])

        with col_filter:
            selected_stage = st.selectbox("Recruitment stage", stages)

        with col_sort:
            sort_option = st.selectbox(
                "Sort candidates",
                ["Highest match score", "Lowest match score", "Name A–Z"]
            )

        filtered_candidates = []

        for candidate in candidates:
            searchable = " ".join([
                str(candidate.get("name", "")),
                str(candidate.get("email", "")),
                " ".join(candidate.get("skills", []))
            ]).lower()

            if search_text.lower() not in searchable:
                continue

            if (
                selected_stage != "All stages"
                and candidate.get("stage", "Screening") != selected_stage
            ):
                continue

            filtered_candidates.append(candidate)

        if sort_option == "Lowest match score":
            filtered_candidates.sort(key=lambda c: c.get("final_score", 0))
        elif sort_option == "Name A–Z":
            filtered_candidates.sort(key=lambda c: c.get("name", "").lower())
        else:
            filtered_candidates.sort(
                key=lambda c: c.get("final_score", 0),
                reverse=True
            )

        st.write(f"**{len(filtered_candidates)} candidates**")

        if filtered_candidates:
            import pandas as pd

            table_rows = []
            for candidate in filtered_candidates:
                table_rows.append({
                    "ID": candidate["id"],
                    "Candidate": candidate.get("name", ""),
                    "Email": candidate.get("email", ""),
                    "Skills": ", ".join(candidate.get("skills", [])),
                    "Match score": f'{candidate.get("final_score", 0):.1f}%',
                    "Stage": candidate.get("stage", "Screening"),
                })

            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True
            )

            candidate_options = {
                f'{c["name"]} — {c.get("email", "No email")} (ID {c["id"]})': c
                for c in filtered_candidates
            }

            selected_label = st.selectbox(
                "Open candidate profile",
                list(candidate_options.keys())
            )

            selected_candidate = candidate_options[selected_label]

            st.divider()
            st.subheader(selected_candidate.get("name", "Candidate profile"))

            detail_col, score_col = st.columns([2, 1])

            with detail_col:
                st.write("**Contact details**")
                st.write(f'Email: {selected_candidate.get("email") or "Not available"}')
                st.write(f'Phone: {selected_candidate.get("phone") or "Not available"}')

                st.write("**Skills**")
                st.write(", ".join(selected_candidate.get("skills", [])) or "No skills extracted")

                st.write("**Matched skills**")
                st.write(", ".join(selected_candidate.get("matched_skills", [])) or "None recorded")

                st.write("**Missing skills**")
                st.write(", ".join(selected_candidate.get("missing_skills", [])) or "None recorded")

            with score_col:
                st.metric("Final match score", f'{selected_candidate.get("final_score", 0):.1f}%')
                st.metric("Skill match", f'{selected_candidate.get("skill_score", 0):.1f}%')
                st.metric("Education match", f'{selected_candidate.get("education_score", 0):.1f}%')
                st.metric("Experience match", f'{selected_candidate.get("experience_score", 0):.1f}%')
                st.metric("Text relevance", f'{selected_candidate.get("relevance_score", 0):.1f}%')

            st.divider()
            st.subheader("Recruiter decision")

            valid_stages = [
                "Screening", "Shortlisted", "Interview",
                "Offer", "Hired", "Rejected"
            ]

            current_stage = selected_candidate.get("stage", "Screening")

            with st.form(f'candidate_stage_form_{selected_candidate["id"]}'):
                new_stage = st.selectbox(
                    "Move candidate to",
                    valid_stages,
                    index=valid_stages.index(current_stage)
                    if current_stage in valid_stages else 0
                )
                recruiter_note = st.text_input("Recruiter note (optional)")
                save_stage = st.form_submit_button(
                    "Save recruitment stage",
                    type="primary"
                )

            if save_stage:
                update_candidate_stage(
                    selected_candidate["id"],
                    new_stage,
                    recruiter_note
                )
                st.success("Recruitment stage saved to SQLite.")
                st.rerun()
        else:
            st.info("No candidates match these filters.")

elif page == "Job Requirements":

    st.title("Job Requirements")

    st.write(
        "Define the job requirements used for candidate screening."
    )

    job_title = st.text_input(
        "Job Title",
        placeholder="Example: Junior Data Analyst"
    )

    jd_text = st.text_area(
        "Job Description",
        height=300,
        placeholder="""Paste the complete job description here...

Example:

Bachelor's degree in Computer Science,
Artificial Intelligence, Data Science or related field.

Required skills:
Python, SQL, Excel, Power BI and Data Analysis.

Candidates should have 1 year of experience."""
    )

    if st.button(
        "Save Job Requirements",
        type="primary"
    ):

        if not jd_text.strip():

            st.warning(
                "Please enter a job description."
            )

        else:

            job_data = parse_job_description(
                jd_text
            )

            st.session_state.job_data = {
                "title": job_title,
                "data": job_data
            }

            st.success(
                "Job requirements saved successfully."
            )

    if st.session_state.job_data:

        st.divider()

        st.subheader("Parsed Requirements")

        job = st.session_state.job_data["data"]

        col1, col2 = st.columns(2)

        with col1:

            st.write("**Required Skills**")

            for skill in job["required_skills"]:
                st.write(f"• {skill}")

        with col2:

            st.write(
                "**Experience Required:** "
                f"{job['required_experience']} years"
            )

            st.write("**Education Requirements**")

            for education in job["education_requirements"]:
                st.write(f"• {education}")


# =========================================================
# CANDIDATE SCREENING
# =========================================================

elif page == "Candidate Screening":

    st.title("Candidate Screening")

    st.write(
        "Upload candidate resumes and automatically "
        "compare them against the selected job requirements."
    )

    if not st.session_state.job_data:

        st.warning(
            "Please configure Job Requirements first."
        )

    else:

        job_info = st.session_state.job_data

        st.info(
            f"Active Position: **{job_info['title']}**"
        )

        uploaded_files = st.file_uploader(
            "Upload Candidate Resumes",
            type=["pdf"],
            accept_multiple_files=True
        )

        if uploaded_files:

            st.write(
                f"**{len(uploaded_files)} resume(s) uploaded**"
            )

        if st.button(
            "🚀 Start Screening",
            type="primary",
            disabled=not uploaded_files
        ):

            job = job_info["data"]

            results = []

            progress = st.progress(0)

            for index, uploaded_file in enumerate(
                uploaded_files
            ):

                try:

                    candidate = parse_resume(
                        uploaded_file
                    )

                    # -----------------------------
                    # SCORE COMPONENTS
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

                    final_score = generate_candidate_score(
                        skill_score,
                        education_score,
                        experience_score,
                        relevance_score
                    )

                    status = get_candidate_status(
                        final_score
                    )

                    # -----------------------------
                    # MATCHED / MISSING SKILLS
                    # -----------------------------

                    required_skills_lower = {
                        skill.lower()
                        for skill in job["required_skills"]
                    }

                    candidate_skills_lower = {
                        skill.lower()
                        for skill in candidate["skills"]
                    }

                    matched_skills = [
                        skill
                        for skill in job["required_skills"]
                        if skill.lower()
                        in candidate_skills_lower
                    ]

                    missing_skills = [
                        skill
                        for skill in job["required_skills"]
                        if skill.lower()
                        not in candidate_skills_lower
                    ]

                    results.append({

                        "name": candidate["name"],

                        "email": candidate["email"],

                        "phone": candidate["phone"],

                        "skills": candidate["skills"],

                        "matched_skills": matched_skills,

                        "missing_skills": missing_skills,

                        "skill_score": skill_score,

                        "education_score": education_score,

                        "experience_score": experience_score,

                        "relevance_score": relevance_score,

                        "final_score": final_score,

                        "status": status

                    })

                except Exception as e:

                    st.error(
                        f"Error processing "
                        f"{uploaded_file.name}: {e}"
                    )

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )
            
            # -----------------------------
            
            # ADD NEW RESULTS
            # -----------------------------

            # Save newly screened candidates to SQLite
            saved_count = save_screening_candidates(results)

            # Keep the existing JSON workflow working for now
            existing_results = st.session_state.screening_results
            existing_results.extend(results)
            existing_results.sort(
                key=lambda x: x["final_score"],
                reverse=True
            )

            st.session_state.screening_results = existing_results
            save_screening_results(existing_results)



            st.success(
                f"Screening completed for "
                f"{len(results)} candidate(s)."
            )

        # -------------------------------------------------
        # DISPLAY RESULTS
        # -------------------------------------------------

        results = st.session_state.screening_results

        if results:

            st.divider()

            st.subheader("Screening Results")

            for rank, result in enumerate(
                results,
                start=1
            ):

                with st.container():

                    col1, col2, col3 = st.columns(
                        [5, 2, 2]
                    )

                    with col1:

                        st.markdown(
                            f"### #{rank} {result['name']}"
                        )

                        st.caption(
                            f"{result['email']}"
                        )

                    with col2:

                        st.metric(
                            "Match Score",
                            f"{result['final_score']}%"
                        )

                    with col3:

                        if result["status"] == "Shortlisted":

                            st.success(
                                result["status"]
                            )

                        elif result["status"] == "Under Review":

                            st.warning(
                                result["status"]
                            )

                        else:

                            st.error(
                                result["status"]
                            )

                    with st.expander(
                        "View Screening Details"
                    ):

                        score_col1, score_col2 = st.columns(2)

                        with score_col1:

                            st.write(
                                f"**Skill Match:** "
                                f"{result['skill_score']}%"
                            )

                            st.write(
                                f"**Education Match:** "
                                f"{result['education_score']}%"
                            )

                        with score_col2:

                            st.write(
                                f"**Experience Match:** "
                                f"{result['experience_score']}%"
                            )

                            st.write(
                                f"**Text Relevance:** "
                                f"{result['relevance_score']}%"
                            )

                        st.divider()

                        st.write(
                            "**Matched Skills**"
                        )

                        if result["matched_skills"]:

                            st.write(
                                ", ".join(
                                    result["matched_skills"]
                                )
                            )

                        else:

                            st.write("None")

                        st.write(
                            "**Missing Skills**"
                        )

                        if result["missing_skills"]:

                            st.write(
                                ", ".join(
                                    result["missing_skills"]
                                )
                            )

                        else:

                            st.write("None")

                    st.divider()


# =========================================================
# SHORTLISTED CANDIDATES
# =========================================================

elif page == "Shortlisted Candidates":

    st.title("Shortlisted Candidates")

    results = st.session_state.screening_results

    shortlisted = [
        result
        for result in results
        if result["status"] == "Shortlisted"
    ]

    if not shortlisted:

        st.info(
            "No shortlisted candidates yet."
        )

    else:

        for rank, candidate in enumerate(
            shortlisted,
            start=1
        ):

            st.markdown(
                f"""
                ### {rank}. {candidate["name"]}

                **Match Score:** {candidate["final_score"]}%

                **Email:** {candidate["email"]}

                **Skills:** {", ".join(candidate["skills"])}

                ---
                """
            )


# =========================================================
# REPORTS
# =========================================================


elif page == "Reports":

    st.title("Screening Reports")

    import pandas as pd
    from src.database import get_candidates

    candidates = get_candidates()

    if not candidates:
        st.info("No screening data available.")

    else:
        report_data = []

        for result in candidates:
            report_data.append({
                "Candidate": result.get("name", ""),
                "Email": result.get("email", ""),
                "Skill Match (%)": result.get("skill_score", 0),
                "Education Match (%)": result.get("education_score", 0),
                "Experience Match (%)": result.get("experience_score", 0),
                "Text Relevance (%)": result.get("relevance_score", 0),
                "Final Score (%)": result.get("final_score", 0),
                "Recommendation": result.get("status") or result.get("recommendation", ""),
                "Recruitment Stage": result.get("stage", "Screening")
            })

        df = pd.DataFrame(report_data)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        csv = df.to_csv(index=False)

        st.download_button(
            label="Download Screening Report",
            data=csv,
            file_name="eminence_talentflow_screening_report.csv",
            mime="text/csv"
        )


        # ---------------------------------------------------------
        # DATA STORAGE
        # ---------------------------------------------------------

        DATA_DIR = os.path.join(BASE_DIR, "data")

        RESULTS_FILE = os.path.join(
            DATA_DIR,
            "screening_results.json"
    )


    def load_screening_results():

        if not os.path.exists(RESULTS_FILE):
            return []

        try:

            with open(
                RESULTS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:

            return []


    def save_screening_results(results):

        os.makedirs(
            DATA_DIR,
            exist_ok=True
        )

        with open(
            RESULTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                results,
                file,
                indent=4,
                ensure_ascii=False
            )