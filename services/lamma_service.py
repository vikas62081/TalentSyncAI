import json
import ollama


class LammaService:
    def send_message_to_llama(self,model_name:str, sys_msg:str, user_msg:str, retries=3):
        """Sends the message to the LLaMA model and handles retries."""
        for attempt in range(retries):
            try:
                response = ollama.chat(
                    model=model_name,
                    messages=[
                        {'role': 'system', 'content':sys_msg},
                        {'role': 'user', 'content': user_msg}
                    ],
                    format="json",
                )
                return json.loads(response['message']['content'])
            except json.JSONDecodeError:
                print("Error: Unable to parse the response into JSON.")
            except Exception as e:
                print(f"Error: {e}")
            print(f"Retrying... ({attempt + 1}/{retries})")
        return None
    
    def send_message_to_llamma_text(self,model_name:str,sys_msg:str,user_msg:str,retries=3):
        """Sends the message to the LLaMA model and handles retries."""
        for attempt in range(retries):
            try:
                response = ollama.chat(
                    model=model_name,
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