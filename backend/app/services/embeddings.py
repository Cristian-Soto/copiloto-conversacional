# embeddings.py
# Servicio para generar embeddings usando modelos de transformers
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingManager:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa el gestor de embeddings.
        
        Args:
            model_name (str): Nombre del modelo de sentence-transformers a usar
        """
        self.transformer_model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def create_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        """
        Genera embeddings vectoriales para una lista de fragmentos de texto.
        
        Args:
            text_chunks (List[str]): Lista de fragmentos de texto para procesar
            
        Returns:
            List[List[float]]: Lista de vectores embedding
        """
        try:
            #Optimizar para documentos muy grandes
            vector_embeddings = self.transformer_model.encode(text_chunks)
            return vector_embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error generando embeddings: {str(e)}")
    
    def create_single_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un fragmento individual de texto.
        
        Args:
            text (str): Texto para convertir a vector
            
        Returns:
            List[float]: Vector embedding del texto
        """
        try:
            embedding_vector = self.transformer_model.encode([text])
            return embedding_vector[0].tolist()
        except Exception as e:
            raise Exception(f"Error creando embedding individual: {str(e)}")
    
    def get_transformer_info(self) -> dict:
        """
        Obtiene información técnica del modelo transformer utilizado.
        
        Returns:
            dict: Detalles del modelo
        """
        return {
            "model_name": self.model_name,
            "max_sequence_length": self.transformer_model.max_seq_length,
            "vector_dimension": self.transformer_model.get_sentence_embedding_dimension()
        }

# Instancia global del gestor de embeddings
document_embedding_manager = EmbeddingManager()
