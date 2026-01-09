import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import config

class HFClient:
    """Local Qwen2.5-7B (No API, Pure Local)"""
    
    def __init__(self):
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        print("📥 Model yükleniyor (ilk kez biraz yavaş)...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
    
    def generate(self, prompt: str, max_tokens: int = None) -> str:
        if max_tokens is None:
            max_tokens = config.LLM_MAX_TOKENS
        
        try:
            if config.VERBOSE:
                print(f"🤖 Local Qwen2.5 çağrılıyor...")
            
            messages = [{"role": "user", "content": prompt}]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=max_tokens,
                temperature=config.LLM_TEMPERATURE
            )
            
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response.strip()
        
        except Exception as e:
            print(f"❌ Hata: {e}")
            return ""

def test_connection():
    try:
        client = HFClient()
        print("✅ Model yüklendi")
        response = client.generate("Merhaba, kısaca kendini tanıt.", max_tokens=50)
        if response:
            print(f"✅ Yanıt:\n{response}")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_connection()
