import sys
from pathlib import Path
import time

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from models.t5_loader import load_t5_model
from utils.performance_logger import get_performance_logger

tokenizer, model, device = load_t5_model()
performance_logger = get_performance_logger()

def summarize_text(text: str, max_length=150, min_length=40) -> str:
    # Ensure text is string and clean input
    text_str = str(text).strip() if text else ""
    input_text = "summarize: " + text_str

    # Start performance tracking
    start_time = time.time()
    input_length = len(text_str)

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(device)

    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        num_beams=4,
        early_stopping=True
    )

    summary = tokenizer.decode(summary_ids[0],
                            skip_special_tokens=True)

    # End performance tracking
    inference_time = time.time() - start_time
    output_length = len(summary)

    # Log performance metrics
    performance_logger.log_inference_performance(
        model_name="t5-small",
        inference_time=inference_time,
        input_length=input_length,
        output_length=output_length
    )

    return summary

if __name__ == "__main__":
    # Test different input types
    test_inputs = [
        "This is a sample text to summarize. It contains multiple sentences.",
        "",
        12345,
        {"key": "value"},
        None
    ]
    
    print("\n=== Summarization Test Results ===")
    for i, text in enumerate(test_inputs):
        try:
            summary = summarize_text(text)
            print(f"Test {i+1} ({type(text)}): {'SUCCESS' if summary else 'EMPTY'}")
            print(f"Summary: {summary}\n")
        except Exception as e:
            print(f"Test {i+1} ({type(text)}): FAILED - {str(e)}")
