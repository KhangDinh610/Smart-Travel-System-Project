from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
import difflib

class DuplicateDetector:
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        # paraphrase-multilingual models are good for Vietnamese
        self.model = SentenceTransformer(model_name)
        # Cache to store embeddings: {text_string: tensor}
        self.embedding_cache = {}

    def get_embedding(self, text):
        if text not in self.embedding_cache:
            self.embedding_cache[text] = self.model.encode(text, convert_to_tensor=True)
        return self.embedding_cache[text]

    def _get_embeddings_batch(self, texts):
        uncached_texts = [t for t in texts if t not in self.embedding_cache]
        if uncached_texts:
            new_embeddings = self.model.encode(uncached_texts, convert_to_tensor=True)
            for text, emb in zip(uncached_texts, new_embeddings):
                self.embedding_cache[text] = emb
        
        # Stack all tensors from cache into a single batched tensor
        return torch.stack([self.embedding_cache[t] for t in texts])

    def get_lexical_similarity(self, text1, text2):
        # Calculate text similarity based on character sequences (good for typos)
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def check_duplicate(self, target_text, existing_products, semantic_threshold=0.85, lexical_threshold=0.85):
        """
        existing_products: list of dicts with 'id' and 'text'
        """
        if not existing_products:
            return None

        target_embedding = self.get_embedding(target_text)
        sentences = [p['text'] for p in existing_products]
        
        # Efficiently get all embeddings using cache
        sentence_embeddings = self._get_embeddings_batch(sentences)

        # Compute cosine-similarities
        cos_scores = util.cos_sim(target_embedding, sentence_embeddings)[0]
        
        # Get semantic max
        semantic_max_score_idx = np.argmax(cos_scores.cpu().numpy())
        semantic_max_score = cos_scores[semantic_max_score_idx].item()

        # Compute Lexical similarities
        lexical_scores = [self.get_lexical_similarity(target_text, text) for text in sentences]
        lexical_max_score_idx = np.argmax(lexical_scores)
        lexical_max_score = lexical_scores[lexical_max_score_idx]

        # Determine best match
        best_match = None
        best_score = 0
        best_type = ""
        
        # 1. Check Substring first for strong containment (using name part)
        target_name = target_text.split('|')[0].strip().lower()
        substring_match_idx = -1
        if len(target_name) >= 3:
            for idx, text in enumerate(sentences):
                existing_name = text.split('|')[0].strip().lower()
                if len(existing_name) >= 3:
                    if target_name in existing_name or existing_name in target_name:
                        substring_match_idx = idx
                        break
        
        if substring_match_idx != -1:
            best_match = existing_products[substring_match_idx]
            best_score = 0.95 # Assign high score for substring match
            best_type = "Substring"
        
        # 2. Check Semantic
        if semantic_max_score >= semantic_threshold and semantic_max_score > best_score:
            best_match = existing_products[semantic_max_score_idx]
            best_score = semantic_max_score
            best_type = "Semantic"
            
        # 3. Check Lexical
        if lexical_max_score >= lexical_threshold and lexical_max_score > best_score:
            best_match = existing_products[lexical_max_score_idx]
            best_score = lexical_max_score
            best_type = "Lexical"

        # Return comprehensive result
        return {
            "id": best_match['id'] if best_match else None,
            "text": best_match['text'] if best_match else None,
            "score": float(best_score),
            "semantic_score": float(semantic_max_score),
            "lexical_score": float(lexical_max_score),
            "match_type": best_type if best_match else "None"
        }
