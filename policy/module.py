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
    @property
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
    def sanitize_prompt(self,sanitize_policy,bloom_filter):
        prompt = self.prompt
        for policy in sanitize_policy:
            prompt = policy['pattern'].sub(policy['action'], prompt)
        if prompt != self.prompt:
            decision = "SANITIZE"
        else:
            decision = "ALLOW"
        self.prompt = prompt
        entropy_prompt,sanitized_words = self.check_secrets(bloom_filter=bloom_filter)
        return prompt,decision,entropy_prompt,sanitized_words
    def entropy_score(self, word):
        """This is used to calculate the entropy score"""
        length = len(word)
        frequency = Counter(word)
        entropy = 0.0
        for count in frequency.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    def check_secrets(self,bloom_filter):
        sanitized_words = []
        self_list = self.prompt.split()
        for i,word in enumerate(self_list):
            stripped_word = word.strip('.,;\'[]}({)<!>"?:=%\n\t').lower()
            if len(stripped_word) > 8:
                score = self.entropy_score(word=word)
                if len(stripped_word) >= 16 and score >= 3.7:
                    if stripped_word not in bloom_filter:
                        if '_' in word or '-' in word:
                            #this is used to check is any redacted word is a compound word so we can check each word in it
                            self_list[i] = compound_word(word,stripped_word,bloom_filter)
                            if self_list[i] == "[REDACTED SECRET]":
                                sanitized_words.append(word)
                        else:
                            #if a word is not a compound word and is not in the bloom filter this is used to check if the word is a valid number 
                            check_numbers_result = check_numbers(word,stripped_word,bloom_filter)
                            if check_numbers_result == "[REDACTED SECRET]":
                                sanitized_words.append(self_list[i])
                                self_list[i] = "[REDACTED SECRET]"
                elif 8 <= len(stripped_word) < 16 and score >= 3:
                    #condition for words from length 8 to length 16 with high entropy
                    if stripped_word not in bloom_filter:
                        if '_' in word or '-' in word:
                                #this is used to check is any redacted word is a compound word so we can check each word in it
                                self_list[i] = compound_word(word,stripped_word,bloom_filter)
                                #add here 
                                if self_list[i] == "[REDACTED SECRET]":
                                    sanitized_words.append(word)
                        else:
                            #if a word is not a compound word and is not in the bloom filter this is used to check if the word is a valid number 
                            check_numbers_result = check_numbers(word,stripped_word,bloom_filter)
                            if check_numbers_result == "[REDACTED SECRET]":
                                sanitized_words.append(self_list[i])
                                self_list[i] = "[REDACTED SECRET]"
        return (" ".join(self_list),sanitized_words)


def check_numbers(word: str,stripped_word: str, bloom_filter):
    """This is used to count the number of consecutive integers in a string the dic is coming from count . It is used to fix shannon entropy redacting valid integers numbers bug e.g $3.5million $12345.78606"""
    count = 0
    not_int = 0 #this is to track consistency in words. I am going to use this to give a buffer 
    consistency = 0
    split_word = ''
    for index in stripped_word:
        if index.isdigit():
            not_int = 0 
            count += 1
            if count != 0: #this is to make sure that consistency cleans the split word (this should likely not be here)
              split_word = ''
        else:
            split_word += index
            not_int += 1
            if not_int < 2:
                continue
            if count > consistency: #this is to make sure it does not overwrite the most consistent number count
                consistency = count
            count = 0
    if count > consistency:
        consistency = count
    if consistency/len(word) > 0.5:
        return word
    elif split_word.lower()  in bloom_filter and consistency != 0:
        return word
    return "[REDACTED SECRET]"

def compound_word(word,stripped_word,bloom_filter):
    """This is used to check each word in a compound word in the bloom filter if it is valid"""
    if "-" in stripped_word:
        word_list = stripped_word.split("-")
    else:
        word_list = stripped_word.split("_")
    # print(list)
    for index in word_list:
        if index  not in bloom_filter:
            check_numbers_result = check_numbers(word,stripped_word,bloom_filter) #check if every word in the valid compound word is a valid number(for words in not in the bloom filter originally)
            if check_numbers_result == "[REDACTED SECRET]":
                return "[REDACTED SECRET]"
    return word
