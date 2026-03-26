from openai import OpenAI

import os

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
