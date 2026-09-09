"""
model/skill_extractor.py

Core "model" for the Skill Extraction pipeline described in the architecture:

User -> Web Interface / API -> Preprocessing -> Skill Extraction Model
     -> Skill Normalization -> Category Mapping -> Final Skills Deliverable

This is a lightweight, dependency-free keyword/alias matching engine.
It can be swapped later for a spaCy / transformer-based NER model without
changing the API contract (extract_skills always returns the same shape).
"""

import json
import re
from pathlib import Path
from typing import Dict, List

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_db.json"


def _load_skills_db() -> Dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class SkillExtractor:
    """
    Loads the skills knowledge base once and reuses it for every request.
    """

    def __init__(self):
        self.skills_db = _load_skills_db()
        # Build a flat alias -> canonical skill name lookup, sorted by
        # alias length (longest first) so multi-word aliases are matched
        # before shorter substrings (e.g. "power bi" before "bi").
        self._alias_map = []
        for canonical, meta in self.skills_db.items():
            for alias in meta["aliases"]:
                self._alias_map.append((alias.strip().lower(), canonical))
        self._alias_map.sort(key=lambda x: len(x[0]), reverse=True)

    # ---------- Step 1: Preprocessing ----------
    @staticmethod
    def preprocess(text: str) -> str:
        text = text.lower()
        # normalize separators so "power-bi" / "power_bi" behave like "power bi"
        text = re.sub(r"[_/,]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return f" {text.strip()} "

    # ---------- Step 2: Skill Extraction Model ----------
    def _find_matches(self, clean_text: str) -> List[str]:
        found = []
        for alias, canonical in self._alias_map:
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias.strip()) + r"(?![a-zA-Z0-9])"
            if re.search(pattern, clean_text):
                if canonical not in found:
                    found.append(canonical)
        return found

    # ---------- Step 3: Skill Normalization ----------
    # Handled implicitly: every alias maps to one canonical skill name,
    # e.g. "powerbi", "power-bi", "power bi" all normalize to "Power BI".

    # ---------- Step 4: Category Mapping ----------
    def _map_categories(self, skills: List[str]) -> Dict[str, List[str]]:
        categories: Dict[str, List[str]] = {}
        for skill in skills:
            category = self.skills_db[skill]["category"]
            categories.setdefault(category, []).append(skill)
        return categories

    # ---------- Public entry point: Final Skills Deliverable ----------
    def extract_skills(self, job_description: str) -> Dict:
        clean_text = self.preprocess(job_description)
        skills = self._find_matches(clean_text)
        categories = self._map_categories(skills)
        return {
            "detected_skills": sorted(skills),
            "categories": categories,
            "total_skills_found": len(skills),
        }


# Singleton instance reused across requests (loaded once at startup)
skill_extractor = SkillExtractor()
