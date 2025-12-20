from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import time
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from utils.performance_logger import get_performance_logger

MODEL_NAME = "t5-small"

def load_t5_model():
    performance_logger = get_performance_logger()
    start_time = time.time()

    performance_logger.logger.info(f"Starting to load model {MODEL_NAME}...")

    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    loading_time = time.time() - start_time
    performance_logger.log_model_loading(MODEL_NAME, loading_time, str(device))

    # Log memory usage
    if hasattr(torch, 'cuda'):
        if device.type == 'cuda':
            memory_usage = {
                'peak': torch.cuda.max_memory_allocated() / (1024 * 1024),
                'current': torch.cuda.memory_allocated() / (1024 * 1024),
                'model': sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)
            }
        else:
            memory_usage = {
                'peak': 0,
                'current': 0,
                'model': sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)
            }
    else:
        memory_usage = {
            'peak': 0,
            'current': 0,
            'model': sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)
        }

    performance_logger.log_memory_usage(memory_usage)

    return tokenizer, model, device
