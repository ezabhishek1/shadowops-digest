"""
Ticket Clustering Engine for ShadowOps Digest

AI-powered clustering module that groups IT support tickets by root cause using
OpenAI embeddings and semantic similarity analysis with scikit-learn fallback.
Includes FAISS vector store integration for enhanced similarity detection.
"""

import logging
import os
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from openai import OpenAI
import re
from vector_store import TicketVectorStore, create_vector_store

logger = logging.getLogger(__name__)


class TicketClusteringEngine:
    """
    AI-powered ticket clustering engine with OpenAI integration and fallback methods.
    
    Uses OpenAI embeddings for semantic understanding of ticket content,
    with scikit-learn KMeans as a fallback for offline scenarios.
    Includes FAISS vector store for enhanced similarity detection.
    """
    
    def __init__(self, use_vector_store: bool = True):
        """Initialize the clustering engine with OpenAI client and configuration."""
        self.openai_client = None
        self.use_openai = False
        self.use_vector_store = use_vector_store
        self.vector_store = None
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip() and api_key != "your_openai_api_key_here":
            try:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_openai = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.use_openai = False
        else:
            logger.info("OpenAI API key not found, using fallback clustering")
        
        # Initialize vector store if enabled and OpenAI is available
        if self.use_vector_store and self.use_openai:
            try:
                self.vector_store = create_vector_store(dimension=1536, index_type="flat")
                logger.info("Vector store initialized for similarity detection")
            except Exception as e:
                logger.warning(f"Failed to initialize vector store: {e}")
                self.vector_store = None
        
        # TF-IDF vectorizer for fallback clustering
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
    
    def cluster_tickets(self, tickets: List[str]) -> Dict[str, List[int]]:
        """
        Cluster tickets by root cause using AI or fallback methods.
        
        Args:
            tickets: List of ticket descriptions to cluster
            
        Returns:
            Dictionary mapping cluster names to lists of ticket indices
        """
        logger.info(f"Starting ticket clustering for {len(tickets)} tickets")
        
        if len(tickets) == 1:
            return {"General Issues": [0]}
        
        try:
            if self.use_openai:
                return self._cluster_with_openai(tickets)
            else:
                return self._cluster_with_sklearn(tickets)
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            # Emergency fallback - return all tickets in one cluster
            return {"General Issues": list(range(len(tickets)))}
    
    def _cluster_with_openai(self, tickets: List[str]) -> Dict[str, List[int]]:
        """
        Cluster tickets using OpenAI embeddings and semantic similarity.
        
        Args:
            tickets: List of ticket descriptions
            
        Returns:
            Dictionary of clusters with semantic names
        """
        logger.info("Using OpenAI embeddings for clustering")
        
        # Generate embeddings for all tickets
        embeddings = self._generate_embeddings(tickets)
        
        # Store embeddings in vector store if available
        if self.vector_store:
            metadata = [{"ticket_index": i, "description": tickets[i]} for i in range(len(tickets))]
            self.vector_store.store_embeddings(embeddings, metadata)
            logger.info("Embeddings stored in vector store for similarity search")
        
        # Determine optimal number of clusters
        n_clusters = self._determine_cluster_count(len(tickets))
        
        # Perform clustering on embeddings
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # Group tickets by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(i)
        
        # Enhance clustering with vector store similarity detection
        if self.vector_store:
            clusters = self._enhance_clusters_with_similarity(tickets, clusters, embeddings)
        
        # Generate semantic cluster names using OpenAI
        named_clusters = self._generate_cluster_names(tickets, clusters)
        
        logger.info(f"OpenAI clustering completed: {len(named_clusters)} clusters")
        return named_clusters
    
    def _generate_embeddings(self, tickets: List[str]) -> np.ndarray:
        """
        Generate OpenAI embeddings for ticket descriptions.
        
        Args:
            tickets: List of ticket descriptions
            
        Returns:
            NumPy array of embeddings
        """
        try:
            # Preprocess tickets for better embeddings
            processed_tickets = [self._preprocess_ticket(ticket) for ticket in tickets]
            
            # Generate embeddings using OpenAI
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=processed_tickets
            )
            
            embeddings = np.array([item.embedding for item in response.data])
            logger.info(f"Generated embeddings for {len(tickets)} tickets")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embeddings: {e}")
            raise
    
    def _generate_cluster_names(self, tickets: List[str], clusters: Dict[int, List[int]]) -> Dict[str, List[int]]:
        """
        Generate semantic names for clusters using OpenAI.
        
        Args:
            tickets: Original ticket descriptions
            clusters: Dictionary mapping cluster IDs to ticket indices
            
        Returns:
            Dictionary mapping semantic cluster names to ticket indices
        """
        named_clusters = {}
        
        for cluster_id, ticket_indices in clusters.items():
            # Get sample tickets from this cluster
            sample_tickets = [tickets[i] for i in ticket_indices[:5]]  # Max 5 samples
            
            try:
                # Generate cluster name using OpenAI
                cluster_name = self._ask_openai_for_cluster_name(sample_tickets)
                named_clusters[cluster_name] = ticket_indices
                
            except Exception as e:
                logger.warning(f"Failed to generate name for cluster {cluster_id}: {e}")
                # Fallback to generic name
                named_clusters[f"Issue Category {cluster_id + 1}"] = ticket_indices
        
        return named_clusters
    
    def _ask_openai_for_cluster_name(self, sample_tickets: List[str]) -> str:
        """
        Ask OpenAI to generate a descriptive name for a cluster of tickets.
        
        Args:
            sample_tickets: Sample tickets from the cluster
            
        Returns:
            Descriptive cluster name
        """
        tickets_text = "\n".join(f"- {ticket}" for ticket in sample_tickets)
        
        prompt = f"""Analyze these IT support tickets and provide a short, descriptive category name (2-4 words) that captures the root cause or common theme:

{tickets_text}

Category name:"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.3
        )
        
        cluster_name = response.choices[0].message.content.strip()
        
        # Clean up the cluster name
        cluster_name = re.sub(r'^["\']|["\']$', '', cluster_name)  # Remove quotes
        cluster_name = cluster_name.title()  # Title case
        
        # Ensure reasonable length
        if len(cluster_name) > 50:
            cluster_name = cluster_name[:47] + "..."
        
        return cluster_name or "General Issues"
    
    def _cluster_with_sklearn(self, tickets: List[str]) -> Dict[str, List[int]]:
        """
        Fallback clustering using scikit-learn TF-IDF and KMeans.
        
        Args:
            tickets: List of ticket descriptions
            
        Returns:
            Dictionary of clusters with rule-based names
        """
        logger.info("Using scikit-learn fallback clustering")
        
        # Preprocess tickets
        processed_tickets = [self._preprocess_ticket(ticket) for ticket in tickets]
        
        # Generate TF-IDF vectors
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_tickets)
        
        # Determine optimal number of clusters
        n_clusters = self._determine_cluster_count(len(tickets))
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Group tickets by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(i)
        
        # Generate rule-based cluster names
        named_clusters = self._generate_rule_based_names(tickets, clusters)
        
        logger.info(f"Scikit-learn clustering completed: {len(named_clusters)} clusters")
        return named_clusters
    
    def _generate_rule_based_names(self, tickets: List[str], clusters: Dict[int, List[int]]) -> Dict[str, List[int]]:
        """
        Generate cluster names using rule-based keyword analysis.
        
        Args:
            tickets: Original ticket descriptions
            clusters: Dictionary mapping cluster IDs to ticket indices
            
        Returns:
            Dictionary mapping descriptive names to ticket indices
        """
        # Common IT issue categories and their keywords
        category_keywords = {
            "Network Issues": ["vpn", "connection", "network", "internet", "wifi", "ethernet", "dns"],
            "Authentication Problems": ["password", "login", "access", "account", "authentication", "credentials"],
            "Email Issues": ["outlook", "email", "mail", "exchange", "smtp", "inbox"],
            "Hardware Problems": ["printer", "monitor", "keyboard", "mouse", "hardware", "device"],
            "Software Issues": ["application", "software", "program", "install", "update", "crash"],
            "Phone Issues": ["phone", "voip", "call", "dial", "telephone", "extension"],
            "Security Issues": ["virus", "malware", "security", "firewall", "antivirus", "threat"],
            "File Access": ["file", "folder", "share", "drive", "storage", "permission"]
        }
        
        named_clusters = {}
        
        for cluster_id, ticket_indices in clusters.items():
            cluster_tickets = [tickets[i].lower() for i in ticket_indices]
            cluster_text = " ".join(cluster_tickets)
            
            # Find best matching category
            best_category = "General Issues"
            best_score = 0
            
            for category, keywords in category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in cluster_text)
                if score > best_score:
                    best_score = score
                    best_category = category
            
            # Ensure unique cluster names
            original_name = best_category
            counter = 1
            while best_category in named_clusters:
                best_category = f"{original_name} {counter}"
                counter += 1
            
            named_clusters[best_category] = ticket_indices
        
        return named_clusters
    
    def _preprocess_ticket(self, ticket: str) -> str:
        """
        Preprocess ticket description for better clustering.
        
        Args:
            ticket: Raw ticket description
            
        Returns:
            Cleaned and normalized ticket text
        """
        # Convert to lowercase
        text = ticket.lower().strip()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove very short words (less than 2 characters)
        words = [word for word in text.split() if len(word) >= 2]
        
        return ' '.join(words)
    
    def _enhance_clusters_with_similarity(self, tickets: List[str], clusters: Dict[int, List[int]], 
                                        embeddings: np.ndarray) -> Dict[int, List[int]]:
        """
        Enhance clustering results using vector store similarity detection.
        
        Args:
            tickets: Original ticket descriptions
            clusters: Initial clustering results
            embeddings: Ticket embeddings
            
        Returns:
            Enhanced clustering with similarity-based refinements
        """
        try:
            enhanced_clusters = clusters.copy()
            
            # For each cluster, find potential similar tickets that might belong
            for cluster_id, ticket_indices in clusters.items():
                if len(ticket_indices) < 2:  # Skip single-ticket clusters
                    continue
                
                # Get cluster representative
                cluster_stats = self.vector_store.get_cluster_representatives(ticket_indices, embeddings)
                if not cluster_stats:
                    continue
                
                # Search for similar tickets using the representative
                representative_idx = cluster_stats['representative_ticket_idx']
                representative_embedding = embeddings[representative_idx]
                
                similar_tickets = self.vector_store.search_similar_tickets(
                    representative_embedding, k=min(10, len(tickets)), threshold=0.8
                )
                
                # Add highly similar tickets to this cluster if they're not already well-placed
                for similar_ticket in similar_tickets:
                    ticket_idx = similar_ticket['ticket_index']
                    similarity_score = similar_ticket['similarity_score']
                    
                    # Only move tickets with very high similarity (>0.85) to avoid disrupting good clusters
                    if similarity_score > 0.85 and ticket_idx not in ticket_indices:
                        # Check if this ticket is in a small cluster (might be misplaced)
                        current_cluster = None
                        for cid, indices in enhanced_clusters.items():
                            if ticket_idx in indices:
                                current_cluster = cid
                                break
                        
                        # Move ticket if it's in a small cluster or isolated
                        if current_cluster is not None and len(enhanced_clusters[current_cluster]) <= 2:
                            enhanced_clusters[current_cluster].remove(ticket_idx)
                            enhanced_clusters[cluster_id].append(ticket_idx)
                            logger.debug(f"Moved ticket {ticket_idx} to cluster {cluster_id} based on similarity")
            
            # Clean up empty clusters
            enhanced_clusters = {cid: indices for cid, indices in enhanced_clusters.items() if indices}
            
            return enhanced_clusters
            
        except Exception as e:
            logger.warning(f"Failed to enhance clusters with similarity: {e}")
            return clusters
    
    def find_similar_tickets(self, query_ticket: str, k: int = 5) -> List[Dict]:
        """
        Find tickets similar to a query ticket using vector store.
        
        Args:
            query_ticket: Ticket description to find similar tickets for
            k: Number of similar tickets to return
            
        Returns:
            List of similar tickets with metadata and similarity scores
        """
        if not self.vector_store or not self.use_openai:
            logger.warning("Vector store not available for similarity search")
            return []
        
        try:
            # Generate embedding for query ticket
            query_embedding = self._generate_embeddings([query_ticket])[0]
            
            # Search for similar tickets
            similar_tickets = self.vector_store.search_similar_tickets(
                query_embedding, k=k, threshold=0.5
            )
            
            return similar_tickets
            
        except Exception as e:
            logger.error(f"Failed to find similar tickets: {e}")
            return []
    
    def get_cluster_insights(self, tickets: List[str], clusters: Dict[str, List[int]]) -> Dict[str, Dict]:
        """
        Get detailed insights about clusters using vector store analysis.
        
        Args:
            tickets: Original ticket descriptions
            clusters: Clustering results
            
        Returns:
            Dictionary with cluster insights and statistics
        """
        if not self.vector_store:
            return {}
        
        insights = {}
        
        try:
            # Generate embeddings if not already done
            embeddings = self._generate_embeddings(tickets)
            
            for cluster_name, ticket_indices in clusters.items():
                if len(ticket_indices) < 2:
                    insights[cluster_name] = {
                        "size": len(ticket_indices),
                        "cohesion_score": 1.0,
                        "representative_ticket": tickets[ticket_indices[0]] if ticket_indices else ""
                    }
                    continue
                
                # Get cluster statistics
                cluster_stats = self.vector_store.get_cluster_representatives(ticket_indices, embeddings)
                
                if cluster_stats:
                    representative_idx = cluster_stats['representative_ticket_idx']
                    insights[cluster_name] = {
                        "size": cluster_stats['size'],
                        "cohesion_score": cluster_stats['cohesion_score'],
                        "representative_ticket": tickets[representative_idx],
                        "representative_index": representative_idx
                    }
                else:
                    insights[cluster_name] = {
                        "size": len(ticket_indices),
                        "cohesion_score": 0.0,
                        "representative_ticket": tickets[ticket_indices[0]]
                    }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get cluster insights: {e}")
            return {}
    
    def _determine_cluster_count(self, num_tickets: int) -> int:
        """
        Determine optimal number of clusters based on ticket count.
        
        Args:
            num_tickets: Total number of tickets
            
        Returns:
            Optimal number of clusters (1-10)
        """
        if num_tickets <= 2:
            return 1
        elif num_tickets <= 5:
            return 2
        elif num_tickets <= 10:
            return 3
        elif num_tickets <= 20:
            return min(4, num_tickets // 3)
        elif num_tickets <= 50:
            return min(6, num_tickets // 5)
        else:
            return min(10, num_tickets // 8)


def cluster_tickets(tickets: List[str], use_vector_store: bool = True) -> Dict[str, List[int]]:
    """
    Main function to cluster tickets by root cause.
    
    Args:
        tickets: List of IT support ticket descriptions
        use_vector_store: Whether to use FAISS vector store for enhanced similarity detection
        
    Returns:
        Dictionary mapping cluster names to lists of ticket indices
    """
    engine = TicketClusteringEngine(use_vector_store=use_vector_store)
    return engine.cluster_tickets(tickets)


def find_similar_tickets(query_ticket: str, tickets: List[str], k: int = 5) -> List[Dict]:
    """
    Find tickets similar to a query ticket using vector store.
    
    Args:
        query_ticket: Ticket description to find similar tickets for
        tickets: List of all ticket descriptions to search within
        k: Number of similar tickets to return
        
    Returns:
        List of similar tickets with metadata and similarity scores
    """
    engine = TicketClusteringEngine(use_vector_store=True)
    
    # First cluster the tickets to populate the vector store
    engine.cluster_tickets(tickets)
    
    # Then find similar tickets
    return engine.find_similar_tickets(query_ticket, k)


def get_cluster_insights(tickets: List[str], clusters: Dict[str, List[int]]) -> Dict[str, Dict]:
    """
    Get detailed insights about clusters using vector store analysis.
    
    Args:
        tickets: Original ticket descriptions
        clusters: Clustering results
        
    Returns:
        Dictionary with cluster insights and statistics
    """
    engine = TicketClusteringEngine(use_vector_store=True)
    return engine.get_cluster_insights(tickets, clusters)