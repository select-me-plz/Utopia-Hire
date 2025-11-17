"""
Assistant Router
Simple rule-based intent detection and input normalization.
"""
from typing import Dict, Any, Tuple


class AssistantRouter:
    """Simple rule-based router to map user input to modes.

    Modes: general, career, resume_eval, job_match, recruiter, latex_resume
    """

    def __init__(self):
        # Keyword sets for simple rule-based classification
        self.career_keywords = {
            "career", "skills", "improve", "help me get hired",
            "how can i prepare", "industry norms", "good practices",
            "how to write", "how to explain experience",
        }

        self.resume_keywords = {"evaluate my resume", "score my profile", "what's wrong with my cv", "cv", "resume"}
        self.job_keywords = {"best job for me", "job match", "compare job offers", "job offers"}
        self.recruiter_keywords = {"simulate interviewer", "ask me interview questions", "pretend to be a recruiter", "interviewer", "interview"}
        self.latex_keywords = {"generate resume in latex", "latex cv", "create pdf resume", "latex"}

    def _contains_any(self, text: str, keywords) -> bool:
        t = text.lower()
        for k in keywords:
            if k in t:
                return True
        return False

    def detect_intent(self, payload: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Detect intent and return (mode, normalized_payload).

        normalized payload contains: message, resume_json, job_offers_json, context
        """
        message = (payload.get("message") or "") if isinstance(payload, dict) else ""
        resume_json = payload.get("resume_json") if isinstance(payload, dict) else None
        job_offers_json = payload.get("job_offers_json") if isinstance(payload, dict) else None
        context = payload.get("context") if isinstance(payload, dict) else {}

        # Priority checks
        # If explicit resume JSON provided -> resume_eval unless job_offers also provided (job_match)
        if resume_json and job_offers_json:
            mode = "job_match"
        elif resume_json and (self._contains_any(message, self.resume_keywords) or self._contains_any(message, {"evaluate", "evaluate my resume"})):
            mode = "resume_eval"
        elif job_offers_json and (self._contains_any(message, self.job_keywords) or True):
            # If job offers are provided, assume job matching
            mode = "job_match"
        else:
            # Keyword-based detection on message
            # Give career-related queries priority over recruiter keywords
            if self._contains_any(message, self.latex_keywords):
                mode = "latex_resume"
            elif self._contains_any(message, self.career_keywords):
                mode = "career"
            elif self._contains_any(message, self.recruiter_keywords):
                mode = "recruiter"
            elif self._contains_any(message, self.job_keywords):
                mode = "job_match"
            elif self._contains_any(message, self.resume_keywords):
                mode = "resume_eval"
            else:
                mode = "general"

        normalized = {
            "message": message,
            "resume_json": resume_json,
            "job_offers_json": job_offers_json,
            "context": context,
        }

        return mode, normalized
