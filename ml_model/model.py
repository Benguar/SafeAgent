import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import time
times = time.time()

data = pd.read_csv("./ml_model/The_file_to_use.csv")
prompt = data["Prompt"]
weight = data["Weight"]
prompt_train, prompt_test, weight_train, weight_test = train_test_split(prompt, weight, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=10000)
prompt_train_vector = vectorizer.fit_transform(prompt_train)
prompt_test_vector = vectorizer.transform(prompt_test)

model = LogisticRegression(random_state= 42)
model.fit(prompt_train_vector,weight_train)

prediction = model.predict(prompt_test_vector)
print(classification_report(weight_test, prediction, target_names=['legitimate', 'injection']))

joblib.dump(model,'ml_model/model.pkl')
joblib.dump(vectorizer, 'ml_model/vectorizer.pkl')
