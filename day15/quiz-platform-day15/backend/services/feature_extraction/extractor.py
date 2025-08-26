import nltk
import textstat
import spacy
import numpy as np
from typing import Dict, List
import re
from collections import Counter
import math

class FeatureExtractor:
    def __init__(self):
        self.nlp = None
        self._download_nltk_data()
        self._load_spacy_model()
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def _load_spacy_model(self):
        """Load spaCy model for advanced NLP features"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️  spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_readability_features(self, text: str) -> Dict[str, float]:
        """Extract readability-based features"""
        return {
            'flesch_kincaid': textstat.flesch_kincaid_grade(text),
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'gunning_fog': textstat.gunning_fog(text),
            'automated_readability': textstat.automated_readability_index(text),
            'coleman_liau': textstat.coleman_liau_index(text)
        }
    
    def extract_syntactic_features(self, text: str) -> Dict[str, float]:
        """Extract syntactic complexity features"""
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        
        features = {
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_word_length': np.mean([len(word) for word in words if word.isalpha()]),
            'punctuation_density': len([c for c in text if c in '.,!?;:']) / max(len(text), 1)
        }
        
        if self.nlp:
            doc = self.nlp(text)
            features.update({
                'dependency_depth': self._calculate_dependency_depth(doc),
                'pos_diversity': len(set([token.pos_ for token in doc])) / max(len(doc), 1),
                'named_entity_density': len(doc.ents) / max(len(doc), 1)
            })
        
        return features
    
    def extract_vocabulary_features(self, text: str) -> Dict[str, float]:
        """Extract vocabulary difficulty features"""
        words = [word.lower() for word in nltk.word_tokenize(text) if word.isalpha()]
        word_freq = Counter(words)
        
        # Simple vocabulary difficulty based on word frequency and length
        difficult_words = [word for word in words if len(word) > 6]
        rare_words = [word for word, freq in word_freq.items() if freq == 1]
        
        return {
            'difficult_word_ratio': len(difficult_words) / max(len(words), 1),
            'rare_word_ratio': len(rare_words) / max(len(words), 1),
            'vocabulary_diversity': len(set(words)) / max(len(words), 1),
            'avg_word_frequency': np.mean(list(word_freq.values()))
        }
    
    def extract_question_type_features(self, text: str, question_type: str) -> Dict[str, float]:
        """Extract question type specific features"""
        question_words = ['what', 'where', 'when', 'why', 'how', 'which', 'who']
        text_lower = text.lower()
        
        features = {
            'has_question_word': any(word in text_lower for word in question_words),
            'question_word_count': sum(1 for word in question_words if word in text_lower),
            'is_negative_question': 'not' in text_lower or "n't" in text_lower,
            'has_multiple_clauses': text.count(',') + text.count(';') > 1
        }
        
        # Question type complexity mapping
        type_complexity = {
            'multiple_choice': 0.3,
            'true_false': 0.2,
            'fill_blank': 0.4,
            'short_answer': 0.6,
            'essay': 0.8
        }
        
        features['question_type_complexity'] = type_complexity.get(question_type, 0.5)
        return features
    
    def _calculate_dependency_depth(self, doc) -> float:
        """Calculate average dependency tree depth"""
        depths = []
        for sent in doc.sents:
            for token in sent:
                depth = 0
                current = token
                while current.head != current:
                    depth += 1
                    current = current.head
                depths.append(depth)
        return np.mean(depths) if depths else 0
    
    def extract_all_features(self, text: str, question_type: str, subject: str = None) -> Dict[str, float]:
        """Extract all features for difficulty classification"""
        features = {}
        
        # Core feature extraction
        features.update(self.extract_readability_features(text))
        features.update(self.extract_syntactic_features(text))
        features.update(self.extract_vocabulary_features(text))
        features.update(self.extract_question_type_features(text, question_type))
        
        # Subject-specific adjustments
        if subject:
            subject_complexity = {
                'mathematics': 0.8,
                'physics': 0.9,
                'chemistry': 0.8,
                'biology': 0.6,
                'history': 0.5,
                'geography': 0.4,
                'literature': 0.7,
                'computer_science': 0.9
            }
            features['subject_complexity'] = subject_complexity.get(subject.lower(), 0.5)
        
        return features
