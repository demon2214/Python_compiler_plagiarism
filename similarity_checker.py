import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import astunparse

class CodeSimilarityChecker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        
    def normalize_code(self, code):
        """Normalize code by parsing AST and extracting structure"""
        try:
            tree = ast.parse(code)
            
            # Remove comments and docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and \
                       isinstance(node.body[0].value, ast.Str):
                        node.body = node.body[1:]
            
            # Normalize variable and function names
            normalized_tree = self.normalize_names(tree)
            
            # Unparse back to code
            normalized_code = astunparse.unparse(normalized_tree)
            
            # Remove all string literals
            normalized_code = self.remove_string_literals(normalized_code)
            
            return normalized_code
        except Exception as e:
            print(f"Error normalizing code: {str(e)}")
            return code  # Fallback to raw code if parsing fails
    
    def normalize_names(self, tree):
        """Normalize all variable and function names"""
        name_map = {}
        next_id = 1
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
                if node.id not in name_map:
                    name_map[node.id] = f"var_{next_id}"
                    next_id += 1
                node.id = name_map[node.id]
            elif isinstance(node, ast.FunctionDef):
                if node.name not in name_map:
                    name_map[node.name] = f"func_{next_id}"
                    next_id += 1
                node.name = name_map[node.name]
        
        return tree
    
    def remove_string_literals(self, code):
        """Remove string literals from code"""
        try:
            tree = ast.parse(code)
            
            class StringRemover(ast.NodeTransformer):
                def visit_Str(self, node):
                    return None
            
            modified_tree = StringRemover().visit(tree)
            return astunparse.unparse(modified_tree)
        except:
            return code
    
    def calculate_similarity(self, code1, code2):
        """Calculate similarity between two code snippets"""
        norm1 = self.normalize_code(code1)
        norm2 = self.normalize_code(code2)
        
        # TF-IDF similarity
        tfidf_matrix = self.vectorizer.fit_transform([norm1, norm2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return similarity
    
    def find_similar_submissions(self, submissions, threshold=0.7):
        """Find groups of similar submissions"""
        if len(submissions) < 2:
            return []
            
        # Preprocess all submissions
        normalized = [self.normalize_code(sub['code']) for sub in submissions]
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(normalized)
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(tfidf_matrix)
        
        # Group similar submissions
        groups = []
        used = set()
        
        for i in range(len(similarities)):
            if i not in used:
                group = [submissions[i]]
                for j in range(i+1, len(similarities)):
                    if similarities[i][j] >= threshold:
                        group.append(submissions[j])
                        used.add(j)
                if len(group) > 1:
                    group_similarities = [similarities[i][j] for j in range(i+1, len(similarities)) 
                                        if similarities[i][j] >= threshold]
                    groups.append({
                        'submissions': group,
                        'avg_similarity': np.mean(group_similarities) if group_similarities else 0
                    })
        return groups