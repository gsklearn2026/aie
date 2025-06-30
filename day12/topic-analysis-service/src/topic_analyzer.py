import asyncio
import time
import json
import hashlib
from typing import List, Dict, Any, Optional
import structlog
import anthropic
from anthropic import AsyncAnthropic

from models import TopicAnalysisResponse, TopicInfo, AnalysisOptions
from cache import CacheManager

logger = structlog.get_logger()

class TopicAnalyzer:
    """AI-powered topic analysis and categorization service"""
    
    def __init__(self, api_key: str, cache_manager: CacheManager):
        self.client = AsyncAnthropic(api_key=api_key)
        self.cache_manager = cache_manager
        
    async def analyze(self, content: str, options: AnalysisOptions) -> TopicAnalysisResponse:
        """Analyze content and extract topics"""
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(content, options)
        
        # Check cache first
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached topic analysis result")
            result = TopicAnalysisResponse(**cached_result)
            result.cache_hit = True
            return result
        
        # Perform AI analysis
        logger.info("Performing AI topic analysis", content_length=len(content))
        
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(content, options)
            
            # Call Claude API
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            analysis_data = self._parse_ai_response(response.content[0].text)
            
            # Create response object
            result = TopicAnalysisResponse(
                topics=analysis_data["topics"],
                summary=analysis_data["summary"],
                word_count=len(content.split()),
                processing_time=time.time() - start_time,
                cache_hit=False
            )
            
            # Cache the result
            await self.cache_manager.set(cache_key, result.dict(), ttl=3600)
            
            logger.info("Topic analysis completed", 
                       topics_count=len(result.topics),
                       processing_time=result.processing_time)
            
            return result
            
        except Exception as e:
            logger.error("AI topic analysis failed", error=str(e))
            raise Exception(f"Topic analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, content: str, options: AnalysisOptions) -> str:
        """Create prompt for AI analysis"""
        prompt = f"""
Analyze the following content and extract topics, subtopics, and related concepts. 
Provide structured output as JSON with the following format:

{{
    "topics": [
        {{
            "name": "Topic Name",
            "confidence": 0.95,
            "category": "Subject Area",
            "subtopics": ["subtopic1", "subtopic2"],
            "concepts": ["concept1", "concept2"],
            "keywords": ["keyword1", "keyword2"]
        }}
    ],
    "summary": "Brief summary of the content"
}}

Analysis Requirements:
- Extract maximum {options.max_topics} topics
- Include subtopics: {options.include_subtopics}
- Minimum confidence threshold: {options.confidence_threshold}
- Extract related concepts: {options.extract_concepts}
{"- Domain filter: " + options.domain_filter if options.domain_filter else ""}

Content to analyze:
{content}

Provide only the JSON response without additional text.
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Convert to TopicInfo objects
            topics = []
            for topic_data in data.get("topics", []):
                topic = TopicInfo(
                    name=topic_data.get("name", "Unknown"),
                    confidence=float(topic_data.get("confidence", 0.5)),
                    category=topic_data.get("category", "General"),
                    subtopics=topic_data.get("subtopics", []),
                    concepts=topic_data.get("concepts", []),
                    keywords=topic_data.get("keywords", [])
                )
                topics.append(topic)
            
            return {
                "topics": topics,
                "summary": data.get("summary", "No summary available")
            }
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response", error=str(e), response=response_text)
            # Fallback response
            return {
                "topics": [
                    TopicInfo(
                        name="Parse Error",
                        confidence=0.1,
                        category="Error",
                        subtopics=[],
                        concepts=[],
                        keywords=[]
                    )
                ],
                "summary": "Failed to parse AI response"
            }
    
    def _generate_cache_key(self, content: str, options: AnalysisOptions) -> str:
        """Generate cache key for content and options"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        options_hash = hashlib.md5(options.json().encode()).hexdigest()
        return f"topic_analysis:{content_hash}:{options_hash}"
