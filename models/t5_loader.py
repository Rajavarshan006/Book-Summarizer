from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

MODEL_NAME = "t5-small"

def load_t5_model():
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    return tokenizer, model, device
