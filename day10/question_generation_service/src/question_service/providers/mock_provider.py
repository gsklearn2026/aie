"""Mock AI provider for testing and development"""

import asyncio
import json
import random
from typing import Any, Dict

from .base_provider import AIProvider


class MockAIProvider(AIProvider):
    """Mock provider that generates sample questions"""

    SAMPLE_QUESTIONS = {
        "python": [
            "What is the difference between list and tuple in Python?",
            "Explain Python's GIL (Global Interpreter Lock)",
            "How do decorators work in Python?",
            "What are Python generators and when would you use them?",
            "Explain the difference between __str__ and __repr__ methods",
        ],
        "javascript": [
            "What is the difference between let, const, and var?",
            "Explain event bubbling and capturing in JavaScript",
            "What are closures and how do they work?",
            "Describe the difference between == and === operators",
            "How does the 'this' keyword work in JavaScript?",
        ],
        "general": [
            "What are the main principles of object-oriented programming?",
            "Explain the concept of algorithm complexity (Big O notation)",
            "What is the difference between stack and heap memory?",
            "Describe common software design patterns",
            "What are the principles of RESTful API design?",
        ],
    }

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate mock questions based on prompt"""
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 2.0))

        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Mock API timeout")

        # Extract topic from prompt
        topic = "general"
        prompt_lower = prompt.lower()

        for key in self.SAMPLE_QUESTIONS:
            if key in prompt_lower:
                topic = key
                break

        # Get random questions
        available_questions = self.SAMPLE_QUESTIONS[topic]
        selected_questions = random.sample(
            available_questions, min(5, len(available_questions))
        )

        # Format as JSON that Claude typically produces
        questions = [
            {
                "question": q,
                "type": random.choice(["multiple_choice", "short_answer", "essay"]),
                "explanation": f"This question tests understanding of {topic.lower()} concepts.",
            }
            for q in selected_questions
        ]

        return json.dumps(questions, indent=2)

    async def health_check(self) -> bool:
        """Mock health check"""
        return True
