from typing import Dict, Any, List
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

class VersionCompatibilityService:
    """Handles backward compatibility between API versions"""
    
    def __init__(self):
        self.v1_to_v2_adapters = {
            "quiz_response": self.adapt_quiz_v1_to_v2,
            "question_response": self.adapt_question_v1_to_v2
        }
        self.v2_to_v1_adapters = {
            "quiz_response": self.adapt_quiz_v2_to_v1,
            "question_response": self.adapt_question_v2_to_v1
        }
    
    def adapt_response(self, data: Dict[str, Any], from_version: str, 
                      to_version: str, response_type: str) -> Dict[str, Any]:
        """Adapt response data between versions"""
        
        if from_version == to_version:
            return data
            
        adapter_key = f"{from_version}_to_{to_version}_adapters"
        adapters = getattr(self, adapter_key, {})
        
        adapter_func = adapters.get(response_type)
        if not adapter_func:
            logger.warning(f"No adapter found for {response_type} from {from_version} to {to_version}")
            return data
            
        return adapter_func(data)
    
    def adapt_quiz_v1_to_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v1 quiz format to v2 with AI enhancements"""
        adapted = data.copy()
        
        # Add new v2 fields
        adapted["ai_difficulty_score"] = self.calculate_ai_difficulty(data.get("questions", []))
        adapted["ai_tags"] = self.generate_ai_tags(data.get("title", ""), data.get("questions", []))
        adapted["estimated_duration"] = len(data.get("questions", [])) * 90  # 1.5 min per question
        adapted["adaptive_scoring"] = True
        
        # Transform questions
        if "questions" in adapted:
            adapted["questions"] = [
                self.adapt_question_v1_to_v2(q) for q in adapted["questions"]
            ]
        
        return adapted
    
    def adapt_quiz_v2_to_v1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v2 quiz format back to v1 (remove new fields)"""
        adapted = data.copy()
        
        # Remove v2-specific fields
        v2_only_fields = ["ai_difficulty_score", "ai_tags", "estimated_duration", "adaptive_scoring"]
        for field in v2_only_fields:
            adapted.pop(field, None)
            
        # Transform questions back to v1 format
        if "questions" in adapted:
            adapted["questions"] = [
                self.adapt_question_v2_to_v1(q) for q in adapted["questions"]
            ]
            
        return adapted
    
    def adapt_question_v1_to_v2(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Add AI enhancements to question format"""
        adapted = question.copy()
        adapted["difficulty_level"] = self.estimate_question_difficulty(question)
        adapted["cognitive_load"] = self.calculate_cognitive_load(question)
        adapted["hint"] = self.generate_hint(question)
        return adapted
    
    def adapt_question_v2_to_v1(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Remove v2 question enhancements"""
        adapted = question.copy()
        v2_fields = ["difficulty_level", "cognitive_load", "hint"]
        for field in v2_fields:
            adapted.pop(field, None)
        return adapted
    
    def calculate_ai_difficulty(self, questions: List[Dict]) -> float:
        """Calculate overall quiz difficulty using AI metrics"""
        if not questions:
            return 1.0
            
        total_difficulty = sum(
            len(q.get("question", "").split()) * 0.1 + 
            len(q.get("options", [])) * 0.05 
            for q in questions
        )
        return min(10.0, max(1.0, total_difficulty / len(questions)))
    
    def generate_ai_tags(self, title: str, questions: List[Dict]) -> List[str]:
        """Generate relevant tags for the quiz"""
        tags = ["auto-generated"]
        
        # Simple keyword extraction
        text = f"{title} {' '.join(q.get('question', '') for q in questions)}"
        words = text.lower().split()
        
        common_topics = ["python", "javascript", "database", "api", "frontend", "backend"]
        for topic in common_topics:
            if topic in text.lower():
                tags.append(topic)
                
        return tags[:5]  # Limit to 5 tags
    
    def estimate_question_difficulty(self, question: Dict[str, Any]) -> int:
        """Estimate question difficulty on 1-10 scale"""
        base_difficulty = 3
        
        # Adjust based on question length
        question_length = len(question.get("question", "").split())
        if question_length > 20:
            base_difficulty += 2
        elif question_length < 5:
            base_difficulty -= 1
            
        # Adjust based on number of options
        option_count = len(question.get("options", []))
        if option_count > 4:
            base_difficulty += 1
            
        return min(10, max(1, base_difficulty))
    
    def calculate_cognitive_load(self, question: Dict[str, Any]) -> str:
        """Estimate cognitive load required"""
        difficulty = self.estimate_question_difficulty(question)
        if difficulty <= 3:
            return "low"
        elif difficulty <= 7:
            return "medium"
        else:
            return "high"
    
    def generate_hint(self, question: Dict[str, Any]) -> str:
        """Generate a helpful hint for the question"""
        question_text = question.get("question", "").lower()
        
        if "what" in question_text:
            return "Focus on the definition or core concept"
        elif "how" in question_text:
            return "Think about the process or steps involved"
        elif "why" in question_text:
            return "Consider the underlying reasons or principles"
        else:
            return "Read the question carefully and eliminate obviously wrong answers"
