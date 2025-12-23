from typing import List, Dict, Optional
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from utils.database import db
from backend.text_chunking import IntelligentTextChunker
import logging

class ChunkRepository:
    """
    Chunk management system that tracks which chunks belong to which book
    and maintains their order.

    Features:
    - Store and retrieve chunks with comprehensive metadata
    - Track chunk-book relationships
    - Maintain chunk order via sequence numbers
    - Support for intelligent token-based chunking
    - Comprehensive chunk statistics and validation
    """

    def __init__(self):
        """Initialize the chunk repository."""
        self.chunks_collection = db.chunks
        self.books_collection = db.books
        # Remove global default chunker to avoid configuration divergence
        self.logger = logging.getLogger(__name__)

    def _validate_object_id(self, id_str: str, id_name: str = "ID") -> ObjectId:
        """
        Validate and convert a string to ObjectId.

        Args:
            id_str: String ID to validate
            id_name: Name of the ID for error messages

        Returns:
            Valid ObjectId

        Raises:
            ValueError: If the ID is invalid
        """
        if not id_str:
            raise ValueError(f"{id_name} cannot be empty or None")

        if not ObjectId.is_valid(id_str):
            raise ValueError(f"Invalid {id_name}: {id_str}")

        try:
            return ObjectId(id_str)
        except InvalidId as e:
            raise ValueError(f"Invalid {id_name} format: {id_str}") from e

    def create_chunks_for_book(self, book_id: str, text: str,
                              model_name: str = "t5-small",
                              max_tokens: int = 512,
                              overlap_tokens: int = 100,
                              min_chunk_tokens: int = 50) -> List[Dict]:
        """
        Create and store chunks for a specific book.

        Args:
            book_id: ID of the book to create chunks for
            text: Text content to chunk
            model_name: Name of the model for token limit lookup
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            min_chunk_tokens: Minimum tokens for a valid chunk

        Returns:
            List of created chunk documents

        Raises:
            ValueError: If book_id is invalid
            Exception: If database operations fail
        """
        try:
            # Validate book_id first
            book_obj_id = self._validate_object_id(book_id, "book_id")

            # Configure chunker with specified parameters
            chunker = IntelligentTextChunker(
                model_name=model_name,
                max_tokens=max_tokens,
                overlap_tokens=overlap_tokens,
                min_chunk_tokens=min_chunk_tokens
            )

            # Generate chunks
            chunks = chunker.chunk_text(text)

            # Store chunking configuration in the book document
            if not self._store_chunking_config(
                book_id,
                model_name=model_name,
                max_tokens=max_tokens,
                overlap_tokens=overlap_tokens,
                min_chunk_tokens=min_chunk_tokens
            ):
                self.logger.error(f"Failed to store chunking configuration for book {book_id}")
                raise Exception(f"Failed to store chunking configuration for book {book_id}")

            # Store chunks in database
            created_chunks = []
            sequence_number = 0

            for chunk in chunks:
                chunk_doc = {
                    "book_id": book_obj_id,
                    "sequence_number": sequence_number,
                    "text": chunk["text"],
                    "sentence_count": chunk["sentence_count"],
                    "estimated_token_count": chunk["estimated_token_count"],
                    "word_count": chunk["word_count"],
                    "start_index": chunk["start_index"],
                    "end_index": chunk["end_index"],
                    "is_first_chunk": chunk["is_first_chunk"],
                    "is_last_chunk": chunk["is_last_chunk"],
                    "overlap_info": chunk["overlap_info"],
                    "sentences": chunk["sentences"],
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }

                try:
                    # Insert chunk into database
                    result = self.chunks_collection.insert_one(chunk_doc)
                    chunk_doc["_id"] = result.inserted_id
                    created_chunks.append(chunk_doc)
                except Exception as e:
                    self.logger.error(f"Failed to insert chunk for book {book_id} at sequence {sequence_number}: {e}")
                    # Clean up any chunks that were already inserted
                    if created_chunks:
                        self.logger.info(f"Cleaning up {len(created_chunks)} chunks that were already inserted")
                        self.delete_chunks_by_book(book_id)
                    # Clean up the stored chunking configuration
                    try:
                        self.logger.info(f"Cleaning up chunking configuration for book {book_id}")
                        self.books_collection.update_one(
                            {"_id": book_obj_id},
                            {"$unset": {"chunking_config": ""}}
                        )
                    except Exception as cleanup_e:
                        self.logger.error(f"Failed to clean up chunking configuration for book {book_id}: {cleanup_e}")
                    raise Exception(f"Database error while inserting chunk for book {book_id} at sequence {sequence_number}: {e}")

                sequence_number += 1

            return created_chunks

        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error creating chunks for book {book_id}: {e}")
            raise Exception(f"Error creating chunks for book {book_id}: {e}")

    def get_chunks_by_book(self, book_id: str, sort_by_sequence: bool = True) -> List[Dict]:
        """
        Retrieve all chunks for a specific book.

        Args:
            book_id: ID of the book to get chunks for
            sort_by_sequence: Whether to sort chunks by sequence number

        Returns:
            List of chunk documents for the specified book

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            query = {"book_id": book_obj_id}

            if sort_by_sequence:
                return list(self.chunks_collection.find(query).sort("sequence_number", 1))
            else:
                return list(self.chunks_collection.find(query))
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving chunks for book {book_id}: {e}")
            raise Exception(f"Error retrieving chunks for book {book_id}: {e}")

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunk_id: ID of the chunk to retrieve

        Returns:
            Chunk document or None if not found

        Raises:
            ValueError: If chunk_id is invalid
        """
        try:
            chunk_obj_id = self._validate_object_id(chunk_id, "chunk_id")
            return self.chunks_collection.find_one({"_id": chunk_obj_id})
        except ValueError as ve:
            self.logger.error(f"Invalid chunk_id format: {ve}")
            raise ValueError(f"Invalid chunk_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving chunk {chunk_id}: {e}")
            raise Exception(f"Error retrieving chunk {chunk_id}: {e}")

    def update_chunk(self, chunk_id: str, update_data: Dict) -> bool:
        """
        Update a specific chunk.

        Args:
            chunk_id: ID of the chunk to update
            update_data: Dictionary of fields to update

        Returns:
            True if update was successful, False otherwise

        Raises:
            ValueError: If chunk_id is invalid
        """
        try:
            chunk_obj_id = self._validate_object_id(chunk_id, "chunk_id")
            update_data["updated_at"] = datetime.now(timezone.utc)

            result = self.chunks_collection.update_one(
                {"_id": chunk_obj_id},
                {"$set": update_data}
            )

            # Success if chunk was found, even if values weren't modified
            return result.matched_count > 0
        except ValueError as ve:
            self.logger.error(f"Invalid chunk_id format: {ve}")
            raise ValueError(f"Invalid chunk_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error updating chunk {chunk_id}: {e}")
            raise Exception(f"Error updating chunk {chunk_id}: {e}")

    def delete_chunks_by_book(self, book_id: str) -> int:
        """
        Delete all chunks for a specific book.

        Args:
            book_id: ID of the book to delete chunks for

        Returns:
            Number of chunks deleted

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            result = self.chunks_collection.delete_many({"book_id": book_obj_id})
            return result.deleted_count
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error deleting chunks for book {book_id}: {e}")
            raise Exception(f"Error deleting chunks for book {book_id}: {e}")

    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a specific chunk.

        Args:
            chunk_id: ID of the chunk to delete

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            ValueError: If chunk_id is invalid
        """
        try:
            chunk_obj_id = self._validate_object_id(chunk_id, "chunk_id")
            result = self.chunks_collection.delete_one({"_id": chunk_obj_id})
            return result.deleted_count > 0
        except ValueError as ve:
            self.logger.error(f"Invalid chunk_id format: {ve}")
            raise ValueError(f"Invalid chunk_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error deleting chunk {chunk_id}: {e}")
            raise Exception(f"Error deleting chunk {chunk_id}: {e}")

    def get_chunk_count_by_book(self, book_id: str) -> int:
        """
        Get the number of chunks for a specific book.

        Args:
            book_id: ID of the book

        Returns:
            Number of chunks for the book

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            return self.chunks_collection.count_documents({"book_id": book_obj_id})
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error counting chunks for book {book_id}: {e}")
            raise Exception(f"Error counting chunks for book {book_id}: {e}")

    def get_chunk_statistics(self, book_id: str) -> Dict:
        """
        Get comprehensive statistics about chunks for a book.

        Args:
            book_id: ID of the book

        Returns:
            Dictionary with chunk statistics
        """
        chunks = self.get_chunks_by_book(book_id)

        if not chunks:
            return self._get_empty_statistics()

        token_counts = [c["estimated_token_count"] for c in chunks]
        word_counts = [c["word_count"] for c in chunks]
        sentence_counts = [c["sentence_count"] for c in chunks]

        # Calculate overlap statistics
        total_overlap_tokens = 0
        overlap_instances = 0

        for i in range(1, len(chunks)):
            overlap_tokens = chunks[i]["overlap_info"]["previous_chunk_overlap"]
            if overlap_tokens > 0:
                total_overlap_tokens += overlap_tokens
                overlap_instances += 1

        avg_overlap_tokens = (total_overlap_tokens / overlap_instances
                            ) if overlap_instances > 0 else 0

        # Get chunking configuration for overlap calculation
        chunking_config = self._get_chunking_config(book_id)
        if chunking_config:
            chunker = IntelligentTextChunker(
                model_name=chunking_config["model_name"],
                max_tokens=chunking_config["max_tokens"],
                overlap_tokens=chunking_config["overlap_tokens"],
                min_chunk_tokens=chunking_config["min_chunk_tokens"]
            )
            overlap_score = self._calculate_overlap_score(chunks, chunker)
        else:
            overlap_score = 0.0

        return {
            "chunk_count": len(chunks),
            "total_estimated_tokens": sum(token_counts),
            "total_words": sum(word_counts),
            "total_sentences": sum(sentence_counts),
            "avg_tokens_per_chunk": round(sum(token_counts) / len(chunks), 2),
            "avg_words_per_chunk": round(sum(word_counts) / len(chunks), 2),
            "avg_sentences_per_chunk": round(sum(sentence_counts) / len(chunks), 2),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "token_range": max(token_counts) - min(token_counts),
            "overlap_stats": {
                "total_overlap_tokens": total_overlap_tokens,
                "avg_overlap_tokens": round(avg_overlap_tokens, 2),
                "overlap_instances": overlap_instances,
                "overlap_coverage": round((overlap_instances / max(1, len(chunks) - 1)) * 100, 2)
            },
            "quality_metrics": {
                "chunk_size_consistency": self._calculate_consistency_score(token_counts),
                "overlap_effectiveness": overlap_score,
                "sentence_integrity": 1.0  # All chunks maintain sentence integrity
            }
        }

    def validate_chunks(self, book_id: str) -> Dict:
        """
        Validate chunks for a book meet quality requirements.

        Args:
            book_id: ID of the book to validate chunks for

        Returns:
            Dictionary with validation results and warnings
        """
        chunks = self.get_chunks_by_book(book_id)

        if not chunks:
            return {"valid": False, "warnings": ["No chunks found for this book"]}

        warnings_list = []
        all_valid = True

        # Get the chunking configuration used for this book
        chunking_config = self._get_chunking_config(book_id)

        if not chunking_config:
            warnings_list.append("Chunking configuration not found for validation")
            return {
                "valid": False,
                "warnings": warnings_list,
                "chunk_count": len(chunks),
                "validation_time": datetime.now(timezone.utc).isoformat()
            }

        # Create chunker with the original configuration
        chunker = IntelligentTextChunker(
            model_name=chunking_config["model_name"],
            max_tokens=chunking_config["max_tokens"],
            overlap_tokens=chunking_config["overlap_tokens"],
            min_chunk_tokens=chunking_config["min_chunk_tokens"]
        )

        for i, chunk in enumerate(chunks):
            if chunk["estimated_token_count"] < chunker.min_chunk_tokens:
                warnings_list.append(f"Chunk {i} too small: {chunk['estimated_token_count']} tokens")
                all_valid = False
            if chunk["estimated_token_count"] > chunker.max_tokens * 1.2:  # Allow 20% buffer
                warnings_list.append(f"Chunk {i} too large: {chunk['estimated_token_count']} tokens")
                all_valid = False

        # Check overlap effectiveness
        overlap_instances = sum(1 for chunk in chunks[1:] if chunk["overlap_info"]["previous_chunk_overlap"] > 0)
        if len(chunks) > 1 and overlap_instances < len(chunks) - 1:
            warnings_list.append(f"Insufficient overlap: {overlap_instances}/{len(chunks)-1} chunk transitions")

        return {
            "valid": all_valid,
            "warnings": warnings_list,
            "chunk_count": len(chunks),
            "validation_time": datetime.now(timezone.utc).isoformat()
        }

    def reorder_chunks(self, book_id: str, new_order: List[str]) -> bool:
        """
        Reorder chunks for a book based on a new sequence.

        Args:
            book_id: ID of the book
            new_order: List of chunk IDs in the new desired order

        Returns:
            True if reordering was successful, False otherwise
        """
        try:
            # First validate that all chunk IDs belong to the specified book
            chunks = self.get_chunks_by_book(book_id)
            chunk_ids = [str(c["_id"]) for c in chunks]

            for chunk_id in new_order:
                if chunk_id not in chunk_ids:
                    raise ValueError(f"Chunk {chunk_id} does not belong to book {book_id}")

            # Update sequence numbers
            for sequence_number, chunk_id in enumerate(new_order):
                self.chunks_collection.update_one(
                    {"_id": ObjectId(chunk_id)},
                    {"$set": {"sequence_number": sequence_number}}
                )

            return True

        except Exception as e:
            print(f"Error reordering chunks: {e}")
            return False

    def get_chunk_sequence(self, book_id: str) -> List[Dict]:
        """
        Get the sequence of chunks for a book in order.

        Args:
            book_id: ID of the book

        Returns:
            List of chunks in sequence order
        """
        return self.get_chunks_by_book(book_id, sort_by_sequence=True)

    def _calculate_consistency_score(self, token_counts: List[int]) -> float:
        """Calculate chunk size consistency score (0-1, higher is better)."""
        if len(token_counts) <= 1:
            return 1.0

        avg_size = sum(token_counts) / len(token_counts)
        variance = sum((x - avg_size) ** 2 for x in token_counts) / len(token_counts)
        std_dev = variance ** 0.5

        # Normalize to 0-1 range
        max_std_dev = avg_size * 0.5  # Allow 50% variation
        return max(0, 1 - (std_dev / max_std_dev))

    def _calculate_overlap_score(self, chunks: List[Dict], chunker: IntelligentTextChunker) -> float:
        """Calculate overlap effectiveness score (0-1, higher is better)."""
        if len(chunks) <= 1:
            return 1.0

        effective_overlaps = 0
        total_possible = len(chunks) - 1

        for i in range(1, len(chunks)):
            overlap_tokens = chunks[i]["overlap_info"]["previous_chunk_overlap"]
            if overlap_tokens >= chunker.overlap_tokens * 0.7:  # At least 70% of target overlap
                effective_overlaps += 1

        return effective_overlaps / total_possible

    def _get_empty_statistics(self) -> Dict:
        """Return empty statistics template."""
        return {
            "chunk_count": 0,
            "total_estimated_tokens": 0,
            "total_words": 0,
            "total_sentences": 0,
            "avg_tokens_per_chunk": 0,
            "avg_words_per_chunk": 0,
            "avg_sentences_per_chunk": 0,
            "min_tokens": 0,
            "max_tokens": 0,
            "token_range": 0,
            "overlap_stats": {
                "total_overlap_tokens": 0,
                "avg_overlap_tokens": 0,
                "overlap_instances": 0,
                "overlap_coverage": 0
            },
            "quality_metrics": {
                "chunk_size_consistency": 0,
                "overlap_effectiveness": 0,
                "sentence_integrity": 0
            }
        }

    def get_first_chunk(self, book_id: str) -> Optional[Dict]:
        """
        Get the first chunk for a book.

        Args:
            book_id: ID of the book

        Returns:
            First chunk document or None if no chunks exist

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            return self.chunks_collection.find_one({
                "book_id": book_obj_id,
                "is_first_chunk": True
            })
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving first chunk for book {book_id}: {e}")
            raise Exception(f"Error retrieving first chunk for book {book_id}: {e}")

    def get_last_chunk(self, book_id: str) -> Optional[Dict]:
        """
        Get the last chunk for a book.

        Args:
            book_id: ID of the book

        Returns:
            Last chunk document or None if no chunks exist

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            return self.chunks_collection.find_one({
                "book_id": book_obj_id,
                "is_last_chunk": True
            })
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving last chunk for book {book_id}: {e}")
            raise Exception(f"Error retrieving last chunk for book {book_id}: {e}")

    def get_chunk_by_sequence(self, book_id: str, sequence_number: int) -> Optional[Dict]:
        """
        Get a specific chunk by its sequence number.

        Args:
            book_id: ID of the book
            sequence_number: Sequence number of the chunk

        Returns:
            Chunk document or None if not found

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            return self.chunks_collection.find_one({
                "book_id": book_obj_id,
                "sequence_number": sequence_number
            })
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving chunk by sequence for book {book_id}: {e}")
            raise Exception(f"Error retrieving chunk by sequence for book {book_id}: {e}")

    def get_chunks_in_range(self, book_id: str, start_seq: int, end_seq: int) -> List[Dict]:
        """
        Get chunks within a specific sequence range.

        Args:
            book_id: ID of the book
            start_seq: Starting sequence number (inclusive)
            end_seq: Ending sequence number (inclusive)

        Returns:
            List of chunks in the specified range

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            return list(self.chunks_collection.find({
                "book_id": book_obj_id,
                "sequence_number": {"$gte": start_seq, "$lte": end_seq}
            }).sort("sequence_number", 1))
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving chunks in range for book {book_id}: {e}")
            raise Exception(f"Error retrieving chunks in range for book {book_id}: {e}")

    def update_book_status_with_chunks(self, book_id: str, status: str) -> bool:
        """
        Update book status and ensure chunks are properly linked.

        Args:
            book_id: ID of the book
            status: New status for the book

        Returns:
            True if both book and chunk updates were successful, False otherwise

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")

            # Get current book status for potential rollback
            current_book = self.books_collection.find_one({"_id": book_obj_id})
            if current_book is None:
                self.logger.warning(f"Book {book_id} not found")
                return False

            current_status = current_book.get("status")

            book_update_success = False
            chunk_update_success = False

            try:
                # Update book status
                book_result = self.books_collection.update_one(
                    {"_id": book_obj_id},
                    {"$set": {"status": status}}
                )
                book_update_success = book_result.matched_count > 0

                # Also update chunks to reflect the book status
                chunk_result = self.chunks_collection.update_many(
                    {"book_id": book_obj_id},
                    {"$set": {"book_status": status}}
                )
                chunk_update_success = chunk_result.matched_count > 0

                # Both updates successful
                if book_update_success and chunk_update_success:
                    return True

            except Exception as update_e:
                self.logger.error(f"Error during status update for book {book_id}: {update_e}")
                chunk_update_success = False

            # Rollback logic if updates were not both successful
            if book_update_success and not chunk_update_success and current_status is not None:
                try:
                    self.logger.warning(f"Rolling back book status for {book_id} from {status} to {current_status}")
                    self.books_collection.update_one(
                        {"_id": book_obj_id},
                        {"$set": {"status": current_status}}
                    )
                except Exception as rollback_e:
                    self.logger.error(f"Failed to rollback book status for {book_id}: {rollback_e}")

            return False

        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error updating book status for book {book_id}: {e}")
            raise Exception(f"Error updating book status for book {book_id}: {e}")

    def get_book_with_chunks(self, book_id: str) -> Optional[Dict]:
        """
        Get a book document along with its chunk statistics.

        Args:
            book_id: ID of the book

        Returns:
            Book document with chunk statistics or None if not found

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            book = self.books_collection.find_one({"_id": book_obj_id})

            if not book:
                return None

            chunk_stats = self.get_chunk_statistics(book_id)

            book_with_chunks = dict(book)
            book_with_chunks["chunk_statistics"] = chunk_stats

            return book_with_chunks
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving book with chunks for book {book_id}: {e}")
            raise Exception(f"Error retrieving book with chunks for book {book_id}: {e}")

    def delete_book_and_chunks(self, book_id: str) -> bool:
        """
        Delete a book and all its associated chunks.

        Args:
            book_id: ID of the book to delete

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")

            # Delete chunks first
            self.delete_chunks_by_book(book_id)

            # Then delete the book
            result = self.books_collection.delete_one({"_id": book_obj_id})

            return result.deleted_count > 0
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error deleting book and chunks for book {book_id}: {e}")
            raise Exception(f"Error deleting book and chunks for book {book_id}: {e}")

    def _store_chunking_config(self, book_id: str, model_name: str,
                             max_tokens: int, overlap_tokens: int,
                             min_chunk_tokens: int) -> bool:
        """
        Store chunking configuration in the book document.

        Args:
            book_id: ID of the book
            model_name: Name of the model used for chunking
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            min_chunk_tokens: Minimum tokens for a valid chunk

        Returns:
            True if configuration was stored successfully

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            chunking_config = {
                "model_name": model_name,
                "max_tokens": max_tokens,
                "overlap_tokens": overlap_tokens,
                "min_chunk_tokens": min_chunk_tokens,
                "created_at": datetime.now(timezone.utc)
            }

            result = self.books_collection.update_one(
                {"_id": book_obj_id},
                {"$set": {"chunking_config": chunking_config}}
            )

            return result.modified_count > 0
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error storing chunking configuration for book {book_id}: {e}")
            raise Exception(f"Error storing chunking configuration for book {book_id}: {e}")

    def _get_chunking_config(self, book_id: str) -> Optional[Dict]:
        """
        Retrieve chunking configuration for a book.

        Args:
            book_id: ID of the book

        Returns:
            Chunking configuration dictionary or None if not found

        Raises:
            ValueError: If book_id is invalid
        """
        try:
            book_obj_id = self._validate_object_id(book_id, "book_id")
            book = self.books_collection.find_one(
                {"_id": book_obj_id},
                {"chunking_config": 1}
            )

            if book and "chunking_config" in book:
                return book["chunking_config"]
            else:
                return None
        except ValueError as ve:
            self.logger.error(f"Invalid book_id format: {ve}")
            raise ValueError(f"Invalid book_id format: {ve}")
        except Exception as e:
            self.logger.error(f"Error retrieving chunking configuration for book {book_id}: {e}")
            raise Exception(f"Error retrieving chunking configuration for book {book_id}: {e}")

# Singleton instance for easy access
chunk_repository = ChunkRepository()
