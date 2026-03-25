from openai import OpenAI

import os
import re

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

class Inference:
    def __init__(self):
        endpoint = os.getenv("DIGITAL_OCEAN_ACCESS_ENDPOINT") + "/api/v1/" 
        api_key = os.getenv("DIGITAL_OCEAN_ACCESS_KEY")

        if (not endpoint) or (not api_key):
            raise ValueError("DIGITAL_OCEAN_ACCESS_ENDPOINT and DIGITAL_OCEAN_ACCESS_KEY must be set in the environment variables.")

        self._client = OpenAI(
            base_url=endpoint,
            api_key=api_key
        )

    async def invoke(
        self,
        messages: list[dict[str, str]]
    ):
        response = self._client.chat.completions.create(
            model="n/a",
            messages=messages,
            extra_body={
                "include_retrieval_info": True
            }
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Attempting to invoke inference for testing...")

    inference = Inference()
    response = inference.invoke("what is the result of 1+1?")
    print("Inference invocation successful. Processing response...")
    print(f"Full response: {response.to_dict()}", end="\n\n")

    for choice in response.choices:
        print(f"Response: {choice.message.content}")
