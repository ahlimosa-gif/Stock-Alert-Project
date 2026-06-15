from openai import OpenAI
from config import OPENAI_API_KEY


class AIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def generate_trading_suggestion(self, symbol: str, price: float, rsi: float, ma: float) -> str:
        if not self.client:
            return "AI 建議：暫未設定 OpenAI key。"
        prompt = "Stock: " + symbol + "\nPrice: " + str(round(price, 2)) + "\nRSI: " + str(round(rsi, 2)) + "\nMA: " + str(round(ma, 2)) + "\nWrite a short Cantonese trading suggestion."
        try:
            r = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional stock trading assistant. Reply in Cantonese."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                max_tokens=220,
            )
            return r.choices[0].message.content or "AI 建議暫時未能生成。"
        except Exception as e:
            return "AI 建議暫時未能生成：" + str(e)
