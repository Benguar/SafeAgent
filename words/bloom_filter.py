from rbloom import Bloom
import hashlib
def bloom_hash(word):
    return int(hashlib.sha256(word.encode('utf-8')).hexdigest()[:16], 16)
bf = Bloom(expected_items=600000,false_positive_rate=0.00001, hash_func=bloom_hash)
languages = ["words/english.txt","words/hungarian.txt"]
count = 0
for index in languages:
    with open(index, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            bf.add(word)
            count+=1
bf.save("words/words.bloom")
if __name__ == "__main__":
    print(count)