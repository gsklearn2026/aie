import google.generativeai as genai
from typing import Dict, Any, Optional, List
import time
import json
import logging
from datetime import datetime
from app.config.settings import settings
from app.services.model_router import router
from app.services.quality_validator import validator

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class GenerationService:
    """Orchestrates multi-model quiz generation"""
    
    def __init__(self):
        self.router = router
        self.validator = validator
        self.models = {}  # Cache model instances
        
    async def generate_question(
        self,
        question_type: str,
        subject: str,
        difficulty: str = "medium",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a question using multi-model routing"""
        
        start_time = time.time()
        
        # Route to appropriate profile
        profile_name = self.router.select_profile(
            question_type=question_type,
            difficulty=difficulty,
            subject=subject
        )
        
        logger.info(f"Routing {question_type} question to profile: {profile_name}")
        
        # Try primary profile
        result = await self._generate_with_profile(
            profile_name=profile_name,
            question_type=question_type,
            subject=subject,
            difficulty=difficulty,
            additional_context=additional_context
        )
        
        fallback_count = 0
        
        # If primary fails or quality is poor, try fallbacks
        if not result or result.get("quality_score", 0) < settings.QUALITY_THRESHOLD:
            logger.warning(f"Primary profile {profile_name} produced poor quality, trying fallbacks")
            
            fallback_chain = self.router.get_fallback_chain(profile_name)
            
            for fallback_profile in fallback_chain:
                fallback_count += 1
                logger.info(f"Attempting fallback: {fallback_profile}")
                
                result = await self._generate_with_profile(
                    profile_name=fallback_profile,
                    question_type=question_type,
                    subject=subject,
                    difficulty=difficulty,
                    additional_context=additional_context
                )
                
                if result and result.get("quality_score", 0) >= settings.QUALITY_THRESHOLD:
                    break
        
        if not result:
            raise Exception("All generation attempts failed")
        
        # Add metadata
        latency_ms = (time.time() - start_time) * 1000
        result["metadata"] = {
            "profile_used": profile_name if fallback_count == 0 else fallback_profile,
            "latency_ms": latency_ms,
            "fallback_count": fallback_count,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _generate_with_profile(
        self,
        profile_name: str,
        question_type: str,
        subject: str,
        difficulty: str,
        additional_context: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Generate question using specific profile"""
        
        profile_config = self.router.get_profile_config(profile_name)
        
        # Build prompt
        prompt = self._build_prompt(
            question_type=question_type,
            subject=subject,
            difficulty=difficulty,
            additional_context=additional_context,
            profile_config=profile_config
        )
        
        # Get or create model instance
        model = self._get_model(profile_config["model_name"])
        
        try:
            # Generate with retry logic
            for attempt in range(profile_config["max_retry"]):
                try:
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=profile_config["temperature"],
                            max_output_tokens=profile_config["max_tokens"]
                        )
                    )
                    
                    # Parse response
                    question_data = self._parse_response(response.text, question_type)
                    
                    # Validate quality
                    quality_score = self.validator.validate_question(question_data, question_type)
                    question_data["quality_score"] = quality_score
                    
                    if quality_score >= settings.QUALITY_THRESHOLD:
                        return question_data
                    
                    logger.warning(f"Quality score {quality_score} below threshold, retrying...")
                    
                except Exception as e:
                    logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                    if attempt == profile_config["max_retry"] - 1:
                        raise
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
            
            return None
            
        except Exception as e:
            logger.error(f"Profile {profile_name} generation failed: {e}")
            return None
    
    def _get_model(self, model_name: str):
        """Get or create Gemini model instance"""
        if model_name not in self.models:
            self.models[model_name] = genai.GenerativeModel(model_name)
        return self.models[model_name]
    
    def _build_prompt(
        self,
        question_type: str,
        subject: str,
        difficulty: str,
        additional_context: Optional[str],
        profile_config: Dict[str, Any]
    ) -> str:
        """Build generation prompt"""
        
        system_prompt = profile_config["system_prompt"]
        
        prompt = f"""{system_prompt}

Generate a {difficulty} difficulty {question_type} question about {subject}.

Requirements:
- Question must be clear and unambiguous
- Appropriate for {difficulty} difficulty level
- Subject: {subject}
- Question type: {question_type}
"""

        if question_type == "multiple_choice":
            prompt += """
Return as JSON:
{
    "question": "question text",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "A",
    "explanation": "why this is correct"
}
"""
        elif question_type == "true_false":
            prompt += """
Return as JSON:
{
    "question": "statement to evaluate",
    "correct_answer": "true" or "false",
    "explanation": "explanation"
}
"""
        elif question_type == "short_answer":
            prompt += """
Return as JSON:
{
    "question": "question text",
    "correct_answer": "expected answer",
    "explanation": "detailed explanation"
}
"""
        elif question_type == "essay":
            prompt += """
Return as JSON:
{
    "question": "essay prompt",
    "guidance": "key points to address",
    "rubric": "evaluation criteria"
}
"""
        elif question_type == "coding":
            prompt += """
Return as JSON:
{
    "question": "coding problem description",
    "requirements": ["req1", "req2"],
    "test_cases": [{"input": "...", "output": "..."}],
    "starter_code": "optional starter code"
}
"""

        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"
        
        return prompt
    
    def _parse_response(self, response_text: str, question_type: str) -> Dict[str, Any]:
        """Parse model response into structured format"""
        
        try:
            # Extract JSON from response
            response_text = response_text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            data = json.loads(response_text)
            data["question_type"] = question_type
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise ValueError(f"Invalid response format: {e}")

generation_service = GenerationService()
