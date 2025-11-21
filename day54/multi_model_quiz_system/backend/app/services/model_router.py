from typing import Dict, Any, Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class ModelRouter:
    """Routes quiz generation requests to appropriate model profiles"""
    
    def __init__(self):
        self.profiles = settings.MODEL_PROFILES
        self.routing_rules = settings.ROUTING_RULES
        
    def select_profile(
        self, 
        question_type: str, 
        difficulty: str = "medium",
        subject: Optional[str] = None,
        load_factor: float = 1.0
    ) -> str:
        """Select optimal model profile based on request parameters"""
        
        # Primary routing by question type
        profile_name = self.routing_rules.get(question_type, "general_fallback")
        
        # Adjust based on difficulty
        if difficulty == "hard" and profile_name in ["multiple_choice_expert", "short_answer_balanced"]:
            # Upgrade to more capable model for hard questions
            if self.profiles[profile_name]["cost_tier"] == "standard":
                logger.info(f"Upgrading profile for difficulty: {difficulty}")
        
        # Check if profile is available (could check system load, rate limits, etc.)
        if not self._is_profile_available(profile_name, load_factor):
            logger.warning(f"Profile {profile_name} unavailable, using fallback")
            return "general_fallback"
            
        return profile_name
    
    def _is_profile_available(self, profile_name: str, load_factor: float) -> bool:
        """Check if profile can handle additional load"""
        # Simple availability check - could be enhanced with circuit breaker pattern
        profile = self.profiles.get(profile_name)
        if not profile:
            return False
            
        # In production, check:
        # - Rate limit status
        # - Current queue depth
        # - Recent error rates
        # - Cost budget remaining
        
        return True
    
    def get_fallback_chain(self, primary_profile: str) -> list:
        """Get ordered list of fallback profiles"""
        profile = self.profiles.get(primary_profile)
        if not profile:
            return settings.FALLBACK_CHAIN
            
        # Build smart fallback chain based on cost tier
        cost_tier = profile["cost_tier"]
        
        fallbacks = []
        if cost_tier == "premium":
            fallbacks.append("general_fallback")
        elif cost_tier == "standard":
            fallbacks.append("general_fallback")
        else:  # economy
            fallbacks.append("general_fallback")
            
        return fallbacks
    
    def get_profile_config(self, profile_name: str) -> Dict[str, Any]:
        """Get complete configuration for a profile"""
        return self.profiles.get(profile_name, self.profiles["general_fallback"])

router = ModelRouter()
