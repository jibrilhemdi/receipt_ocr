# app/llm_service.py

from typing import Dict, Any
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Hugging Face model ID for Qwen3.5-0.8B
MODEL_NAME = "Qwen/Qwen3.5-0.8B"

# Choose device: use MPS on Apple Silicon if available, otherwise CPU
if torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"[Qwen] Using device: {device}")

# Load tokenizer & model once at import time (FastAPI process startup)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# torch_dtype="auto" lets transformers pick BF16/FP16/FP32 appropriately
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map=None  # we move to device manually
).to(device)


SYSTEM_PROMPT = """You are an assistant that extracts structured data from shopping receipts.
You must output STRICTLY valid JSON with no additional text.

JSON schema:
{
  "merchant": string or null,
  "purchase_date": string or null, // ISO 8601 format if possible
  "total": number or null,
  "currency": string or null,
  "items": [
    {
      "name": string,
      "quantity": number,
      "unit_price": number or null,
      "line_total": number or null
    }
  ],
  "extra_data": object or null
}

Rules:
- If a field is unknown, use null.
- If an item price is missing, set unit_price and/or line_total to null.
- Do NOT include any explanation or commentary. Output JSON only.
"""

USER_TEMPLATE = """Here is the OCR text of a shopping receipt:

---
{ocr_text}
---

Extract information according to the schema and output JSON only.
"""


def build_messages(ocr_text: str):
    user_content = USER_TEMPLATE.format(ocr_text=ocr_text)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    return messages


def parse_receipt_with_llm(ocr_text: str) -> Dict[str, Any]:
    """
    Call Qwen3.5-0.8B to parse OCR text of a receipt into structured JSON.
    """
    messages = build_messages(ocr_text)

    # Use Qwen's chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            temperature=0.2,
            do_sample=False,
        )

    # Only take newly generated tokens (after the input prompt)
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
    output_text = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    # Ideally the model outputs pure JSON. But we still guard:
    json_start = output_text.find("{")
    json_end = output_text.rfind("}")
    if json_start == -1 or json_end == -1:
        raise ValueError(f"Model did not return valid JSON: {output_text[:200]}")

    json_str = output_text[json_start:json_end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from model output: {e}\nRaw: {output_text}")

    return data