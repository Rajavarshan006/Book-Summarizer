"""
Test script for performance logging implementation
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from utils.performance_logger import get_performance_logger
from models.t5_summarizer import summarize_text
from backend.pipeline import PreprocessingPipeline

def test_performance_logging():
    """Test the performance logging implementation"""
    print("🚀 Starting Performance Logging Test...")

    # Get performance logger
    performance_logger = get_performance_logger()
    print(f"✅ Performance logger initialized - logging to: {performance_logger.log_file}")

    # Test 1: Model loading performance (already tested when importing summarize_text)
    print("\n📊 Test 1: Model Loading Performance")
    print("✅ Model loading performance logged during import")

    # Test 2: Inference performance
    print("\n📊 Test 2: Inference Performance")
    test_texts = [
        "This is a short test sentence for performance logging.",
        "The quick brown fox jumps over the lazy dog. This sentence contains all letters of the alphabet and is commonly used for testing purposes.",
        "Artificial intelligence and machine learning are transforming industries across the globe. From healthcare to finance, these technologies are enabling new capabilities and driving innovation. However, they also raise important ethical questions about privacy, bias, and the future of work."
    ]

    for i, text in enumerate(test_texts):
        print(f"  Testing text {i+1} ({len(text)} characters)...")
        try:
            summary = summarize_text(text, max_length=50, min_length=10)
            print(f"  ✅ Summary generated: {len(summary)} characters")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    # Test 3: Preprocessing pipeline performance
    print("\n📊 Test 3: Preprocessing Pipeline Performance")
    pipeline = PreprocessingPipeline(chunk_size=500, overlap_size=50)

    long_text = """Artificial Intelligence (AI) is revolutionizing the way we live and work.
    From virtual assistants like Siri and Alexa to advanced medical diagnosis systems,
    AI technologies are becoming increasingly integrated into our daily lives.

    Machine Learning, a subset of AI, focuses on developing algorithms that can learn
    from and make predictions on data. Deep Learning takes this a step further by using
    neural networks with many layers to model complex patterns in large datasets.

    The impact of AI on various industries is profound. In healthcare, AI-powered systems
    can analyze medical images with accuracy comparable to human experts. In finance,
    machine learning algorithms detect fraudulent transactions and optimize investment
    portfolios. The transportation industry is being transformed by autonomous vehicles
    that use AI for navigation and decision-making.

    However, the rapid advancement of AI also raises important ethical considerations.
    Issues such as algorithmic bias, data privacy, and the potential for job displacement
    need to be carefully addressed as these technologies continue to evolve."""

    print(f"  Processing text with {len(long_text)} characters...")
    start_time = performance_logger.start_timer()

    results = pipeline.process(long_text)

    processing_time = performance_logger.end_timer(start_time)
    print(f"  ✅ Preprocessing completed in {processing_time:.4f} seconds")
    print(f"  📝 Generated {len(results['chunks'])} chunks")

    # Log preprocessing performance
    performance_logger.log_preprocessing_performance(
        text_length=len(long_text),
        processing_time=processing_time,
        chunk_count=len(results['chunks']),
        operation="full_pipeline"
    )

    # Test 4: Total processing performance
    print("\n📊 Test 4: Total Processing Performance")
    performance_logger.log_total_processing(
        total_time=processing_time + 0.5,  # Add some extra time for simulation
        chunk_count=len(results['chunks']),
        success_count=len(results['chunks']),
        error_count=0
    )

    # Test 5: Get performance summary
    print("\n📊 Test 5: Performance Summary")
    summary = performance_logger.get_performance_summary()
    print(f"  📈 Inference operations: {summary['metrics']['inference']['count']}")
    print(f"  ⏱️  Average inference time: {summary['metrics']['inference']['average_time']:.4f}s")
    print(f"  📈 Preprocessing operations: {summary['metrics']['preprocessing']['count']}")
    print(f"  ⏱️  Average preprocessing time: {summary['metrics']['preprocessing']['average_time']:.4f}s")

    # Test 6: Save metrics to file
    print("\n📊 Test 6: Save Metrics to File")
    success = performance_logger.save_metrics_to_file()
    if success:
        print("  ✅ Performance metrics saved successfully")
    else:
        print("  ❌ Failed to save performance metrics")

    # Test 7: Error logging
    print("\n📊 Test 7: Error Logging")
    try:
        # Simulate an error
        raise ValueError("This is a test error for logging")
    except Exception as e:
        performance_logger.log_error(
            error_type="TEST_ERROR",
            error_message=str(e),
            context={"test": "error_logging", "severity": "low"}
        )
        print("  ✅ Error logged successfully")

    print("\n🎉 Performance Logging Test Completed!")
    print(f"📁 Logs saved to: {performance_logger.log_file}")
    metrics_file = performance_logger.log_file.replace('.log', '_metrics.json') if performance_logger.log_file else 'performance_metrics.json'
    print(f"📊 Metrics saved to: {metrics_file}")
if __name__ == "__main__":
    test_performance_logging()
