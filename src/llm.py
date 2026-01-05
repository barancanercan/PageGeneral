"""
PAGEGENERAL - LLM Client
Ollama (qwen2.5:7b) ile iletişim
"""

import requests
import config


class OllamaClient:
    """Ollama LLM ile bağlantı"""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.LLM_MODEL
        self.endpoint = f"{self.base_url}/api/generate"

    def is_available(self) -> bool:
        """Ollama sunucusu açık mı kontrol et"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, temperature: float = None,
                 max_tokens: int = None) -> str:
        """
        Ollama'dan yanıt al

        Args:
            prompt: İstek
            temperature: Yaratıcılık (0.0-1.0)
            max_tokens: Maksimum yanıt uzunluğu

        Returns:
            Model yanıtı (string)
        """
        if temperature is None:
            temperature = config.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = config.LLM_MAX_TOKENS

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }

        try:
            if config.VERBOSE:
                print(f"🤖 LLM'ye soruluyor ({self.model})...")

            response = requests.post(self.endpoint, json=payload, timeout=300)
            response.raise_for_status()

            result = response.json()
            return result.get('response', '').strip()

        except requests.exceptions.ConnectionError:
            print("❌ HATA: Ollama sunucusu çalışmıyor!")
            print("   Lütfen şunu çalıştırın: ollama serve")
            return ""

        except requests.exceptions.Timeout:
            print("⏱️  HATA: Ollama timeout (çok yavaş)")
            return ""

        except Exception as e:
            print(f"❌ LLM Hatası: {e}")
            return ""


def test_connection():
    """Ollama bağlantısını test et"""
    client = OllamaClient()

    print("🔗 Ollama bağlantısı test ediliyor...")

    if client.is_available():
        print(f"✅ Ollama açık: {client.base_url}")
        print(f"📦 Model: {client.model}")

        # Basit test
        response = client.generate("Merhaba, ne yapıyorsun?")
        if response:
            print(f"💬 Yanıt: {response[:100]}...")
        else:
            print("❌ Model yanıt vermedi")
    else:
        print(f"❌ Ollama açık değil: {client.base_url}")
        print("   Çalıştır: ollama serve")


if __name__ == "__main__":
    test_connection()