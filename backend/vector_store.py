"""
Vector Store Integration for ShadowOps Digest

FAISS-based vector database for semantic search and similarity detection
of IT support tickets using embeddings for enhanced clustering accuracy.
"""

import logging
import os
import pickle
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
from datetime import datetime

logger = logging.getLogger(__name__)


class TicketVectorStore:
    """
    FAISS-based vector store for ticket embeddings and semantic search.
    
    Provides functionality to store, index, and search ticket embeddings
    for improved clustering and similarity detection capabilities.
    """
    
    def __init__(self, dimension: int = 1536, index_type: str = "flat"):
        """
        Initialize the vector store with FAISS index.
        
        Args:
            dimension: Embedding dimension (1536 for OpenAI ada-002)
            index_type: FAISS index type ("flat" or "ivf")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadata = []  # Store ticket metadata
        self.is_trained = False
        
        # Initialize FAISS index
        self._initialize_index()
        
        logger.info(f"Vector store initialized with {index_type} index, dimension: {dimension}")
    
    def _initialize_index(self):
        """Initialize the appropriate FAISS index based on configuration."""
        if self.index_type == "flat":
            # Flat index for exact search (good for small datasets)
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            self.is_trained = True
        elif self.index_type == "ivf":
            # IVF index for approximate search (better for large datasets)
            nlist = 100  # Number of clusters for IVF
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.is_trained = False
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
    
    def store_embeddings(self, embeddings: np.ndarray, metadata: List[Dict]) -> bool:
        """
        Store embeddings and associated metadata in the vector store.
        
        Args:
            embeddings: NumPy array of embeddings to store
            metadata: List of metadata dictionaries for each embedding
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            if len(embeddings) != len(metadata):
                raise ValueError("Number of embeddings must match number of metadata entries")
            
            # Normalize embeddings for cosine similarity
            normalized_embeddings = self._normalize_embeddings(embeddings)
            
            # Train index if necessary (for IVF)
            if not self.is_trained and self.index_type == "ivf":
                if len(normalized_embeddings) >= 100:  # Need sufficient data for training
                    self.index.train(normalized_embeddings.astype(np.float32))
                    self.is_trained = True
                    logger.info("IVF index trained successfully")
                else:
                    logger.warning("Insufficient data for IVF training, using flat index")
                    self._initialize_index()  # Fall back to flat index
            
            # Add embeddings to index
            if self.is_trained:
                self.index.add(normalized_embeddings.astype(np.float32))
                self.metadata.extend(metadata)
                
                logger.info(f"Stored {len(embeddings)} embeddings in vector store")
                return True
            else:
                logger.error("Index not trained, cannot store embeddings")
                return False
                
        except Exception as e:
            logger.error(f"Failed to store embeddings: {e}")
            return False
    
    def search_similar_tickets(self, query_embedding: np.ndarray, k: int = 5, 
                             threshold: float = 0.7) -> List[Dict]:
        """
        Search for similar tickets using embedding similarity.
        
        Args:
            query_embedding: Query embedding to search for
            k: Number of similar tickets to return
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar ticket metadata with similarity scores
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty, no similar tickets found")
                return []
            
            # Normalize query embedding
            normalized_query = self._normalize_embeddings(query_embedding.reshape(1, -1))
            
            # Search for similar embeddings
            scores, indices = self.index.search(normalized_query.astype(np.float32), k)
            
            # Filter results by threshold and format response
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and score >= threshold:  # -1 indicates no match found
                    result = self.metadata[idx].copy()
                    result['similarity_score'] = float(score)
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar tickets above threshold {threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar tickets: {e}")
            return []
    
    def get_cluster_representatives(self, cluster_indices: List[int], 
                                 embeddings: np.ndarray) -> Dict[str, any]:
        """
        Find representative embeddings for a cluster of tickets.
        
        Args:
            cluster_indices: Indices of tickets in the cluster
            embeddings: All ticket embeddings
            
        Returns:
            Dictionary with cluster statistics and representative embedding
        """
        try:
            if not cluster_indices:
                return {}
            
            # Get embeddings for cluster
            cluster_embeddings = embeddings[cluster_indices]
            
            # Calculate cluster centroid
            centroid = np.mean(cluster_embeddings, axis=0)
            
            # Find most representative ticket (closest to centroid)
            similarities = np.dot(cluster_embeddings, centroid) / (
                np.linalg.norm(cluster_embeddings, axis=1) * np.linalg.norm(centroid)
            )
            most_representative_idx = cluster_indices[np.argmax(similarities)]
            
            # Calculate cluster cohesion (average pairwise similarity)
            cohesion = self._calculate_cluster_cohesion(cluster_embeddings)
            
            return {
                'centroid': centroid,
                'representative_ticket_idx': most_representative_idx,
                'cohesion_score': cohesion,
                'size': len(cluster_indices)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster representatives: {e}")
            return {}
    
    def update_vector_index(self, new_embeddings: np.ndarray, new_metadata: List[Dict]) -> bool:
        """
        Update the vector index with new embeddings and metadata.
        
        Args:
            new_embeddings: New embeddings to add
            new_metadata: Corresponding metadata for new embeddings
            
        Returns:
            True if update was successful, False otherwise
        """
        return self.store_embeddings(new_embeddings, new_metadata)
    
    def save_index(self, filepath: str) -> bool:
        """
        Save the FAISS index and metadata to disk.
        
        Args:
            filepath: Path to save the index (without extension)
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{filepath}.faiss")
            
            # Save metadata
            with open(f"{filepath}_metadata.pkl", 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'dimension': self.dimension,
                    'index_type': self.index_type,
                    'is_trained': self.is_trained,
                    'saved_at': datetime.utcnow().isoformat()
                }, f)
            
            logger.info(f"Vector store saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            return False
    
    def load_index(self, filepath: str) -> bool:
        """
        Load a FAISS index and metadata from disk.
        
        Args:
            filepath: Path to load the index from (without extension)
            
        Returns:
            True if load was successful, False otherwise
        """
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{filepath}.faiss")
            
            # Load metadata
            with open(f"{filepath}_metadata.pkl", 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.dimension = data['dimension']
                self.index_type = data['index_type']
                self.is_trained = data['is_trained']
            
            logger.info(f"Vector store loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with vector store statistics
        """
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'is_trained': self.is_trained,
            'metadata_count': len(self.metadata)
        }
    
    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Normalize embeddings for cosine similarity calculation.
        
        Args:
            embeddings: Raw embeddings to normalize
            
        Returns:
            L2-normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        return embeddings / norms
    
    def _calculate_cluster_cohesion(self, cluster_embeddings: np.ndarray) -> float:
        """
        Calculate the cohesion score for a cluster of embeddings.
        
        Args:
            cluster_embeddings: Embeddings in the cluster
            
        Returns:
            Average pairwise cosine similarity (0-1)
        """
        if len(cluster_embeddings) <= 1:
            return 1.0
        
        # Calculate pairwise cosine similarities
        normalized = self._normalize_embeddings(cluster_embeddings)
        similarity_matrix = np.dot(normalized, normalized.T)
        
        # Get upper triangle (excluding diagonal)
        upper_triangle = np.triu(similarity_matrix, k=1)
        similarities = upper_triangle[upper_triangle > 0]
        
        return float(np.mean(similarities)) if len(similarities) > 0 else 0.0


def create_vector_store(dimension: int = 1536, index_type: str = "flat") -> TicketVectorStore:
    """
    Factory function to create a new vector store instance.
    
    Args:
        dimension: Embedding dimension
        index_type: FAISS index type
        
    Returns:
        Initialized TicketVectorStore instance
    """
    return TicketVectorStore(dimension=dimension, index_type=index_type)