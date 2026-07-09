import json
import os
from openai import AsyncOpenAI
from utils.config import Config
from utils.logger import logger
from services.database import db_service

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.AI_API_KEY)
        self.kb_path = "data/knowledge_base.json"
        self._init_kb()

    def _init_kb(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.kb_path):
            default_kb = {
                "business_hours": "We are open Monday to Friday, 9:00 AM to 6:00 PM EST.",
                "pricing": "Our basic plan starts at $19/month. Premium plans are available at $49/month.",
                "refund_policy": "We offer a 14-day money-back guarantee if you are not fully satisfied.",
                "shipping_policy": "Standard shipping takes 3-5 business days. Digital delivery is instantaneous."
            }
            with open(self.kb_path, "w") as f:
                json.dump(default_kb, f, indent=4)

    def load_knowledge_base(self) -> str:
        try:
            with open(self.kb_path, "r") as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error reading knowledge base: {e}")
            return "{}"

    async def get_reply(self, user_id: int, user_message: str) -> str:
        settings = await db_service.get_user_settings(user_id)
        kb_context = self.load_knowledge_base()

        system_prompt = (
            f"You are @AICustomerSupportsBot, an elite, professional, and empathetic AI support agent.\n"
            f"Style constraint: Provide {settings['style']} answers.\n"
            f"Language constraint: Respond in language code '{settings['language']}'.\n\n"
            f"Prioritize this company knowledge base above general facts:\n{kb_context}\n\n"
            f"If you cannot find the answer in the context or if the user requires specific account access, "
            f"politely instruct them to escalate to human support using the 'Contact Support' option."
        )

        messages = [{"role": "system", "content": system_prompt}]

        if settings["history_enabled"]:
            history = await db_service.get_conversation_history(user_id)
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=messages,
                temperature=0.4 if settings["style"] == "Concise" else 0.7
            )
            ai_reply = response.choices[0].message.content
            
            if settings["history_enabled"]:
                await db_service.log_conversation(user_id, "user", user_message)
                await db_service.log_conversation(user_id, "assistant", ai_reply)

            return ai_reply
        except Exception as e:
            logger.error(f"AI Service Error: {e}")
            return "⚠️ I am currently having trouble updating my knowledge base processors. Please try again shortly or route to human support."

ai_service = AIService()
