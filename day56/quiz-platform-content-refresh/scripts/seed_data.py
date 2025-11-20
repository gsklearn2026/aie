import asyncio
import httpx
import random
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

SAMPLE_CONTENT = [
    {
        "topic": "Python Basics",
        "question": "What is the correct way to create a variable in Python?",
        "options": ["var x = 5", "x := 5", "x = 5", "int x = 5"],
        "correct_answer": "x = 5",
        "explanation": "Python uses dynamic typing, so variables are created by simple assignment.",
        "difficulty": "easy",
        "category": "Programming"
    },
    {
        "topic": "Data Structures",
        "question": "Which data structure uses LIFO (Last In First Out) principle?",
        "options": ["Queue", "Stack", "Array", "Linked List"],
        "correct_answer": "Stack",
        "explanation": "Stacks follow LIFO - the last element added is the first one removed.",
        "difficulty": "medium",
        "category": "Computer Science"
    },
    {
        "topic": "Machine Learning",
        "question": "What type of learning uses labeled training data?",
        "options": ["Unsupervised", "Reinforcement", "Supervised", "Transfer"],
        "correct_answer": "Supervised",
        "explanation": "Supervised learning trains on labeled data to predict outputs.",
        "difficulty": "medium",
        "category": "AI"
    },
    {
        "topic": "Databases",
        "question": "What does SQL stand for?",
        "options": ["Strong Query Language", "Structured Query Language", "Simple Question Language", "Standard Query Logic"],
        "correct_answer": "Structured Query Language",
        "explanation": "SQL is the standard language for managing relational databases.",
        "difficulty": "easy",
        "category": "Databases"
    },
    {
        "topic": "Networking",
        "question": "Which protocol is used for secure web communication?",
        "options": ["HTTP", "FTP", "HTTPS", "SMTP"],
        "correct_answer": "HTTPS",
        "explanation": "HTTPS adds encryption to HTTP using TLS/SSL.",
        "difficulty": "easy",
        "category": "Networking"
    },
    {
        "topic": "Algorithms",
        "question": "What is the time complexity of binary search?",
        "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"],
        "correct_answer": "O(log n)",
        "explanation": "Binary search halves the search space with each comparison.",
        "difficulty": "medium",
        "category": "Algorithms"
    },
    {
        "topic": "Web Development",
        "question": "Which HTML tag is used for the largest heading?",
        "options": ["<h6>", "<heading>", "<h1>", "<head>"],
        "correct_answer": "<h1>",
        "explanation": "h1 is the largest heading, h6 is the smallest.",
        "difficulty": "easy",
        "category": "Web"
    },
    {
        "topic": "Cloud Computing",
        "question": "What does IaaS stand for?",
        "options": ["Internet as a Service", "Infrastructure as a Service", "Integration as a Service", "Information as a Service"],
        "correct_answer": "Infrastructure as a Service",
        "explanation": "IaaS provides virtualized computing resources over the internet.",
        "difficulty": "medium",
        "category": "Cloud"
    }
]

async def seed_content():
    async with httpx.AsyncClient() as client:
        print("Seeding content...")
        
        for item in SAMPLE_CONTENT:
            try:
                response = await client.post(f"{API_URL}/api/content/", json=item)
                if response.status_code == 200:
                    content = response.json()
                    print(f"Created: {item['topic']} - {content['id']}")
                    
                    # Simulate some usage
                    for _ in range(random.randint(5, 20)):
                        correct = random.random() > 0.3
                        time_taken = random.uniform(20, 180)
                        await client.post(
                            f"{API_URL}/api/content/{content['id']}/attempt",
                            params={
                                "correct": correct,
                                "time_seconds": time_taken,
                                "skipped": random.random() > 0.9
                            }
                        )
                else:
                    print(f"Failed to create: {item['topic']} - {response.text}")
            except Exception as e:
                print(f"Error: {e}")
        
        # Trigger freshness scan
        print("\nTriggering freshness scan...")
        await client.post(f"{API_URL}/api/jobs/scan-freshness")
        
        print("\nSeeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_content())
