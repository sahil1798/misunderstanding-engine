"""
OpenRouter API Integration
Universal gateway to multiple AI models (GPT-4, Claude, Gemini, etc.)
"""

import os
import json
from openai import OpenAI
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class OpenRouterAnalyzer:
    """OpenRouter API client for emotional intelligence analysis"""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.app_name = os.getenv('APP_NAME', 'Misunderstanding-Engine')
        self.app_url = os.getenv('APP_URL', 'http://localhost:5000')

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file")

        # Initialize OpenAI client with OpenRouter endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": self.app_url,
                "X-Title": self.app_name,
            }
        )

        # Model selection - Choose based on your needs
        # Free models (good for hackathon):
        self.model = "anthropic/claude-haiku-4.5"


        # Paid models (better quality, still cheap):
        # self.model = "anthropic/claude-3-haiku"  # Best balance
        # self.model = "openai/gpt-4o-mini"  # OpenAI's cheapest
        # self.model = "google/gemini-flash-1.5"  # Very fast

        print(f"🤖 OpenRouter initialized with model: {self.model}")

    def analyze_emotion(self, text: str) -> Dict:
        """
        Analyze emotional tone and intent

        Args:
            text: Input text to analyze

        Returns:
            Dict with emotion analysis results
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an emotional intelligence expert. 
Analyze text for emotions and tone.

Return ONLY valid JSON (no markdown, no explanations):
{
    "primary_emotion": "joy|anger|sadness|fear|surprise|disgust|neutral|passive-aggressive",
    "intensity": 7.5,
    "hidden_feelings": "what's unsaid or implied",
    "tone_markers": ["sarcasm", "sincerity", "etc"],
    "empathy_level": 4.0,
    "emotions_detected": ["emotion1", "emotion2"]
}"""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this message: '{text}'"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            # Parse response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            return result

        except Exception as e:
            print(f"OpenRouter API Error (emotion): {e}")
            # Fallback
            return {
                "primary_emotion": "neutral",
                "intensity": 5.0,
                "hidden_feelings": "Unable to analyze",
                "tone_markers": ["unclear"],
                "empathy_level": 5.0,
                "emotions_detected": ["neutral"]
            }

    def generate_misunderstandings(self, text: str, emotion_data: Dict, count: int = 5) -> List[Dict]:
        """
        Generate plausible misinterpretations

        Args:
            text: Original message
            emotion_data: Emotion analysis results
            count: Number of misunderstandings to generate

        Returns:
            List of misunderstanding scenarios
        """
        try:
            prompt = f"""Original message: "{text}"
Emotion detected: {emotion_data.get('primary_emotion', 'neutral')}
Intensity: {emotion_data.get('intensity', 5.0)}

Generate {count} realistic misunderstandings. For each, explain:
1. How someone might misinterpret it
2. Their emotional reaction
3. Why this happens psychologically
4. Likelihood score (1-10)

Return ONLY valid JSON (no markdown):
{{
    "misunderstandings": [
        {{
            "misunderstood_meaning": "clear description",
            "emotional_impact": "how they'd feel",
            "why_it_happens": "psychological reason",
            "likelihood": 8
        }}
    ]
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a communication psychology expert. Generate realistic misunderstanding scenarios. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Clean markdown
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            return result.get('misunderstandings', [])[:count]

        except Exception as e:
            print(f"OpenRouter API Error (misunderstandings): {e}")
            return [
                {
                    "misunderstood_meaning": f"Could be interpreted differently than intended",
                    "emotional_impact": "May cause confusion or hurt feelings",
                    "why_it_happens": "Lack of context or tone clarity",
                    "likelihood": 6
                }
            ]

    def suggest_improvement(self, text: str, emotion_data: Dict) -> str:
        """
        Suggest improved, clearer version of the message

        Args:
            text: Original message
            emotion_data: Emotion analysis results

        Returns:
            Improved message string
        """
        try:
            emotion = emotion_data.get('primary_emotion', 'neutral')

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Rephrase messages to be clearer and prevent misunderstanding.

Rules:
- Keep the {emotion} emotion but make it explicit
- Be direct yet kind
- Add empathy markers
- Maximum 2-3 sentences
- Return ONLY the improved message, nothing else"""
                    },
                    {
                        "role": "user",
                        "content": f"Improve clarity: '{text}'"
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )

            improved = response.choices[0].message.content.strip()
            # Remove quotes if added
            improved = improved.strip('"').strip("'")
            return improved

        except Exception as e:
            print(f"OpenRouter API Error (improvement): {e}")
            return f"Try being more direct: {text}"

    def calculate_ambiguity_score(self, text: str) -> float:
        """
        Calculate how ambiguous/unclear the text is (1-10 scale)

        Args:
            text: Input text

        Returns:
            Ambiguity score (float)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Rate text clarity on 1-10 scale (10 = very ambiguous).

Return ONLY valid JSON:
{"ambiguity_score": 7.5, "reason": "brief explanation"}"""
                    },
                    {
                        "role": "user",
                        "content": f"Rate ambiguity: '{text}'"
                    }
                ],
                temperature=0.3,
                max_tokens=150
            )

            content = response.choices[0].message.content.strip()

            # Clean markdown
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
            return float(result.get('ambiguity_score', 5.0))

        except Exception as e:
            print(f"OpenRouter API Error (ambiguity): {e}")
            return 5.0

    def test_connection(self) -> bool:
        """Test if OpenRouter API is working"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Say 'OK' if you're working."}
                ],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"OpenRouter Connection Error: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("Testing OpenRouter Integration...")

    try:
        analyzer = OpenRouterAnalyzer()

        # Test connection
        if analyzer.test_connection():
            print("✅ OpenRouter API connected!")

            # Test analysis
            test_text = "I'm fine with whatever you decide."
            print(f"\n📝 Analyzing: '{test_text}'")

            emotion = analyzer.analyze_emotion(test_text)
            print(f"✅ Emotion: {emotion.get('primary_emotion')} (intensity: {emotion.get('intensity')})")

            misunderstandings = analyzer.generate_misunderstandings(test_text, emotion, count=3)
            print(f"✅ Generated {len(misunderstandings)} misunderstandings")

            improved = analyzer.suggest_improvement(test_text, emotion)
            print(f"✅ Improved: {improved}")

            score = analyzer.calculate_ambiguity_score(test_text)
            print(f"✅ Ambiguity score: {score}")

        else:
            print("❌ Connection failed")

    except Exception as e:
        print(f"❌ Error: {e}")