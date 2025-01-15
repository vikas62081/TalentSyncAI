import json
import os
import ollama



class LammaService:
    def __init__(self):
        self.model_name=os.getenv("DEFAULT_MODEL","llama3.1:8b")
    def send_message_to_llama_generate(self, user_msg:str, retries=1):
        """Sends the message to the LLaMA model and handles retries."""
        if self.model_name is None:
            raise Exception("Modal name is not found.")
        for attempt in range(retries):
            try:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=user_msg,
                    format="json",
                )
                data=response["response"]
                return json.loads(data)
            except json.JSONDecodeError:
                print("Error: Unable to parse the response into JSON.")
            except Exception as e:
                print(f"Error: {e}")
            print(f"Retrying... ({attempt + 1}/{retries})")
        return None
    
    def send_message_to_llama_chat(self, sys_msg:str,user_msg:str,format="json" ,retries=1):
        """Sends the message to the LLaMA model and handles retries."""
        if self.model_name is None:
            raise Exception("Modal name is not found.")
        for attempt in range(retries):
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[{"role":"system","content":sys_msg},
                              {"role":"user","content":user_msg}],
                    format=format,
                )
                data=response['message']['content']
                return json.loads(data)
            except json.JSONDecodeError:
                print("Error: Unable to parse the response into JSON.")
            except Exception as e:
                print(f"Error: {e}")
            print(f"Retrying... ({attempt + 1}/{retries})")
        return None
    
    def send_message_to_llama_text(self,sys_msg:str,user_msg:str,retries=3):
        """Sends the message to the LLaMA model and handles retries."""
        for attempt in range(retries):
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {'role': 'system', 'content':sys_msg},
                        {'role': 'user', 'content': user_msg}
                    ],
                )
                return response['message']['content']
            except Exception as e:
                print(f"Error: {e}")
            print(f"Retrying... ({attempt + 1}/{retries})")
        return None