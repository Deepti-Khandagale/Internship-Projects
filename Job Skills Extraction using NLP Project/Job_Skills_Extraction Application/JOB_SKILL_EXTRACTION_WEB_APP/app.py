import streamlit as st

from utils.auth import (
    create_database,
    register_user,
    login_user
)

from utils.data_loader import (
    load_dataset,
    build_skill_database
)

from model.skill_extractor import SkillExtractor

from model.resume_parser import (
    extract_resume_text,
    clean_resume_text,
    extract_resume_skills,
    get_resume_skill_categories,
    calculate_job_match
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Job Skills Extractor",
    page_icon="💼",
    layout="wide"
)


# ============================================================
# SIMPLE CORPORATE STYLE
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f7f9fc;
    }

    section[data-testid="stSidebar"] {
        background-color: #12395b;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .skill-badge {
        display: inline-block;
        background-color: #edf6fc;
        color: #165a82;
        border: 1px solid #cde5f4;
        padding: 7px 12px;
        border-radius: 20px;
        margin: 4px;
        font-size: 13px;
        font-weight: 600;
    }

    .matched {
        background-color: #edf8f2;
        border: 1px solid #c9e8d7;
        color: #236b45;
        padding: 10px 14px;
        border-radius: 9px;
        margin: 5px 0;
        font-weight: 600;
    }

    .missing {
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a4d0b;
        padding: 10px 14px;
        border-radius: 9px;
        margin: 5px 0;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

create_database()


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_data():
    return load_dataset()


@st.cache_resource
def create_extractor(data):

    database = build_skill_database(data)

    return SkillExtractor(database)


try:

    data = load_data()

    extractor = create_extractor(data)

except Exception as e:

    st.error(
        f"Unable to load application data: {e}"
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

if "job_skills" not in st.session_state:
    st.session_state.job_skills = []

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []


# ============================================================
# LOGIN / REGISTER
# ============================================================

if not st.session_state.logged_in:

    st.title("💼 Job Skills Extractor")

    st.caption(
        "AI-powered job description and resume analysis"
    )

    st.divider()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if st.session_state.auth_page == "login":

        st.subheader("🔐 Welcome")

        st.write(
            "Sign in to access your recruitment dashboard."
        )

        email = st.text_input(
            " Email",
            placeholder="example@gmail.com"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not email or not password:

                st.warning(
                    "Please enter email and password."
                )

            else:

                success, name, message = login_user(
                    email,
                    password
                )

                if success:

                    st.session_state.logged_in = True
                    st.session_state.user_name = name
                    st.session_state.user_email = email

                    st.rerun()

                else:

                    st.error(message)

        st.write("")

        st.write(
            "Don't have an account?"
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True
        ):

            st.session_state.auth_page = "register"

            st.rerun()

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    else:

        st.subheader("📝 Create Account")

        st.write(
            "Create an account to start analyzing "
            "jobs and candidate resumes."
        )

        name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        email = st.text_input(
            "Email",
            placeholder="example@gmail.com"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password"
        )

        if st.button(
            "Register",
            type="primary",
            use_container_width=True
        ):

            if (
                not name
                or not email
                or not password
                or not confirm_password
            ):

                st.warning(
                    "Please complete all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(
                        "Registration successful!"
                    )

                    st.session_state.auth_page = "login"

                    st.info(
                        "Please login with your new account."
                    )

                else:

                    st.error(message)

        st.write("")

        st.write(
            "Already have an account?"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            st.session_state.auth_page = "login"

            st.rerun()

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("💼 Skill Extractor")

    st.caption(
        "Recruitment Analytics Platform"
    )

    st.divider()

    st.subheader("👤 Account")

    st.write(
        st.session_state.user_name
    )

    st.caption(
        st.session_state.user_email
    )

    st.divider()


    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("💼Skill Extractor")

st.caption(
    "AI-powered recruitment and candidate analysis"
)

st.divider()


# ============================================================
# WELCOME
# ============================================================

st.header(
    f"Welcome, {st.session_state.user_name} 👋"
)

st.write(
    "Analyze job requirements, extract candidate skills, "
    "and evaluate candidate-job alignment using "
    "AI-assisted skill intelligence."
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.divider()

st.header(
    "🔎 1. Analyze Job Description"
)

st.write(
    "Enter the job requirements that you want "
    "to match against a candidate."
)

job_description = st.text_area(
    "Job Description",
    value=st.session_state.job_description,
    height=230,
    placeholder=(
        "Example:\n\n"
        "We are looking for a Python developer with "
        "experience in SQL, Excel, AWS, Docker and Git."
    )
)


if st.button(
    "🧠 Extract Job Skills",
    type="primary",
    use_container_width=True
):

    if not job_description.strip():

        st.warning(
            "Please enter a job description."
        )

    else:

        job_skills = extractor.extract_skills(
            job_description
        )

        st.session_state.job_description = (
            job_description
        )

        st.session_state.job_skills = (
            job_skills
        )

        if job_skills:

            st.success(
                f"{len(job_skills)} required skill(s) detected."
            )

        else:

            st.warning(
                "No matching skills were found."
            )


# ============================================================
# JOB SKILLS
# ============================================================

if st.session_state.job_skills:

    st.subheader(
        "🎯 Required Job Skills"
    )

    skill_columns = st.columns(
        min(
            len(st.session_state.job_skills),
            5
        )
    )

    for index, skill in enumerate(
        st.session_state.job_skills
    ):

        with skill_columns[
            index % len(skill_columns)
        ]:

            st.info(skill)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.divider()

st.header(
    "📄 2. Upload Candidate Resume"
)

st.write(
    "Upload a PDF or DOCX resume. "
    "The system will extract the text and "
    "identify recognized skills."
)

uploaded_resume = st.file_uploader(
    "Candidate Resume",
    type=[
        "pdf",
        "docx"
    ],
    help="Supported formats: PDF and DOCX"
)


if uploaded_resume is not None:

    st.success(
        f"Resume selected: {uploaded_resume.name}"
    )

    if st.button(
        "🤖 Extract Resume Skills",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Reading resume and extracting skills..."
        ):

            try:

                resume_text = extract_resume_text(
                    uploaded_resume
                )

                resume_text = clean_resume_text(
                    resume_text
                )

                resume_skills = extract_resume_skills(
                    resume_text,
                    extractor.skill_database
                )

                st.session_state.resume_text = (
                    resume_text
                )

                st.session_state.resume_skills = (
                    resume_skills
                )

                if resume_skills:

                    st.success(
                        f"{len(resume_skills)} skill(s) "
                        "detected from the resume."
                    )

                else:

                    st.warning(
                        "No recognized skills were found "
                        "in this resume."
                    )

            except Exception as e:

                st.error(
                    f"Resume processing failed: {e}"
                )


# ============================================================
# RESUME RESULTS
# ============================================================

if st.session_state.resume_skills:

    st.divider()

    st.header(
        "🧠 Candidate Skill Profile"
    )

    skill_columns = st.columns(
        min(
            len(st.session_state.resume_skills),
            5
        )
    )

    for index, skill in enumerate(
        st.session_state.resume_skills
    ):

        with skill_columns[
            index % len(skill_columns)
        ]:

            st.info(skill)


    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    category_data = get_resume_skill_categories(
        st.session_state.resume_skills,
        extractor.skill_database
    )

    category_counts = {}

    for item in category_data:

        for category in item["categories"]:

            category_counts[category] = (
                category_counts.get(
                    category,
                    0
                ) + 1
            )


    if category_counts:

        st.subheader(
            "🗂️ Candidate Skill Categories"
        )

        for category, count in sorted(
            category_counts.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            st.write(
                f"**{category}** — "
                f"{count} skill(s)"
            )


# ============================================================
# JOB MATCH
# ============================================================

if (
    st.session_state.job_skills
    and st.session_state.resume_skills
):

    st.divider()

    st.header(
        "🎯 3. Candidate–Job Match"
    )

    match_result = calculate_job_match(
        st.session_state.job_skills,
        st.session_state.resume_skills
    )

    score = match_result["score"]

    matched_skills = match_result[
        "matched_skills"
    ]

    missing_skills = match_result[
        "missing_skills"
    ]

    extra_skills = match_result[
        "extra_skills"
    ]


    # --------------------------------------------------------
    # MATCH SCORE
    # --------------------------------------------------------

    st.subheader(
        "Candidate–Job Match Score"
    )

    st.metric(
        "Match Score",
        f"{score}%"
    )

    st.progress(
        score / 100
    )


    if score >= 80:

        st.success(
            "🟢 Strong Match — "
            "The candidate has most of the required skills."
        )

    elif score >= 60:

        st.info(
            "🔵 Good Match — "
            "The candidate meets a significant portion "
            "of the requirements."
        )

    elif score >= 40:

        st.warning(
            "🟠 Moderate Match — "
            "Several important skills are missing."
        )

    else:

        st.error(
            "🔴 Low Match — "
            "The candidate may require substantial upskilling."
        )


    st.write(
        f"Matched **{len(matched_skills)}** "
        f"of **{len(st.session_state.job_skills)}** "
        "required skills."
    )


    # --------------------------------------------------------
    # MATCHED SKILLS
    # --------------------------------------------------------

    st.subheader(
        "✅ Matched Skills"
    )

    if matched_skills:

        for skill in matched_skills:

            st.success(
                f"✓ {skill}"
            )

    else:

        st.write(
            "No required skills matched."
        )


    # --------------------------------------------------------
    # MISSING SKILLS
    # --------------------------------------------------------

    st.subheader(
        "⚠️ Missing Skills"
    )

    if missing_skills:

        for skill in missing_skills:

            st.warning(
                f"⚠ {skill}"
            )

    else:

        st.success(
            "The candidate has all detected job skills."
        )


    # --------------------------------------------------------
    # ADDITIONAL SKILLS
    # --------------------------------------------------------

    if extra_skills:

        st.subheader(
            "⭐ Additional Candidate Skills"
        )

        skill_columns = st.columns(
            min(
                len(extra_skills),
                5
            )
        )

        for index, skill in enumerate(
            extra_skills
        ):

            with skill_columns[
                index % len(skill_columns)
            ]:

                st.info(skill)


    # --------------------------------------------------------
    # HR RECOMMENDATION
    # --------------------------------------------------------

    st.subheader(
        "👔 Recommendation"
    )

    if score >= 80:

        recommendation = (
            "Strong technical alignment. "
            "This candidate appears highly aligned "
            "with the technical requirements of the role."
        )

    elif score >= 60:

        recommendation = (
            "Good technical alignment. "
            "The candidate meets many requirements, "
            "but the missing skills should be reviewed."
        )

    elif score >= 40:

        recommendation = (
            "Moderate technical alignment. "
            "Consider evaluating the candidate's "
            "experience and potential for upskilling."
        )

    else:

        recommendation = (
            "Limited technical alignment. "
            "The candidate is missing several "
            "identified requirements and may need "
            "further assessment."
        )

    st.info(
        recommendation
    )


# ============================================================
# WAITING MESSAGE
# ============================================================

elif uploaded_resume is not None:

    if not st.session_state.job_skills:

        st.info(
            "💡 Analyze a job description first, "
            "then upload a resume to calculate "
            "the Candidate–Job Match Score."
        )

    elif not st.session_state.resume_skills:

        st.info(
            "💡 Click **Extract Resume Skills** "
            "to analyze the candidate."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Skill Intelligence • "
    "Recruitment Analytics Platform"
)