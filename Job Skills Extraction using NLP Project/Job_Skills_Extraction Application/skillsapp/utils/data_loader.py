import pandas as pd
import os
import re


DATA_FILE = os.path.join(
    "data",
    "clean_jobs_descriptions_combined.csv"
)


def load_dataset():
    """
    Load the complete job dataset.
    """

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    # Clean column names
    df.columns = df.columns.str.strip()

    required_columns = [
        "Job Description",
        "clean_description",
        "skills",
        "extracted_skills",
        "categories"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Required column missing: {column}"
            )

    # Replace missing values
    df = df.fillna("")

    return df


def clean_skill(skill):
    """
    Clean a skill name.

    Examples:
        Python (Programming) -> Python
        SQL (Database) -> SQL
    """

    skill = str(skill).strip()

    # Remove category in brackets
    skill = re.sub(
        r"\s*\([^)]*\)",
        "",
        skill
    )

    return skill.strip()


def split_values(value):
    """
    Split comma/semicolon/pipe separated values.
    """

    if not value:
        return []

    value = str(value).strip()

    if not value:
        return []

    parts = re.split(
        r"[,;|]",
        value
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def build_skill_database(df):
    """
    Build a skill -> category dictionary.

    Supports formats such as:

        Python (Programming), SQL (Database)

    or:

        Python, SQL, Java
    """

    skill_database = {}

    for _, row in df.iterrows():

        extracted_value = str(
            row.get("extracted_skills", "")
        ).strip()

        category_value = str(
            row.get("categories", "")
        ).strip()

        # ------------------------------------------------
        # Get categories from categories column
        # ------------------------------------------------

        row_categories = split_values(
            category_value
        )

        # ------------------------------------------------
        # Process extracted skills
        # ------------------------------------------------

        skills = split_values(
            extracted_value
        )

        for part in skills:

            part = part.strip()

            if not part:
                continue

            # Check for:
            # Python (Programming)
            match = re.match(
                r"^(.*?)\s*\(([^()]*)\)\s*$",
                part
            )

            if match:

                skill = match.group(1).strip()

                category = match.group(2).strip()

                categories = [category] if category else row_categories

            else:

                skill = part

                categories = row_categories

            # Clean skill name
            skill = clean_skill(skill)

            if not skill:
                continue

            # Ignore extremely short/invalid values
            if len(skill) < 2:
                continue

            # Create dictionary entry
            if skill not in skill_database:
                skill_database[skill] = set()

            # Add categories
            for category in categories:

                category = str(
                    category
                ).strip()

                if category:
                    skill_database[skill].add(
                        category
                    )

    return skill_database


def get_all_skills(skill_database):
    """
    Return all unique skills.
    """

    return sorted(
        skill_database.keys(),
        key=len,
        reverse=True
    )