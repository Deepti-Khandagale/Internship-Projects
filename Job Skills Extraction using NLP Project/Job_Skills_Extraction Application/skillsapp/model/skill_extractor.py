import re


class SkillExtractor:

    def __init__(self, skill_database):

        self.skill_database = skill_database

        # Longest skills first
        self.skills = sorted(
            skill_database.keys(),
            key=len,
            reverse=True
        )

    def normalize_text(self, text):
        """
        Normalize text before searching.
        """

        text = str(text).lower()

        # Normalize common separators
        text = text.replace(
            "-", " "
        )

        text = text.replace(
            "/", " "
        )

        # Replace multiple spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def extract_skills(self, job_description):
        """
        Extract skills from a job description.
        """

        text = self.normalize_text(
            job_description
        )

        detected = []

        for skill in self.skills:

            skill_lower = self.normalize_text(
                skill
            )

            # Word-boundary matching
            pattern = (
                r"(?<!\w)"
                + re.escape(skill_lower)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                text
            ):

                detected.append(skill)

        # Remove duplicates
        detected = list(
            dict.fromkeys(
                detected
            )
        )

        return detected

    def get_categories(self, skills):
        """
        Map extracted skills to categories.
        """

        results = []

        for skill in skills:

            categories = self.skill_database.get(
                skill,
                set()
            )

            results.append({
                "skill": skill,
                "categories": sorted(
                    categories
                )
            })

        return results
    