import boto3
import json
from src.ga.plan import Plan
import re
import prompt

class LLM:
    def __init__(self, endpoint_id: str, region: str = "us-west-2", version: str = "bedrock-2023-05-31"):
        self.model_id = endpoint_id
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.version = version

    def buildPrompt(self, system: str, user: str):
        return [
            {"role":"system", "content": [{"type": "text", "text": system}]},
            {"role":"user", "content": [{"type": "text", "text": user}]}
        ]
    
    def invoke(self, systemPrompt: str, userPrompt: str):
        prompt = self.buildPrompt(systemPrompt, userPrompt)

        body = {
            "anthropic_version": self.version,
            "messages": prompt,
            "max_tokens": 1024,
            "temperature": 0.2
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            body=json.dumps(body)
        )

        payload = json.loads(response["body"].read())
        generated_text = payload["content"][0]["text"]

        return generated_text

    def generateTrip(self, systemPrompt: str, userPrompt: str) -> Plan:
        generatedText = self.invoke(systemPrompt, userPrompt)
        json_str = self._extract_json(generatedText)

        return Plan.model_validate_json(json_str)
    
    def explainTrip(self, systemPrompt: str, userPrompt: str) -> str:
        generatedText = self.invoke(systemPrompt, userPrompt)
        return generatedText
    
    def _extract_json(self, text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in model output.")
        return match.group(0)