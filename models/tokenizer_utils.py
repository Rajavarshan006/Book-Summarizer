from typing import Dict, List
import torch


def tokenize_input(
    tokenizer,
    text: str,
    max_length: int = 512
) -> Dict[str, torch.Tensor]:
    """
    Tokenize input text with truncation and padding.

    This function ensures:
    - Input never exceeds model max tokens
    - Padding is applied correctly
    - Output is ready for model inference

    Args:
        tokenizer: Hugging Face tokenizer
        text: Input text chunk
        max_length: Maximum token length supported by model

    Returns:
        Dictionary with input_ids and attention_mask tensors
    """

    return tokenizer(
        text,
        max_length=max_length,
        truncation=True,          # 🔒 prevents overflow
        padding="max_length",     # 🔒 ensures uniform tensor size
        return_tensors="pt"       # 🔒 PyTorch tensors
    )


def tokenize_batch(
    tokenizer,
    texts: List[str],
    max_length: int = 512
) -> Dict[str, torch.Tensor]:
    """
    Tokenize a batch of texts efficiently.

    Used when summarizing multiple chunks at once.

    Args:
        tokenizer: Hugging Face tokenizer
        texts: List of text chunks
        max_length: Maximum token length

    Returns:
        Tokenized batch tensors
    """

    return tokenizer(
        texts,
        max_length=max_length,
        truncation=True,
        padding=True,             # dynamic padding for batch
        return_tensors="pt"
    )
