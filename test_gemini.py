import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )

if not model_name:
    raise ValueError(
        "GEMINI_MODEL was not found in the .env file."
    )


client = genai.Client(
    api_key=api_key
)

response = client.interactions.create(
    model=model_name,
    input="""
You are an AI system for investigating infrastructure
and distributed system anomalies.

Briefly explain what could cause an HDFS DataNode
connection failure.
"""
)

print("\nGEMINI RESPONSE:\n")
print(response.output_text)