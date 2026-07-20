# # i so rough coding here it was gitignored before nut i guess it is cool to let people see the process of writing SafeAgent

# import time 
# x = 100
# addition =0
import math
from collections import Counter
# from collections import Counter
# import time

# import pandas as pd
# file = pd.read_csv("C:/Users/iqmbe/Downloads/data.csv")
# # file.columns()
# print(file.columns)
# bloom_filter = ['million','billion']
# # for i in range(1,101):
# #     addition +=i
# # print(addition)

# # def x(int,addition=0,counter = 10000000000000000000000):
# #     counter -=1
# #     addition +=int 
# #     int -=1
# #     if counter == 0:
# #         print(addition)
# #         return addition
# #     return x(int,addition,counter)
# # while x>=100:
# #     x+=1
# # x(100)
# def entropy_score(word):
#         length = len(word)
#         frequency = Counter(word)
#         # check_numbers(word)
#         # print(frequency)
#         # entropy = 0.0
#         # for count in frequency.values():
#         #     probability = count / length
#         #     entropy -= probability * math.log2(probability)
#         # return entropy

# # change try except to is digit later 
# def check_numbers_dict(counts: dict, word):
#     """This is used to count the number of consecutive integers in a string the dic is coming from count """
#     count = 0
#     not_int = 0
#     list_consistency = []
#     for key, values in counts.items():
#         # print(key)
#         if key.isdigit():
#             key = int(key)
#             count += values
#             not_int = 0 
#         else:
#             not_int += values
#             if not_int > 1:
#                 continue
#             count = 0
#     list_consistency.append(count)
#     if len(list_consistency) == 0 or list_consistency[0]/word > 0.5: 
#         pass    
#         # print('good')
#     # print(count,list_consistency)
#     return count    
# # entropy_score('$104563.66.45')



# def check_numbers(word: str):
#     """This is used to count the number of consecutive integers in a string the dic is coming from count """
#     count = 0
#     not_int = 0 #this is to track consistency in words. I am going to use this to give a buffer 
#     consistency = 0
#     split_word = ''
#     # consistency always adds
#     for index in word:
#         if index.isdigit():
#             not_int = 0 
#             count += 1
#             if count != 0: #this is to make sure that consistency cleans the split word (this should likely not be here)
#               split_word = ''
#         else:
#             split_word += index
#             not_int += 1
#             if not_int < 2:
#                 continue
#             if count > consistency: #this is to make sure it does not overwrite the most consistent number count
#                 consistency = count
#             count = 0
#     if count > consistency:
#         consistency = count
#     if consistency/len(word) > 0.5:
#         return 0
#     elif split_word.lower() in bloom_filter:
#         return 0
#     print([split_word,consistency])
#     return 100, consistency/len(word)    
# print(check_numbers("$Dgye6890"))

# # if __name__ == "__main__":
# #     print(check_numbers('$3.5million'))
# #     num = 500
# #     t = time.time
# #     while num >0:
# #         entropy_score('$3.5million')
# #         num -=1
# #     print(time.time()-t)
# # print("3444.44".strip('.,;\'[]}({)<!>"?:=%\n\t'))

# def entropy_score_1(word):
#         """This is used to calculate the entropy score"""
#         length = len(word)
#         frequency = Counter(word)
#         entropy = 0.0
#         for count in frequency.values():
#             probability = count / length
#             entropy -= probability * math.log2(probability)
#         print(entropy)

# #my shannon entropy 
# def entropy_score( word):
#         """This is used to calculate the entropy score"""
#         length = len(word)
#         frequency = Counter(word)
#         print(frequency)
#         print(len(frequency))
#         entropy = len(frequency)/len(word)* math.log2(len(frequency))
#         print(entropy,'\n\n')
# entropy_score('qwertyuiq')
# entropy_score_1('qwertyuiq')
# # print(len({'ben':3,'same':'fff','fff': 4}))
# print(t'this is a t string')
# ll = [1,2,3,4,5,6,7,4,5,6,7]
# new_l = [x*2 if x>2 else x-2 for x in ll]
# # print(new_l)

