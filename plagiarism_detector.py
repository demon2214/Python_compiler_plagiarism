import ast
import re
import math
from collections import Counter
from difflib import SequenceMatcher

class TFIDFVectorizer:
    def __init__(self):
        self.vocabulary = {}
        self.idf = {}
        
    def tokenize(self, text):
        # Remove comments and normalize code
        text = re.sub(r'#.*', '', text)  # Remove comments
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Extract tokens (words, operators, keywords)
        tokens = re.findall(r'\w+|[^\w\s]', text.lower())
        return tokens
    
    def fit_transform(self, documents):
        # Build vocabulary
        all_tokens = []
        doc_tokens = []
        
        for doc in documents:
            tokens = self.tokenize(doc)
            doc_tokens.append(tokens)
            all_tokens.extend(set(tokens))
        
        self.vocabulary = {token: i for i, token in enumerate(set(all_tokens))}
        
        # Calculate IDF
        doc_count = len(documents)
        for token in self.vocabulary:
            containing_docs = sum(1 for tokens in doc_tokens if token in tokens)
            self.idf[token] = math.log(doc_count / (containing_docs + 1))
        
        # Create TF-IDF vectors
        vectors = []
        for tokens in doc_tokens:
            vector = [0] * len(self.vocabulary)
            token_counts = Counter(tokens)
            
            for token, count in token_counts.items():
                if token in self.vocabulary:
                    tf = count / len(tokens)
                    tfidf = tf * self.idf[token]
                    vector[self.vocabulary[token]] = tfidf
            
            vectors.append(vector)
        
        return vectors

def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

def normalize_code(code):
    """Normalize code for AST comparison"""
    try:
        tree = ast.parse(code)
        return ast.dump(tree, annotate_fields=False)
    except:
        return code

def ast_similarity(code1, code2):
    """Calculate similarity based on AST structure"""
    try:
        norm1 = normalize_code(code1)
        norm2 = normalize_code(code2)
        
        # Use sequence matcher on normalized AST
        matcher = SequenceMatcher(None, norm1, norm2)
        return matcher.ratio() * 100
    except:
        # Fallback to simple text similarity
        matcher = SequenceMatcher(None, code1, code2)
        return matcher.ratio() * 100

def calculate_similarity(code1, code2):
    """Calculate combined similarity score"""
    # TF-IDF similarity
    vectorizer = TFIDFVectorizer()
    vectors = vectorizer.fit_transform([code1, code2])
    tfidf_sim = cosine_similarity(vectors[0], vectors[1]) * 100
    
    # AST similarity
    ast_sim = ast_similarity(code1, code2)
    
    # Combined score (average)
    combined_score = (tfidf_sim + ast_sim) / 2
    
    return round(combined_score, 2)

def compare_codes_detailed(code1, code2):
    """Detailed comparison for visualization"""
    lines1 = code1.split('\n')
    lines2 = code2.split('\n')
    
    matcher = SequenceMatcher(None, lines1, lines2)
    
    comparison = {
        'lines1': [],
        'lines2': [],
        'similarity': calculate_similarity(code1, code2)
    }
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for i in range(i1, i2):
                comparison['lines1'].append({'line': lines1[i], 'type': 'equal'})
            for j in range(j1, j2):
                comparison['lines2'].append({'line': lines2[j], 'type': 'equal'})
        elif tag == 'delete':
            for i in range(i1, i2):
                comparison['lines1'].append({'line': lines1[i], 'type': 'delete'})
        elif tag == 'insert':
            for j in range(j1, j2):
                comparison['lines2'].append({'line': lines2[j], 'type': 'insert'})
        elif tag == 'replace':
            for i in range(i1, i2):
                comparison['lines1'].append({'line': lines1[i], 'type': 'replace'})
            for j in range(j1, j2):
                comparison['lines2'].append({'line': lines2[j], 'type': 'replace'})
    
    return comparison
