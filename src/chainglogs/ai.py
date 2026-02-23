import os
import time
from typing import Optional

import keyring
from google import genai
from google.genai import errors


class AI:
    """Handles interactions with the Gemini API."""

    def __init__(self):
        api_key = self._get_gemini_api_key()
        # If api_key is None, genai will look for a GEMINI_API_KEY env var
        self.client = genai.Client(api_key=api_key)

    @staticmethod
    def _get_gemini_api_key() -> Optional[str]:
        if 'GEMINI_API_KEY' in os.environ:
            return os.environ['GEMINI_API_KEY']
        return keyring.get_password("chainglogs", "gemini-api-key")

    def summarize_commit(self, message: str) -> str:
        prompt = (
            "Summarize the following commit message into a single, concise line "
            "of reStructuredText suitable for a changelog entry. Preserve any "
            "existing reStructuredText links. Do not include bullet points.\n\n"
            f"Commit message:\n{message}"
        )
        print(f"Summarizing commit\n{message}")

        while True:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-lite", contents=prompt
                )
                summary = response.text.strip()
                print("Summary:\n{summary}")
                return summary

            except errors.ClientError as e:
                # Check if it's a 429 Resource Exhausted error
                if e.code == 429:
                    sleep_seconds = self._get_retry_delay(e)
                    if sleep_seconds == 0.0:
                        # Probably out of quota for the day
                        raise e
                    print(f"Quota exceeded. Retrying in {sleep_seconds} seconds...")
                    time.sleep(sleep_seconds)
                    continue
                # If it's a different ClientError, re-raise it
                raise e

    def _get_retry_delay(self, exc: errors.ClientError) -> float:
        """Parses the retryDelay from the ClientError response details."""
        default_delay = 30.0

        for detail in exc.details['error']['details']:
            if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                delay_str = detail.get("retryDelay", "30s")
                # Remove the 's' suffix and convert to float
                return float(delay_str.rstrip("s"))

        return default_delay
