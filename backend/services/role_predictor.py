import joblib
from config import MODEL_FOLDER

def predict_role(resume_text: str):
    model = joblib.load(f"{MODEL_FOLDER}/role_prediction.pkl")
    vectorizer = joblib.load(f"{MODEL_FOLDER}/tfidf_vectorizer.pkl")

    vector = vectorizer.transform([resume_text])
    prediction = model.predict(vector)[0]

    return prediction