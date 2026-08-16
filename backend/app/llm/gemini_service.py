import os
import json

from dotenv import load_dotenv
from google import genai



class GeminiService:
    """
    Gemini service responsible for generating an
    evidence-based infrastructure investigation.
    """

    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL") or "gemini-3.5-flash"
        self.client = None

        if self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key
                )
            except Exception as e:
                print(f"Failed to initialize GenAI Client: {e}")

    def generate_investigation(
        self,
        analysis,
        evaluation,
        retrieved_evidence
    ):
        """
        Generate an evidence-based root cause investigation
        using SentinelAI's ML, database, and RAG results.
        """

        prompt = f"""
You are SentinelAI, an AI system for investigating
infrastructure and distributed-system anomalies.

Your task is to generate an evidence-based investigation.

You MUST primarily rely on the information provided below.

Do not invent specific logs, metrics, events, configurations,
or historical incidents that are not present in the evidence.

If the available evidence is insufficient to determine an exact
root cause, clearly state that the result is a hypothesis and
recommend additional investigation steps.

====================
STRUCTURED ANALYSIS
====================

{json.dumps(analysis, indent=2, default=str)}

====================
EVALUATION
====================

{json.dumps(evaluation, indent=2, default=str)}

====================
RETRIEVED KNOWLEDGE BASE EVIDENCE
====================

{json.dumps(retrieved_evidence, indent=2, default=str)}

====================
RESPONSE FORMAT
====================

Return a clear investigation with these sections:

1. Incident Summary
2. Severity and Impact
3. Affected Services
4. Most Likely Root Cause
5. Supporting Evidence
6. Alternative Possible Causes
7. Recommended Investigation Steps
8. Confidence and Limitations

Clearly distinguish between facts detected by SentinelAI
and hypotheses inferred from the available evidence.
"""

        if not self.client or not self.api_key:
            return (
                "### Investigation Report (Fallback Mode)\n\n"
                "**Note:** Automated analysis via Gemini is currently unavailable because the API key is not configured.\n\n"
                "Please configure `GEMINI_API_KEY` on your backend server environment variables "
                "to enable automated root cause analysis reports."
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback mock report when Gemini API fails
            return (
                "### Investigation Report (Fallback Mode)\n\n"
                "**Note:** Automated analysis via Gemini is currently unavailable. "
                "This report is a placeholder based on raw data inputs.\n\n"
                f"**Error Details:** {str(e)}\n\n"
                "Please review the raw analysis and evaluation JSON inputs directly "
                "to determine the root cause of this incident."
            )