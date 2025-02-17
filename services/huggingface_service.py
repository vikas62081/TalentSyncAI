from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

# Load the configuration and model
config = AutoConfig.from_pretrained("deepseek-ai/deepseek-llm-7b-base", trust_remote_code=True)
config.quantization_type = None  # Remove quantization if not needed

model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/deepseek-llm-7b-base",
    config=config,
    trust_remote_code=True
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-llm-7b-base", trust_remote_code=True)

# Define the prompt
prompt = "Describe the future impact of AI language models like DeepSeek-LLM on personalized education and real-time collaboration across global teams."

# Tokenize the input prompt
inputs = tokenizer(prompt, return_tensors="pt")

# Generate response
outputs = model.generate(
    inputs["input_ids"],
    max_length=300,  # Adjust the max length of the response as needed
    num_return_sequences=1,
    temperature=0.7,  # Adjust the temperature for creativity (lower = more deterministic)
)

# Decode and print the output
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)