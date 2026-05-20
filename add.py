import time 
x = 100
addition =0
import math
from collections import Counter
import time
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
        check_numbers(word)
        # print(frequency)
        # entropy = 0.0
        # for count in frequency.values():
        #     probability = count / length
        #     entropy -= probability * math.log2(probability)
        # return entropy

# change try except to is digit later 
def check_numbers(word):
    """This is used to count the number of consecutive integers in a string the dic is coming from count """
    count = 0
    not_int = 0
    list_consistency = []
    for index in word:
        if index.isdigit():
            count += 1
            not_int = 0 
        else:
            not_int += 1
            if not_int > 1:
                continue
            # if count > consistency: #this is to make sure it does not overwrite the most consistent workspace
            #     cobnsistency = count
            if len(list_consistency) ==0:
                list_consistency.append(count)
            elif list_consistency[0] < count:
                list_consistency[0] = count
            count = 0
    if len(list_consistency) == 0 or list_consistency[0]/word > 0.5: 
        return 0
    return 100    
entropy_score('$104563.66.45')
if __name__ == "__main__":
    num = 500
    t = time.time()
    while num >0:
        entropy_score('$104563.66.45')
        num -=1
    print(time.time()-t)
#find a way that this only runs when the entropy is high and it contains digit 
# print("3444.44".strip('.,;\'[]}({)<!>"?:=%\n\t'))