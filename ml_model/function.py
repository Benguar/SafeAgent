import joblib
import time
# model = joblib.load('ml_model/model.pkl')
# vectorizer = joblib.load('ml_model/vectorizer.pkl')
def ml_scan(prompt,model,vectorizer):
    now = time.time()
    prompt_vector = vectorizer.transform([prompt])
    ml_score = model.predict_proba(prompt_vector)[0]
    injection_score = ml_score[1]
    print(f'{time.time() - now}')
    return injection_score
    if __name__ == "__main__":
        print(injection_score, ml_score)
