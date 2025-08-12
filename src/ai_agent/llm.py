import boto3
import json
from src.ga.plan import Plan
import re

class LLM:
    def __init__(self, endpoint_id: str, boto3_session: boto3.Session, region: str = "eu-north-1", version: str = "bedrock-2023-05-31"):
        self.model_id = endpoint_id
        self.client = boto3_session.client("bedrock-runtime", region_name=region)
        self.version = version

    def buildPrompt(self, user: str):
        return [
            {"role":"user", "content": [{"type": "text", "text": user}]}
        ]
    
    def invoke(self, systemPrompt: str, userPrompt: str):
        prompt = self.buildPrompt(userPrompt)

        body = {
            "anthropic_version": self.version,
            "messages": prompt,
            "system": systemPrompt,
            "max_tokens": 2048,
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
    
    def _parse_response(self, text: str) -> str:
        try:
            start = text.index("{")
            end = text.rindex("}")

            explanation = text[:start].strip() + "\n" + text[end+1:].strip()
            json_str = text[start:end+1].strip()
            structured = json.loads(json_str)

            return explanation, structured
        except Exception as e:
            return text, {}