# z = "bjfiw jwnviownov wngoiwnoginw wngoiiwng".split(" ")
# word = " ".join(z)
# ll += z
# print(ll,word)
# def check_numbers(word: str,stripped_word: str, bloom_filter):
#     print(word+"     This word is checked")
#     """This is used to count the number of consecutive integers in a string the dic is coming from count . It is used to fix shannon entropy redacting valid integers numbers bug e.g $3.5million $12345.78606"""
#     count = 0 #this is to track most recurring numbers
#     not_int = 0 #this is to track consistency in words. I am going to use this to give a buffer 
#     consistency = 0
#     split_word = ' '
#     for index in stripped_word:
#         if index.isdigit():
#             not_int = 0 
#             count += 1
#             if count != 0: #this is to make sure that consistency cleans the split word (this should likely not be here)
#               split_word = ''
#         else:
#             split_word += index
#             not_int += 1
#             if not_int < 2:
#                 continue
#             if count > consistency: #this is to make sure it does not overwrite the most consistent number count
#                 consistency = count
#             count = 0
#     ratio_of_consistency_to_word = consistency/len(word)
#     print(consistency,len(word),split_word)
#     if count > consistency:
#         consistency = count
#     if ratio_of_consistency_to_word > 0.5:
#         return word
#     elif (split_word != "") and (len(split_word)>=3) and (split_word in bloom_filter) and (consistency != 0) and (ratio_of_consistency_to_word > 0.1):
#         # print([stripped_word,split_word,consistency,len(word),consistency/len(word)])
#         return word
#     return "[REDACTED SECRET]"

# def compound_word(word,stripped_word=None,bloom_filter= None):
#     """This is used to check each word in a compound word in the bloom filter if it is valid. Ir also checks for words joined with full stop or comma without space e.g end.now , cake,butter,yam"""
#     word_list = word_splitter(word)
#     double_check = True
#     while double_check:
#         no_sub_list = True
#         for index,word in enumerate(word_list):
#             if '_' in word or '-' in word or ',' in word or '.' in word:
#                 print(word,index)
#                 sub_word_list = word_splitter(word)
#                 word_list.extend(sub_word_list)
#                 no_sub_list = False
#                 del(word_list[index])
#         if no_sub_list:
#             double_check = False
                
        
#     print(word_list)
# #     for index in word_list:
# #         if index  not in bloom_filter:
# #             check_numbers_result = check_numbers(word,stripped_word,bloom_filter) #check if every word in the valid compound word is a valid number(for words in not in the bloom filter originally)
# #             if check_numbers_result == "[REDACTED SECRET]":
# #                 return "[REDACTED SECRET]"
# #     return word

# def word_splitter(stripped_word: str):
#     if "-" in stripped_word:
#         word_list = stripped_word.split("-")
#     elif "_" in stripped_word:
#         word_list = stripped_word.split("_")
#     elif "." in stripped_word:
#         word_list = stripped_word.split(".")
#     elif ',' in stripped_word:
#         word_list = stripped_word.split(",")
#     return word_list

# print(compound_word("cake-boy,yam.dog"))
import httpx
import asyncio
async def prompt_guard_node(state):
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            "http://127.0.0.1:8000/v1/safeagent/prompt",
            json={
                "user_id": "test_id",
                "role": "user",
                "prompt": state
            }

        )
    return result.json()
# result = await prompt_guard_node("whats up")
async def tool_guard_node(state):
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            "http://127.0.0.1:8000/v1/safeagent/tool_output",
            json={
                "role": "tool",
                "tool_call_id": "call_vctR_hungary_092",
                "name": "search_pinecone_db",
                "content": state
            }

        )
    return result.json()
async def output_guard_node(state):
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            "http://127.0.0.1:8000/v1/safeagent/final_output",
            json={
                "output": state
            }

        )
    return result.json()
print(asyncio.run(output_guard_node("whats up ? how are you doing today this is my credit card number 4444-5555-6666-6767")))