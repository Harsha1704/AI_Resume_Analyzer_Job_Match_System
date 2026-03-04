import pandas as pd
import re
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report


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
X = data["Resume_html"].astype(str)   # Use HTML column
y = data["Category"]


# =========================
# 3️⃣ Clean Text Function
# =========================
def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', ' ', text)

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", "", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z ]", " ", text)

    # Convert to lowercase
    text = text.lower()

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


X = X.apply(clean_text)


# =========================
# 4️⃣ TF-IDF Vectorization
# =========================
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=50000,
    ngram_range=(1, 3),   # Unigram + Bigram + Trigram
    min_df=2,
    max_df=0.85
)

X_vectorized = vectorizer.fit_transform(X)


# =========================
# 5️⃣ Train-Test Split
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
model = LinearSVC(class_weight="balanced")

model.fit(X_train, y_train)


# =========================
# 7️⃣ Evaluation
# =========================
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n🔥 Final Accuracy:", accuracy)
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))


# =========================
# 8️⃣ Save Model + Vectorizer
# =========================
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("\n✅ Model and Vectorizer Saved Successfully!")