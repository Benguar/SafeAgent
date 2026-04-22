import yaml
import re
import unicodedata
import httpx
import re
import asyncio
import pathlib
import math
from collections import Counter
from src.config.settings import settings

class policy(object):
    def __init__(self, prompt: str):
        self.prompt = prompt
    def normalize_prompt(self):
        prompt = self.prompt
        prompt = unicodedata.normalize("NFKC",prompt)
        self.prompt = prompt
        return prompt
    async def scan_prompt(self,client):
        OPA_URL = settings.OPA_URL
        prompt = self.prompt
        clean_prompt = str.maketrans( "04@31$78([5*+†9", "oaaeistbccsottg")
        cleaned_words = [word.translate(clean_prompt) if re.search(r'[a-z]', word) else word for word in prompt.lower().split()]
        prompt = ' '.join(cleaned_words)
        prompt = re.sub(r'[^a-z0-9]', ' ', prompt)
        payload = {"input": {"prompt": prompt}}
        try:
            response = await client.post(OPA_URL, json= payload)
            response.raise_for_status()
            decision = response.json().get("result",{})

            return {
                "block": decision.get("block_prompt"),
                "violations": decision.get("violation_ids"),
                "weight": decision.get("weight")
            }
        except httpx.RequestError as e:
            print(f"OPA Connection Error: {e}")
            return {
                "block": True,
                "violations": ["OPA unreachable"],
            }
    def sanitize_prompt(self,sanitize_policy):
        prompt = self.prompt
        for policy in sanitize_policy:
            prompt = policy['pattern'].sub(policy['action'], prompt)
        if prompt != self.prompt:
            decision = "SANITIZE"
        else:
            decision = "ALLOW"
        return prompt,decision
    def entropy_score(self, word):
        length = len(word)
        frequency = Counter(word)
        entropy = 0.0
        for count in frequency.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        return entropy
    def check_secrets(self):
        sanitized_words = []
        self_list = self.prompt.split()
        for i,word in enumerate(self_list):
            if len(word) > 8:
                score = self.entropy_score(word=word)
                if len(word) >= 16 and score >= 3.8:
                        sanitized_words.append(self_list[i])
                        self_list[i] = "[REDACTED SECRET]"
                elif 8 <= len(word) < 16 and score >= 3.0:
                    sanitized_words.append(self_list[i])
                    self_list[i] = "[REDACTED SECRET]"
        return " ".join(self_list),sanitized_words

                
if __name__ == "__main__":
    test = policy("this is beneddhdhvbdict fiefiebghefeu $Sdnfjeu^^&#")
    print(test.check_secrets())
