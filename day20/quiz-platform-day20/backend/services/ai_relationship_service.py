import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import asyncio
from ..config.settings import settings
from ..models.schemas import Topic

class AIRelationshipService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def discover_relationships(self, topics: List[Topic]) -> List[Dict[str, Any]]:
        """Use Gemini AI to discover relationships between topics"""
        if len(topics) < 2:
            return []
        
        topic_data = []
        for topic in topics:
            topic_data.append({
                "id": topic.id,
                "name": topic.name,
                "description": topic.description or "",
                "category": topic.category or "",
                "difficulty_level": topic.difficulty_level,
                "keywords": topic.content_keywords or ""
            })
        
        prompt = self._build_relationship_prompt(topic_data)
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            relationships = self._parse_ai_response(response.text)
            return relationships
        except Exception as e:
            print(f"AI relationship discovery error: {e}")
            return []
    
    def _build_relationship_prompt(self, topics: List[Dict]) -> str:
        topics_text = "\n".join([
            f"- ID: {t['id']}, Name: {t['name']}, Description: {t['description']}, "
            f"Category: {t['category']}, Difficulty: {t['difficulty_level']}, Keywords: {t['keywords']}"
            for t in topics
        ])
        
        return f"""
        Analyze the following educational topics and identify relationships between them.
        
        Topics:
        {topics_text}
        
        Identify relationships using these types:
        - prerequisite: Topic A must be learned before Topic B
        - corequisite: Topics should be learned together
        - similar: Topics share common concepts  
        - builds_on: Topic B extends Topic A concepts
        - applies_to: Topic A is used in Topic B applications
        
        For each relationship, provide:
        1. Source topic ID
        2. Target topic ID  
        3. Relationship type
        4. Confidence score (0.0 to 1.0)
        5. Brief evidence/reasoning
        
        Return ONLY a valid JSON array with this structure:
        [
          {{
            "source_id": 1,
            "target_id": 2,
            "type": "prerequisite",
            "confidence": 0.85,
            "evidence": "Linear algebra concepts are fundamental for understanding neural networks"
          }}
        ]
        
        Focus on educationally meaningful relationships. Be conservative with confidence scores.
        """
    
    def _parse_ai_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured relationship data"""
        try:
            # Clean the response to extract JSON
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            relationships = json.loads(cleaned)
            
            # Validate and standardize
            validated = []
            for rel in relationships:
                if all(k in rel for k in ["source_id", "target_id", "type", "confidence"]):
                    validated.append({
                        "source_topic_id": rel["source_id"],
                        "target_topic_id": rel["target_id"],
                        "relationship_type": rel["type"],
                        "strength": min(max(rel["confidence"], 0.0), 1.0),
                        "source_evidence": rel.get("evidence", "AI generated relationship"),
                        "ai_generated": True
                    })
            
            return validated
        except json.JSONDecodeError:
            print(f"Failed to parse AI response: {response_text}")
            return []
    
    async def suggest_related_topics(self, topic: Topic, all_topics: List[Topic], 
                                   max_suggestions: int = 10) -> List[Dict[str, Any]]:
        """Suggest related topics for a given topic"""
        if not all_topics:
            return []
        
        # Filter out the source topic
        candidate_topics = [t for t in all_topics if t.id != topic.id]
        
        if not candidate_topics:
            return []
        
        # Limit candidates for performance
        if len(candidate_topics) > 20:
            candidate_topics = candidate_topics[:20]
        
        topics_to_analyze = [topic] + candidate_topics
        relationships = await self.discover_relationships(topics_to_analyze)
        
        # Filter relationships where our topic is the source
        suggestions = [
            rel for rel in relationships 
            if rel["source_topic_id"] == topic.id or rel["target_topic_id"] == topic.id
        ]
        
        # Sort by confidence and limit
        suggestions.sort(key=lambda x: x["strength"], reverse=True)
        return suggestions[:max_suggestions]
