import io
import re

import spacy
from PyPDF2 import PdfReader
from docx import Document


# ============================================================
# NLP SETUP
# ============================================================

# Blank English pipeline is enough for tokenization and
# normalization. No external spaCy model download is required.
nlp = spacy.blank("en")


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf(file_bytes):
    """
    Extract text from a PDF file.
    """

    text_parts = []

    try:
        pdf_file = io.BytesIO(file_bytes)

        reader = PdfReader(pdf_file)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

    except Exception as e:

        raise ValueError(
            f"Unable to read PDF file: {e}"
        )

    return "\n".join(text_parts)


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_text_from_docx(file_bytes):
    """
    Extract text from a DOCX file.
    """

    try:

        doc_file = io.BytesIO(file_bytes)

        document = Document(doc_file)

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        # Also extract text from tables because many resumes
        # store skills/contact information inside tables.
        for table in document.tables:

            for row in table.rows:

                row_text = []

                for cell in row.cells:

                    cell_text = cell.text.strip()

                    if cell_text:
                        row_text.append(cell_text)

                if row_text:
                    paragraphs.append(
                        " ".join(row_text)
                    )

    except Exception as e:

        raise ValueError(
            f"Unable to read DOCX file: {e}"
        )

    return "\n".join(paragraphs)


# ============================================================
# GENERAL FILE EXTRACTION
# ============================================================

def extract_resume_text(uploaded_file):
    """
    Extract raw text from an uploaded PDF or DOCX file.
    """

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):

        return extract_text_from_pdf(
            file_bytes
        )

    elif file_name.endswith(".docx"):

        return extract_text_from_docx(
            file_bytes
        )

    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload a PDF or DOCX resume."
        )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_resume_text(text):
    """
    Clean extracted resume text while preserving useful
    technology names and section information.
    """

    if not text:
        return ""

    text = str(text)

    # Normalize common separators.
    text = text.replace("\r", "\n")

    # Replace multiple spaces.
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Reduce excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Remove repeated decorative characters.
    text = re.sub(
        r"[|]{2,}",
        "|",
        text
    )

    return text.strip()


# ============================================================
# NLP TOKENIZATION
# ============================================================

def tokenize_resume(text):
    """
    Tokenize resume text using spaCy.
    """

    cleaned_text = clean_resume_text(text)

    if not cleaned_text:
        return []

    doc = nlp(cleaned_text)

    tokens = []

    for token in doc:

        if token.is_space:
            continue

        token_text = token.text.strip()

        if token_text:
            tokens.append(token_text)

    return tokens


# ============================================================
# NORMALIZE TEXT FOR SKILL MATCHING
# ============================================================

def normalize_for_matching(text):
    """
    Normalize text so that skills can be matched despite
    differences such as:
        Python
        python
        PYTHON
        C++
        C/C++
        Node.js
    """

    text = str(text).lower()

    # Normalize common unicode punctuation.
    replacements = {
        "–": "-",
        "—": "-",
        "’": "'",
        "“": '"',
        "”": '"',
        "\u00a0": " ",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SKILL MATCHING
# ============================================================

def skill_exists_in_text(skill, text):
    """
    Determine whether a skill appears in text.

    Uses boundaries where possible while allowing technical
    names containing characters such as:
        C++
        C#
        .NET
        Node.js
        React.js
    """

    skill = str(skill).strip()

    if not skill:
        return False

    normalized_text = normalize_for_matching(
        text
    )

    normalized_skill = normalize_for_matching(
        skill
    )

    if not normalized_skill:
        return False

    # Direct phrase check for technical names.
    if normalized_skill in normalized_text:

        # For very short skills, avoid accidental matches.
        if len(normalized_skill) <= 2:

            pattern = (
                r"(?<![a-zA-Z0-9])"
                + re.escape(normalized_skill)
                + r"(?![a-zA-Z0-9])"
            )

            return bool(
                re.search(
                    pattern,
                    normalized_text
                )
            )

        return True

    # Handle slash-based variations.
    skill_variants = [
        normalized_skill.replace("/", " / "),
        normalized_skill.replace("-", " "),
        normalized_skill.replace(".", " "),
    ]

    for variant in skill_variants:

        variant = re.sub(
            r"\s+",
            " ",
            variant
        ).strip()

        if variant and variant in normalized_text:
            return True

    return False


def extract_resume_skills(
    resume_text,
    skill_database
):
    """
    Extract skills from resume text using the application's
    existing skill database.

    Returns a list of matched skill names.
    """

    if not resume_text:
        return []

    detected = []

    # Longer skills first so that specific phrases are
    # evaluated before shorter ones.
    skills = sorted(
        skill_database.keys(),
        key=len,
        reverse=True
    )

    for skill in skills:

        if skill_exists_in_text(
            skill,
            resume_text
        ):

            detected.append(skill)

    # Remove duplicates while preserving order.
    detected = list(
        dict.fromkeys(detected)
    )

    return detected


# ============================================================
# CATEGORY EXTRACTION
# ============================================================

def get_resume_skill_categories(
    skills,
    skill_database
):
    """
    Map detected resume skills to their categories.
    """

    results = []

    for skill in skills:

        categories = skill_database.get(
            skill,
            set()
        )

        results.append(
            {
                "skill": skill,
                "categories": sorted(
                    categories
                )
            }
        )

    return results


# ============================================================
# JOB / RESUME COMPARISON
# ============================================================

def calculate_job_match(
    job_skills,
    resume_skills
):
    """
    Compare required job skills against candidate resume skills.

    Score is based on:
        matched required skills / total required skills

    Returns:
        score
        matched_skills
        missing_skills
        extra_skills
    """

    job_set = {
        str(skill).lower().strip()
        for skill in job_skills
    }

    resume_lookup = {
        str(skill).lower().strip(): skill
        for skill in resume_skills
    }

    matched_skills = []
    missing_skills = []

    for job_skill in job_skills:

        normalized = (
            str(job_skill)
            .lower()
            .strip()
        )

        if normalized in resume_lookup:

            matched_skills.append(
                job_skill
            )

        else:

            missing_skills.append(
                job_skill
            )

    if len(job_set) == 0:

        score = 0

    else:

        score = round(
            (
                len(matched_skills)
                / len(job_set)
            ) * 100
        )

    extra_skills = []

    for skill in resume_skills:

        normalized = (
            str(skill)
            .lower()
            .strip()
        )

        if normalized not in job_set:

            extra_skills.append(skill)

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
    }