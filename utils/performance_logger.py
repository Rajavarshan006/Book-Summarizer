"""
Performance Logger Module
Comprehensive logging for tracking model performance and processing times
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

class PerformanceLogger:
    """
    Advanced performance logging system for tracking model performance metrics
    and processing times across the application.
    """

    def __init__(self, name: str = "performance", log_file: Optional[str] = None):
        """
        Initialize the performance logger.

        Args:
            name: Logger name
            log_file: Optional file path for performance log file
        """
        self.logger = logging.getLogger(f"{name}_logger")
        self.logger.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if log_file is provided
        self.log_file = log_file
        if log_file:
            # Create logs directory if it doesn't exist
            log_dir = Path(log_file).parent
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Performance metrics storage
        self.metrics = {
            'model_loading_times': [],
            'inference_times': [],
            'preprocessing_times': [],
            'total_processing_times': [],
            'memory_usage': [],
            'error_rates': []
        }

    def log_model_loading(self, model_name: str, loading_time: float, device: str):
        """
        Log model loading performance.

        Args:
            model_name: Name of the model
            loading_time: Time taken to load model in seconds
            device: Device used (CPU/GPU)
        """
        log_message = (
            f"Model '{model_name}' loaded on {device} in {loading_time:.4f} seconds"
        )
        self.logger.info(log_message)

        # Store metric
        self.metrics['model_loading_times'].append({
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'loading_time': loading_time,
            'device': device
        })

    def log_inference_performance(self, model_name: str, inference_time: float,
                                input_length: int, output_length: int,
                                chunk_id: Optional[str] = None):
        """
        Log model inference performance.

        Args:
            model_name: Name of the model
            inference_time: Time taken for inference in seconds
            input_length: Length of input text
            output_length: Length of output text
            chunk_id: Optional chunk identifier
        """
        throughput = input_length / inference_time if inference_time > 0 else 0
        chunk_info = f" (Chunk: {chunk_id})" if chunk_id else ""
        log_message = (
            f"Inference completed{chunk_info} - "
            f"Model: {model_name}, "
            f"Time: {inference_time:.4f}s, "
            f"Input: {input_length} chars, "
            f"Output: {output_length} chars, "
            f"Throughput: {throughput:.2f} chars/s"
        )
        self.logger.info(log_message)

        # Store metric
        self.metrics['inference_times'].append({
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'inference_time': inference_time,
            'input_length': input_length,
            'output_length': output_length,
            'chunk_id': chunk_id,
            'throughput': input_length / inference_time if inference_time > 0 else 0
        })
    def log_preprocessing_performance(self, text_length: int, processing_time: float,
                                    chunk_count: int, operation: str):
        """
        Log preprocessing performance.

        Args:
            text_length: Length of input text
            processing_time: Time taken for preprocessing
            chunk_count: Number of chunks generated
            operation: Type of preprocessing operation
        """
        throughput = text_length / processing_time if processing_time > 0 else 0
        log_message = (
            f"Preprocessing '{operation}' completed - "
            f"Text: {text_length} chars, "
            f"Time: {processing_time:.4f}s, "
            f"Chunks: {chunk_count}, "
            f"Throughput: {throughput:.2f} chars/s"
        )
        self.logger.info(log_message)

        # Store metric
        self.metrics['preprocessing_times'].append({
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'text_length': text_length,
            'processing_time': processing_time,
            'chunk_count': chunk_count,
            'throughput': text_length / processing_time if processing_time > 0 else 0
        })
    def log_total_processing(self, total_time: float, chunk_count: int,
                           success_count: int, error_count: int):
        """
        Log total processing performance.

        Args:
            total_time: Total processing time
            chunk_count: Number of chunks processed
            success_count: Number of successful chunks
            error_count: Number of failed chunks
        """
        error_rate = (error_count / chunk_count) * 100 if chunk_count > 0 else 0
        avg_time = total_time / chunk_count if chunk_count > 0 else 0
        log_message = (
            f"Total processing completed - "
            f"Time: {total_time:.4f}s, "
            f"Chunks: {chunk_count}, "
            f"Success: {success_count}, "
            f"Errors: {error_count} ({error_rate:.1f}%), "
            f"Avg time per chunk: {avg_time:.4f}s"
        )
        self.logger.info(log_message)

        # Store metrics
        self.metrics['total_processing_times'].append({
            'timestamp': datetime.now().isoformat(),
            'total_time': total_time,
            'chunk_count': chunk_count,
            'success_count': success_count,
            'error_count': error_count,
            'error_rate': error_rate
        })

        self.metrics['error_rates'].append({
            'timestamp': datetime.now().isoformat(),
            'error_rate': error_rate,
            'chunk_count': chunk_count
        })

    def log_memory_usage(self, memory_usage: Dict[str, float]):
        """
        Log memory usage statistics.

        Args:
            memory_usage: Dictionary containing memory usage metrics
        """
        log_message = (
            f"Memory usage - "
            f"Peak: {memory_usage.get('peak', 0):.2f} MB, "
            f"Current: {memory_usage.get('current', 0):.2f} MB, "
            f"Model: {memory_usage.get('model', 0):.2f} MB"
        )
        self.logger.info(log_message)

        # Store metric
        self.metrics['memory_usage'].append({
            'timestamp': datetime.now().isoformat(),
            **memory_usage
        })

    def log_error(self, error_type: str, error_message: str,
                 context: Optional[Dict[str, Any]] = None):
        """
        Log errors with context.

        Args:
            error_type: Type/category of error
            error_message: Error message
            context: Additional context information
        """
        context_str = f" | Context: {json.dumps(context)}" if context else ""
        log_message = f"ERROR [{error_type}]: {error_message}{context_str}"
        self.logger.error(log_message)

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of performance metrics.

        Returns:
            Dictionary containing performance summary
        """
        if not any(self.metrics.values()):
            return {"message": "No performance data available"}

        # Calculate averages
        avg_inference_time = sum(
            item['inference_time'] for item in self.metrics['inference_times']
        ) / len(self.metrics['inference_times']) if self.metrics['inference_times'] else 0

        avg_preprocessing_time = sum(
            item['processing_time'] for item in self.metrics['preprocessing_times']
        ) / len(self.metrics['preprocessing_times']) if self.metrics['preprocessing_times'] else 0

        avg_model_loading_time = sum(
            item['loading_time'] for item in self.metrics['model_loading_times']
        ) / len(self.metrics['model_loading_times']) if self.metrics['model_loading_times'] else 0

        avg_error_rate = sum(
            item['error_rate'] for item in self.metrics['error_rates']
        ) / len(self.metrics['error_rates']) if self.metrics['error_rates'] else 0

        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'inference': {
                    'count': len(self.metrics['inference_times']),
                    'average_time': avg_inference_time,
                    'total_count': len(self.metrics['inference_times'])
                },
                'preprocessing': {
                    'count': len(self.metrics['preprocessing_times']),
                    'average_time': avg_preprocessing_time,
                    'total_count': len(self.metrics['preprocessing_times'])
                },
                'model_loading': {
                    'count': len(self.metrics['model_loading_times']),
                    'average_time': avg_model_loading_time,
                    'total_count': len(self.metrics['model_loading_times'])
                },
                'error_rate': avg_error_rate,
                'total_processing_operations': len(self.metrics['total_processing_times']),
                'memory_usage_records': len(self.metrics['memory_usage'])
            }
        }

    def save_metrics_to_file(self, file_path: Optional[str] = None):
        """
        Save performance metrics to a JSON file.

        Args:
            file_path: Optional custom file path
        """
        if not file_path:
            file_path = self.log_file.replace('.log', '_metrics.json') if self.log_file else 'performance_metrics.json'

        try:
            with open(file_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            self.logger.info(f"Performance metrics saved to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save performance metrics: {str(e)}")
            return False

    def start_timer(self) -> float:
        """
        Start a timer and return the start time.

        Returns:
            Current timestamp in seconds
        """
        return time.time()

    def end_timer(self, start_time: float) -> float:
        """
        End a timer and return the elapsed time.

        Args:
            start_time: Start time from start_timer()

        Returns:
            Elapsed time in seconds
        """
        return time.time() - start_time

# Global performance logger instance
performance_logger = PerformanceLogger(
    name="model_performance",
    log_file="logs/performance.log"
)

def get_performance_logger() -> PerformanceLogger:
    """
    Get the global performance logger instance.

    Returns:
        PerformanceLogger instance
    """
    return performance_logger
