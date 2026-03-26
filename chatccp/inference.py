from openai import OpenAI

import collections
import re
import os

class Inference:
    def __init__(self):
        self.use_context_chain = (os.getenv("INFERENCE_USE_CONTEXT_CHAIN", "0").lower() == "1")
        self.max_context_chain_depth = int(os.getenv("INFERENCE_MAX_CONTEXT_CHAIN_DEPTH", "4"))

        endpoint_base = os.getenv("DIGITAL_OCEAN_ACCESS_ENDPOINT")
        api_key = os.getenv("DIGITAL_OCEAN_ACCESS_KEY")

        if (not endpoint_base) or (not api_key):
            raise ValueError("DIGITAL_OCEAN_ACCESS_ENDPOINT and DIGITAL_OCEAN_ACCESS_KEY must be set in the environment variables.")

        endpoint = endpoint_base.rstrip("/") + "/api/v1/"

        self._client = OpenAI(
            base_url=endpoint,
            api_key=api_key
        )

        self._context_chain = collections.deque(
            maxlen=self.max_context_chain_depth
        )

    async def invoke(
        self,
        query: str
    ) -> str:
        messages = []

        if self.use_context_chain:
            messages += list(self._context_chain)

        messages.append({"role": "user", "content": query})

        completed_inference = self._client.chat.completions.create(
            model="n/a",
            messages=messages,
            extra_body={
                "include_retrieval_info": True
            }
        )

        # cleanup the response by removing any <think> tags and their contents
        response = completed_inference.choices[0].message.content or ""

        response = re.sub(
            r"<think>.*?</think>", "",
            response,
            flags=re.DOTALL
        ).strip()

        if self.use_context_chain:
            self._context_chain.append({"role": "user", "content": query})
            self._context_chain.append({"role": "assistant", "content": response})

        return response
