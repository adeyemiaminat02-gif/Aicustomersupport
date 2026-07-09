import os
import json
from openai import AsyncOpenAI
from utils.config import Config
from utils.logger import logger

class AIService:
    def __init__(self):
        # Configure the OpenAI client wrapper to point to Google Gemini's API gateway
        # This routes all standard AsyncOpenAI calls directly to Gemini's models
        self.client = AsyncOpenAI(
            api_key=Config.AI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Safe structural fallback to a stable Gemini model if not specified in Render
        self.model_name = getattr(Config, "MODEL_NAME", "gemini-2.5-flash")
        
        # Core data file definitions
        self.kb_path = os.path.join("data", "knowledge_base.json")
        self.system_instruction = (
            "You are an elite, empathetic AI Customer Support Specialist. "
            "Your objective is to provide precise, professional, and clear assistance based on "
            "the provided knowledge base data. If you are uncertain or the information is not present, "
            "gracefully offer to escalate the issue to human customer support."
        )

    def _load_knowledge_base(self) -> str:
        """Read contextual local data safely to pass to Gemini's attention window."""
        if not os.path.exists(self.kb_path):
            logger.warning(f"Knowledge base document missing at path: {self.kb_path}. Empty baseline fallback utilized.")
            return "No company FAQ or knowledge base data provided."
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
                return json.dumps(kb_data, indent=2)
        except Exception as e:
            logger.error(f"Error parse processing knowledge base array matrix data: {e}")
            return "Error reading technical data layers."

    async def generate_response(self, user_message: str, chat_history: list = None) -> str:
        """Dispatches an async generation payload to Gemini's endpoint using standard OpenAI schema mappings."""
        if not Config.AI_API_KEY:
            logger.error("AI Generation executed but AI_API_KEY environment string is absent.")
            return "⚠️ Connection error: AI system configuration key is missing on the server host."

        try:
            kb_context = self._load_knowledge_base()
            
            # Formulate structural system messaging stack
            messages = [
                {
                    "role": "system", 
                    "content": f"{self.system_instruction}\n\n[CONTEXT KNOWLEDGE BASE DATA]:\n{kb_context}"
                }
            ]

            # Rehydrate context streams via chat historical backlogs safely if provided
            if chat_history:
                for msg in chat_history[-6:]:  # Limit history to recent exchanges to prevent token bloating
                    role = "assistant" if msg.get("is_bot") else "user"
                    messages.append({"role": role, "content": msg.get("message", "")})

            # Append the current active user statement
            messages.append({"role": "user", "content": user_message})

            logger.info(f"Dispatching query interface payload directly to Gemini Engine via Model: {self.model_name}")
            
            # Execute standard AsyncOpenAI structural syntax request mapped smoothly to Gemini servers
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3, # Keeps responses factual, grounded, and concise
                max_tokens=800
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Critical execution error during Gemini Engine response cycle generation: {e}", exc_info=True)
            return "⚠️ I apologize, but I encountered a momentary error processing your request. Please try again shortly or use /support to contact a human."

# Instantiate the centralized singleton instance resource for app orchestration
ai_service = AIService()
