import os

from deepeval.models import GeminiModel
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "Set GOOGLE_API_KEY (or GEMINI_API_KEY) to use Gemini for DeepEval."
    )

eval_model = GeminiModel(
    model="gemini-3.5-flash-lite",
    api_key=api_key,
)