from openai import OpenAI
from django.conf import settings
import json
import re
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Modern OpenAI Responses API service for question generation, evaluation and reports."""

    def __init__(self):
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            logger.warning("OPENAI_API_KEY is not set. OpenAIService will fail at runtime.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    def _extract_json(self, text):
        if not text:
            return None
        m = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        m = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        try:
            return json.loads(text)
        except Exception:
            return None

    def _get_text_from_response(self, resp):
        try:
            if hasattr(resp, "output_text") and resp.output_text:
                return resp.output_text
            output = getattr(resp, "output", None)
            if output and isinstance(output, list) and len(output) > 0:
                for item in output:
                    content = item.get("content") if isinstance(item, dict) else None
                    if content and isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and "text" in part:
                                return part["text"]
                try:
                    return "".join(str(o) for o in output)
                except Exception:
                    pass
        except Exception as e:
            logger.exception("Failed to extract text from response: %s", e)
        return ""

    def extract_skills(self, job_description):
        prompt = (
            "Extract key technical and soft skills from this job description.\n"
            "Return ONLY a JSON array of strings (no markdown, no extra text).\n\n"
            f"Job Description:\n{job_description}\n\n"
            "Example: [\"Python\", \"Django\", \"Communication\"]"
        )
        try:
            resp = self.client.responses.create(model=self.model, input=prompt)
            text = self._get_text_from_response(resp)
            skills = self._extract_json(text)
            return skills if isinstance(skills, list) else []
        except Exception as e:
            logger.exception("extract_skills failed: %s", e)
            return []

    def generate_questions(self, job_description, resume_data, num_questions=10):
        prompt = (
            f"You're an expert interviewer. Generate exactly {num_questions} interview questions based on the job description "
            "and candidate resume. Return ONLY a JSON array of objects (no markdown):\n\n"
            "[{ \"question\": \"...\", \"type\": \"technical|behavioral|situational\", "
            "\"difficulty\": \"easy|medium|hard\", \"expected_key_points\": [\"...\"] }]\n\n"
            f"Job Description:\n{job_description}\n\nCandidate Resume:\n{resume_data}\n"
        )
        try:
            resp = self.client.responses.create(model=self.model, input=prompt)
            text = self._get_text_from_response(resp)
            questions = self._extract_json(text)
            if not questions or not isinstance(questions, list):
                return self._get_fallback_questions(num_questions)
            return questions[:num_questions]
        except Exception as e:
            logger.exception("generate_questions failed: %s", e)
            return self._get_fallback_questions(num_questions)

    def _get_fallback_questions(self, n):
        fallback = [
            {
                "question": "Tell me about yourself and your experience.",
                "type": "behavioral",
                "difficulty": "easy",
                "expected_key_points": ["Background", "Experience", "Skills"]
            },
            {
                "question": "What are your key technical skills?",
                "type": "technical",
                "difficulty": "easy",
                "expected_key_points": ["Languages", "Frameworks", "Tools"]
            },
            {
                "question": "Describe a challenging project you worked on.",
                "type": "behavioral",
                "difficulty": "medium",
                "expected_key_points": ["Challenge", "Action", "Result"]
            },
            {
                "question": "How do you handle tight deadlines?",
                "type": "situational",
                "difficulty": "medium",
                "expected_key_points": ["Prioritization", "Communication", "Planning"]
            }
        ]
        return fallback[:n]

    def evaluate_answer(self, question, answer, expected_key_points):
        prompt = (
            "Evaluate this interview answer and return ONLY a JSON object (no markdown):\n\n"
            "{ \"score\": 0-100, \"feedback\": \"\", \"strengths\": [], \"improvements\": [] }\n\n"
            f"Question: {question}\n"
            f"Expected Key Points: {', '.join(expected_key_points) if expected_key_points else 'General evaluation'}\n"
            f"Candidate Answer: {answer}\n"
        )
        try:
            resp = self.client.responses.create(model=self.model, input=prompt)
            text = self._get_text_from_response(resp)
            evaluation = self._extract_json(text)
            if not evaluation or not isinstance(evaluation, dict):
                return {
                    "score": 50,
                    "feedback": "Could not parse model output. Answer recorded.",
                    "strengths": [],
                    "improvements": ["Provide more detail"]
                }
            try:
                evaluation["score"] = max(0, min(100, int(evaluation.get("score", 50))))
            except Exception:
                evaluation["score"] = 50
            return evaluation
        except Exception as e:
            logger.exception("evaluate_answer failed: %s", e)
            return {
                "score": 50,
                "feedback": "Evaluation failed due to system error.",
                "strengths": [],
                "improvements": []
            }

    def generate_report(self, interview_data):
        answers = interview_data.get("answers", [])
        scores_summary = "\n".join([f"Q: {a.get('question')} | Score: {a.get('score', 'N/A')}" for a in answers])

        prompt = (
            "Generate a final interview report and return ONLY a JSON object (no markdown):\n\n"
            "{ \"overall_score\": 0-100, \"summary\": \"\", \"strengths\": [], \"weaknesses\": [], "
            "\"recommendation\": \"hire|maybe|no\", \"detailed_feedback\": \"\" }\n\n"
            f"Candidate: {interview_data.get('candidate_name')}\n"
            f"Position: {interview_data.get('position')}\n"
            f"Average Score: {interview_data.get('average_score', 0):.1f}\n"
            f"Question Scores:\n{scores_summary}\n"
        )
        try:
            resp = self.client.responses.create(model=self.model, input=prompt)
            text = self._get_text_from_response(resp)
            report = self._extract_json(text)
            if not report or not isinstance(report, dict):
                return {
                    "overall_score": int(interview_data.get("average_score", 50)),
                    "summary": "Report generation failed; manual review needed.",
                    "strengths": [],
                    "weaknesses": [],
                    "recommendation": "maybe",
                    "detailed_feedback": "Manual review recommended."
                }
            try:
                report["overall_score"] = max(0, min(100, int(report.get("overall_score", interview_data.get("average_score", 50)))))
            except Exception:
                report["overall_score"] = int(interview_data.get("average_score", 50))
            return report
        except Exception as e:
            logger.exception("generate_report failed: %s", e)
            return {
                "overall_score": int(interview_data.get("average_score", 50)),
                "summary": "Report failed to generate.",
                "strengths": [],
                "weaknesses": [],
                "recommendation": "maybe",
                "detailed_feedback": "Manual review recommended."
            }

