from transformers import pipeline
from pydub import AudioSegment
from pydub.utils import make_chunks
from services.lamma_service import LammaService

format={
  "type": "object",
  "properties":{
    "questions": {
      "type": "array",
          "items": {
            "type": "string"
          },
      "description": "list of questions(string) ask by interviewer"
    },
  },
  "required": ["questions"]
}

class AudioService:
    def __init__(self, audio_path):
        
        self.audio_path = audio_path
        self.asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base",)

    def process_audio(self):
        lamma_service = LammaService()
        # Load audio file using pydub
        audio = AudioSegment.from_file(self.audio_path)

        # Split audio into 2-minute chunks
        chunk_length_ms = 120 * 1000  # 2 minute
        chunks = make_chunks(audio, chunk_length_ms)

        questions = []

        # Process each chunk sequentially
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}...")

            # Export chunk to WAV format
            chunk_path = f"chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")

            # Transcribe the chunk
            transcription = self.asr_pipeline(inputs=chunk_path,return_timestamps=True)
            transcribed_text = transcription["text"]
            

            # Send transcription to Llama service
           
            sys_msg = "You are an advanced AI designed to analyze text."
            user_msg = f"""
            Extract and list all the questions asked by the interviewer during the job interview from the provided transcript. Ensure that only questions directly posed by the interviewer are included. If a question is logical or context-based, combine similar questions into one. 
            
            INPUT: {transcribed_text} \nRespond using JSON 
            """
            try:
                response = lamma_service.send_message_to_llama_chat(sys_msg=sys_msg, user_msg=user_msg,format=format)
                questions.extend(response["questions"])  # Add the returned questions to the list
            except Exception as e:
                print(f"Error processing chunk {i + 1}: {e}")

        return self.sentazing_questions(questions)
    
    def sentazing_questions(self,questions):
        print(questions)
        # Filter out questions that are empty or have less than 3 words
        filtered_questions = [question for question in questions if len(question.split()) >= 3]
        return filtered_questions
    
    def refine_questions(self,questions):
        
        lamma_service = LammaService()
        sys_msg = "You are an advanced AI designed to analyze text."
        user_msg=f""" find the list of questions asked by interviewer and return resposne in following JSON format
         {{questions:"A list of string of question"}}
         INPUT:{questions}
         """
        return lamma_service.send_message_to_llama_chat(sys_msg=sys_msg, user_msg=user_msg)
                
                
                