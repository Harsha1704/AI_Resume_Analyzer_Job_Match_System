import pandas as pd
import re
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download("wordnet")
nltk.download("stopwords")


# =========================
# 1️⃣ Load Dataset
# =========================
data = pd.read_csv("datasets/resumes_dataset.csv")

print("Dataset Shape:", data.shape)
print("\nCategory Distribution:\n")
print(data["Category"].value_counts())


# =========================
# 2️⃣ Select Columns
# =========================
X = data["Resume_html"].astype(str)
y = data["Category"]


# =========================
# 3️⃣ NLP Preprocessing
# =========================
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def clean_text(text):

    # Remove HTML
    text = re.sub(r'<.*?>', ' ', text)

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", "", text)

    # Remove special characters
    text = re.sub(r"[^a-zA-Z ]", " ", text)

    text = text.lower()

    words = text.split()

    # Remove stopwords + lemmatize
    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)


print("\nCleaning Resume Text...")
X = X.apply(clean_text)


# =========================
# 4️⃣ TF-IDF Vectorization
# =========================
vectorizer = TfidfVectorizer(
    max_features=60000,
    ngram_range=(1,3),
    min_df=2,
    max_df=0.9
)

X_vectorized = vectorizer.fit_transform(X)


# =========================
# 5️⃣ Train/Test Split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# =========================
# 6️⃣ Train Model
# =========================
print("\nTraining Model...")

model = LinearSVC(class_weight="balanced")

model.fit(X_train, y_train)


# =========================
# 7️⃣ Model Evaluation
# =========================
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n🔥 Final Accuracy:", accuracy)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

print("\n🧠 Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))


# =========================
# 8️⃣ Save Model
# =========================
os.makedirs("backend/models", exist_ok=True)

pickle.dump(model, open("backend/models/role_prediction.pkl", "wb"))
pickle.dump(vectorizer, open("backend/models/tfidf_vectorizer.pkl", "wb"))

print("\n✅ Model and Vectorizer Saved Successfully!")