from __future__ import annotations

import os

from openai import OpenAI
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from app.config import Config

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get(Config.OPENAI_API_KEY),
)


# Define a function to call the OpenAI API with retries
@retry(
    stop=stop_after_attempt(5),  # Stop after 5 attempts
    wait=wait_exponential(min=1, max=60),  # Exponential backoff from 1 to 60 seconds
)
def generate_text(prompt):
    """
    Generates a completion from OpenAI API with retries for rate limits and network errors.

    Parameters:
    prompt (str): The text prompt to send to the OpenAI API.

    Returns:
    str: The response text from the API.
    """
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message,
    )

    return response.choices[0].message.content


# Example usage
if __name__ == "__main__":
    prompt = "Explain the theory of relativity in simple terms."
    try:
        result = generate_text(prompt)
        print("Generated Text:", result)
    except Exception as e:
        print("Failed after multiple retries:", e)
