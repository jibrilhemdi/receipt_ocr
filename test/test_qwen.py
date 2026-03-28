import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "Qwen/Qwen3.5-0.8B"

device = "cpu"  # start with CPU for testing
print("Using device:", device)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
).to(device)

messages = [
    {"role": "system", "content": "You output JSON only."},
    {"role": "user", "content": "Return {\"hello\": \"world\"} only."}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer([text], return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=64,
        temperature=0.2,
        do_sample=False,
    )

new_tokens = outputs[0][len(inputs.input_ids[0]):]
out_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
print("Model output:")
print(out_text)