"""
ChromaDB service for storing and retrieving business information embeddings.
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os
from pathlib import Path


class ChromaDBService:
    """
    Service to interact with ChromaDB for business information storage and retrieval.
    """
    
    def __init__(self):
        """Initialize ChromaDB client and embedding model."""
        # Use persistent storage in the backend directory
        from django.conf import settings
        base_dir = settings.BASE_DIR
        chroma_dir = base_dir / 'chroma_data'
        chroma_dir.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create the business collection
        self.collection = self.client.get_or_create_collection(
            name="business_information",
            metadata={"description": "Business information for users"}
        )
    
    def add_business(self, business_id: str, business_info: str, username: str) -> bool:
        """
        Add or update business information in ChromaDB.
        
        Args:
            business_id: Unique ID for the business (typically user_id)
            business_info: Business information text
            username: Username of the business owner
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(business_info).tolist()
            
            # Add to ChromaDB
            self.collection.upsert(
                ids=[business_id],
                embeddings=[embedding],
                documents=[business_info],
                metadatas=[{"username": username, "type": "business"}]
            )
            return True
        except Exception as e:
            print(f"Error adding business to ChromaDB: {e}")
            return False
    
    def search_businesses(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for businesses based on a query.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            
        Returns:
            List of dictionaries containing business information
        """
        try:
            # Check how many businesses exist in the collection
            collection_count = self.collection.count()
            
            # If no businesses, return empty list
            if collection_count == 0:
                return []
            
            # Adjust n_results to not exceed available businesses
            actual_n_results = min(n_results, collection_count)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_n_results
            )
            
            # Format results
            businesses = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    businesses.append({
                        'id': results['ids'][0][i],
                        'business_info': results['documents'][0][i],
                        'username': results['metadatas'][0][i].get('username', 'Unknown'),
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return businesses
        except Exception as e:
            print(f"Error searching businesses in ChromaDB: {e}")
            return []
    
    def get_business(self, business_id: str) -> Optional[Dict]:
        """
        Get a specific business by ID.
        
        Args:
            business_id: Unique ID for the business
            
        Returns:
            Dictionary containing business information or None
        """
        try:
            results = self.collection.get(
                ids=[business_id],
                include=["documents", "metadatas"]
            )
            
            if results and results['documents']:
                return {
                    'id': results['ids'][0],
                    'business_info': results['documents'][0],
                    'username': results['metadatas'][0].get('username', 'Unknown')
                }
            return None
        except Exception as e:
            print(f"Error getting business from ChromaDB: {e}")
            return None
    
    def delete_business(self, business_id: str) -> bool:
        """
        Delete a business from ChromaDB.
        
        Args:
            business_id: Unique ID for the business
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[business_id])
            return True
        except Exception as e:
            print(f"Error deleting business from ChromaDB: {e}")
            return False
    
    def get_all_businesses(self) -> List[Dict]:
        """
        Get all businesses from ChromaDB.
        
        Returns:
            List of dictionaries containing business information
        """
        try:
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            businesses = []
            if results and results['documents']:
                for i in range(len(results['documents'])):
                    businesses.append({
                        'id': results['ids'][i],
                        'business_info': results['documents'][i],
                        'username': results['metadatas'][i].get('username', 'Unknown')
                    })
            
            return businesses
        except Exception as e:
            print(f"Error getting all businesses from ChromaDB: {e}")
            return []


# Create a singleton instance
chroma_service = ChromaDBService()
