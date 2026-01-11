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
        self.business_collection = self.client.get_or_create_collection(
            name="business_information",
            metadata={"description": "Business information for users"}
        )
        
        # Get or create the products collection
        self.products_collection = self.client.get_or_create_collection(
            name="product_information",
            metadata={"description": "Product information for businesses"}
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
            self.business_collection.upsert(
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
            collection_count = self.business_collection.count()
            
            # If no businesses, return empty list
            if collection_count == 0:
                return []
            
            # Adjust n_results to not exceed available businesses
            actual_n_results = min(n_results, collection_count)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.business_collection.query(
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
            results = self.business_collection.get(
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
            self.business_collection.delete(ids=[business_id])
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
            results = self.business_collection.get(
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
    
    # Product methods
    def add_product(self, product_id: str, product_description: str, business_id: int, username: str) -> bool:
        """
        Add or update product information in ChromaDB.
        
        Args:
            product_id: Unique ID for the product (format: product_{business_id}_{product_pk})
            product_description: Product description text
            business_id: ID of the business that owns the product
            username: Username of the business owner
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(product_description).tolist()
            
            # Add to ChromaDB
            self.products_collection.upsert(
                ids=[product_id],
                embeddings=[embedding],
                documents=[product_description],
                metadatas=[{
                    "username": username,
                    "business_id": business_id,
                    "type": "product"
                }]
            )
            return True
        except Exception as e:
            print(f"Error adding product to ChromaDB: {e}")
            return False
    
    def search_products(self, query: str, n_results: int = 5, business_id: Optional[int] = None) -> List[Dict]:
        """
        Search for products based on a query.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            business_id: Optional business ID to filter results
            
        Returns:
            List of dictionaries containing product information
        """
        try:
            # Check how many products exist in the collection
            collection_count = self.products_collection.count()
            
            # If no products, return empty list
            if collection_count == 0:
                return []
            
            # Adjust n_results to not exceed available products
            actual_n_results = min(n_results, collection_count)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB with optional filtering
            where_filter = {"business_id": business_id} if business_id else None
            
            results = self.products_collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            products = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    products.append({
                        'id': results['ids'][0][i],
                        'product_description': results['documents'][0][i],
                        'username': results['metadatas'][0][i].get('username', 'Unknown'),
                        'business_id': results['metadatas'][0][i].get('business_id'),
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return products
        except Exception as e:
            print(f"Error searching products in ChromaDB: {e}")
            return []
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get a specific product by ID.
        
        Args:
            product_id: Unique ID for the product
            
        Returns:
            Dictionary containing product information or None
        """
        try:
            results = self.products_collection.get(
                ids=[product_id],
                include=["documents", "metadatas"]
            )
            
            if results and results['documents']:
                return {
                    'id': results['ids'][0],
                    'product_description': results['documents'][0],
                    'username': results['metadatas'][0].get('username', 'Unknown'),
                    'business_id': results['metadatas'][0].get('business_id')
                }
            return None
        except Exception as e:
            print(f"Error getting product from ChromaDB: {e}")
            return None
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from ChromaDB.
        
        Args:
            product_id: Unique ID for the product
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.products_collection.delete(ids=[product_id])
            return True
        except Exception as e:
            print(f"Error deleting product from ChromaDB: {e}")
            return False
    
    def delete_products_by_business(self, business_id: int) -> bool:
        """
        Delete all products for a specific business from ChromaDB.
        
        Args:
            business_id: ID of the business
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all products for this business
            results = self.products_collection.get(
                where={"business_id": business_id},
                include=["metadatas"]
            )
            
            if results and results['ids']:
                # Delete all matching products
                self.products_collection.delete(ids=results['ids'])
            
            return True
        except Exception as e:
            print(f"Error deleting products by business from ChromaDB: {e}")
            return False


# Create a singleton instance
chroma_service = ChromaDBService()
