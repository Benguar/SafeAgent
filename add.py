# i so rough coding here it was gitignored before nut i guess it is cool to let people see the process of writing SafeAgent

import time 
x = 100
addition =0
import math
from collections import Counter
import time

bloom_filter = ['million','billion']
# for i in range(1,101):
#     addition +=i
# print(addition)

# def x(int,addition=0,counter = 10000000000000000000000):
#     counter -=1
#     addition +=int 
#     int -=1
#     if counter == 0:
#         print(addition)
#         return addition
#     return x(int,addition,counter)
# while x>=100:
#     x+=1
# x(100)
def entropy_score(word):
        length = len(word)
        frequency = Counter(word)
        # check_numbers(word)
        # print(frequency)
        # entropy = 0.0
        # for count in frequency.values():
        #     probability = count / length
        #     entropy -= probability * math.log2(probability)
        # return entropy

# change try except to is digit later 
def check_numbers_dict(counts: dict, word):
    """This is used to count the number of consecutive integers in a string the dic is coming from count """
    count = 0
    not_int = 0
    list_consistency = []
    for key, values in counts.items():
        # print(key)
        if key.isdigit():
            key = int(key)
            count += values
            not_int = 0 
        else:
            not_int += values
            if not_int > 1:
                continue
            count = 0
    list_consistency.append(count)
    if len(list_consistency) == 0 or list_consistency[0]/word > 0.5: 
        pass    
        # print('good')
    # print(count,list_consistency)
    return count    
# entropy_score('$104563.66.45')



def check_numbers(word: str):
    """This is used to count the number of consecutive integers in a string the dic is coming from count """
    count = 0
    not_int = 0 #this is to track consistency in words. I am going to use this to give a buffer 
    consistency = 0
    split_word = ''
    # consistency always adds
    for index in word:
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
        return 0
    elif split_word.lower() in bloom_filter:
        return 0
    print([split_word,consistency])
    return 100    
print(check_numbers("$3.5million"))

if __name__ == "__main__":
    print(check_numbers('$3.5million'))
    num = 500
    t = time.time
    while num >0:
        entropy_score('$3.5million')
        num -=1
    print(time.time()-t)
print("3444.44".strip('.,;\'[]}({)<!>"?:=%\n\t'))