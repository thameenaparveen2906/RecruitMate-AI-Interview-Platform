import google.generativeai as genai
from django.conf import settings
import json
import re
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Use valid model (gemini-pro is deprecated)
        self.model = genai.GenerativeModel("models/gemini-flash-lite-latest")



    def _get_text(self, response):
        try:
            text = ""
            for p in response.candidates[0].content.parts:
                if hasattr(p, "text"):
                    text += p.text
            return text.strip()
        except Exception:
            return ""

    def _extract_json(self, text):
        if not text:
            return None

        cleaned = text.strip()

        try:
            return json.loads(cleaned)
        except:
            pass

        match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                return None

        return None

    def _get_fallback_questions(self, num_questions):
        fallback = []
        for i in range(1, num_questions + 1):
            fallback.append({
                "question": f"Sample Question {i}: Describe your experience related to this job.",
                "type": "text",
                "difficulty": "medium",
                "expected_key_points": ["experience", "skills"]
            })
        return fallback

    def generate_questions(self, job_description, resume_data, num_questions=10):
        
        prompt = f"""
        You are an AI that outputs ONLY valid JSON. 
        NO explanation. NO markdown. NO other text.

        Generate exactly {num_questions} interview questions.

        Return ONLY a JSON array like:
        [
        {{
            "question": "",
            "type": "text",
            "difficulty": "easy | medium | hard",
            "expected_key_points": ["", ""]
        }}
        ]

        Job Description:
        {job_description}

        Candidate Resume:
        {resume_data}
        """


        try:
            response = self.model.generate_content(prompt)
            data = self._extract_json(self._get_text(response))

            if isinstance(data, list):
                return data[:num_questions]
            return self._get_fallback_questions(num_questions)

        except Exception as e:
            logger.exception("Question generation error: %s", e)
            return self._get_fallback_questions(num_questions)

    def evaluate_answer(self, question, answer, expected_key_points):
        prompt = f"""
Evaluate the following interview answer.

Question: {question}
Answer: {answer}

Expected Key Points: {expected_key_points}

Return STRICT JSON ONLY:
{{
  "score": 0-100,
  "feedback": "",
  "strengths": ["", ""],
  "improvements": ["", ""]
}}
"""

        try:
            response = self.model.generate_content(prompt)
            data = self._extract_json(self._get_text(response))

            if not data:
                return {"score": 50, "feedback": "Evaluation failed.", "strengths": [], "improvements": []}

            data["score"] = max(0, min(100, int(data.get("score", 50))))
            return data

        except:
            return {"score": 50, "feedback": "Evaluation failed.", "strengths": [], "improvements": []}

    def generate_report(self, interview_data):
        prompt = f"""
Generate a detailed interview report.

Interview Data:
{json.dumps(interview_data, indent=2)}

Return STRICT JSON ONLY:
{{
  "overall_score": 0-100,
  "summary": "",
  "strengths": [],
  "weaknesses": [],
  "recommendation": "hire | maybe | reject",
  "detailed_feedback": ""
}}
"""

        try:
            response = self.model.generate_content(prompt)
            data = self._extract_json(self._get_text(response))

            if not data:
                avg = int(interview_data.get("average_score", 50))
                return {"overall_score": avg, "summary": "Fallback", "strengths": [], "weaknesses": [], "recommendation": "maybe"}

            data["overall_score"] = max(0, min(100, int(data.get("overall_score", interview_data.get("average_score", 50)))))
            return data

        except Exception:
            avg = int(interview_data.get("average_score", 50))
            return {"overall_score": avg, "summary": "Error", "strengths": [], "weaknesses": [], "recommendation": "maybe"}

    def extract_skills(self, text):
        prompt = f"""
    Extract a list of technical skills from the following text.

    Text:
    {text}

    Return STRICT JSON ONLY:
    {{
    "skills": ["skill1", "skill2", "skill3"]
    }}
    """

        try:
            response = self.model.generate_content(prompt)
            raw = self._get_text(response)
            data = self._extract_json(raw)

            if data and "skills" in data:
                return data["skills"]

            return []

        except Exception as e:
            print("Skill extraction error:", e)
            return []

