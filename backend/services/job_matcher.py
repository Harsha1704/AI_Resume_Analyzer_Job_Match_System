import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from config import DATASET_FOLDER, MODEL_FOLDER

def match_jobs(resume_text: str):
    job_data = pd.read_csv(f"{DATASET_FOLDER}/job_descriptions.csv")

    vectorizer = joblib.load(f"{MODEL_FOLDER}/tfidf_vectorizer.pkl")

    job_vectors = vectorizer.transform(job_data["description"])
    resume_vector = vectorizer.transform([resume_text])

    similarity_scores = cosine_similarity(resume_vector, job_vectors).flatten()

    job_data["match_score"] = similarity_scores
    top_jobs = job_data.sort_values(by="match_score", ascending=False).head(5)

    return top_jobs[["job_title", "match_score"]].to_dict(orient="records")