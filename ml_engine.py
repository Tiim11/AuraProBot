from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FAQAnswerEngine:
    def __init__(self, faq_dict):
        self.faq_dict = faq_dict
        self.questions = [item["question"] for item in faq_dict.values()]
        self.keys = list(faq_dict.keys())
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.model.encode(self.questions)

    def find_best_match(self, user_input, threshold=0.6):
        user_vec = self.model.encode([user_input])
        sims = cosine_similarity(user_vec, self.embeddings)[0]
        best_idx = np.argmax(sims)
        best_score = sims[best_idx]

        if best_score >= threshold:
            best_key = self.keys[best_idx]
            return self.faq_dict[best_key]["question"], self.faq_dict[best_key]["answer"]
        else:
            return None, None
