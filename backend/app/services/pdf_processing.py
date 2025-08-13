# pdf_processing.py
# Procesador de documentos PDF con extracción y fragmentación de texto
import fitz  # PyMuPDF
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_content(pdf_file_path: str) -> str:
    """
    Extrae contenido textual completo de un archivo PDF usando PyMuPDF.
    
    Args:
        pdf_file_path (str): Ruta al archivo PDF
        
    Returns:
        str: Contenido textual extraído
    """
    extracted_content = ""
    try:
        # Abrir documento PDF
        pdf_document = fitz.open(pdf_file_path)
        
        # Procesar cada página del documento
        for page_index in range(len(pdf_document)):
            page = pdf_document.load_page(page_index)
            extracted_content += page.get_text()
            
        pdf_document.close()
        return extracted_content
    except Exception as e:
        raise Exception(f"Error procesando archivo PDF: {str(e)}")

def extract_content_by_pages(pdf_file_path: str) -> List[str]:
    """
    Extrae contenido textual página por página del PDF.
    
    Args:
        pdf_file_path (str): Ruta al archivo PDF
        
    Returns:
        List[str]: Lista con contenido de cada página
    """
    pages_content = []
    try:
        pdf_document = fitz.open(pdf_file_path)
        
        for page_index in range(len(pdf_document)):
            page = pdf_document.load_page(page_index)
            page_content = page.get_text()
            pages_content.append(page_content)
            
        pdf_document.close()
        return pages_content
    except Exception as e:
        raise Exception(f"Error extrayendo contenido por páginas: {str(e)}")

def extract_document_metadata(pdf_file_path: str) -> dict:
    """
    Obtiene metadatos y propiedades del documento PDF.
    
    Args:
        pdf_file_path (str): Ruta al archivo PDF
        
    Returns:
        dict: Metadatos del documento
    """
    try:
        pdf_document = fitz.open(pdf_file_path)
        document_metadata = pdf_document.metadata
        document_metadata['total_pages'] = len(pdf_document)
        pdf_document.close()
        return document_metadata
    except Exception as e:
        raise Exception(f"Error obteniendo metadatos: {str(e)}")

def fragment_text_content(content: str, fragment_size: int = 1000, fragment_overlap: int = 200) -> List[str]:
    """
    Divide el contenido textual en fragmentos usando RecursiveCharacterTextSplitter.
    
    Args:
        content (str): Contenido textual a fragmentar
        fragment_size (int): Tamaño máximo de cada fragmento
        fragment_overlap (int): Superposición entre fragmentos
        
    Returns:
        List[str]: Lista de fragmentos de texto
    """
    try:
        # NOTE: Usando separadores jerárquicos para mejor fragmentación
        content_splitter = RecursiveCharacterTextSplitter(
            chunk_size=fragment_size,
            chunk_overlap=fragment_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        text_fragments = content_splitter.split_text(content)
        return text_fragments
    except Exception as e:
        raise Exception(f"Error fragmentando contenido: {str(e)}")

def process_pdf_document(pdf_file_path: str, fragment_size: int = 1000, fragment_overlap: int = 200) -> List[str]:
    """
    Procesa un PDF completo: extrae contenido y lo fragmenta.
    
    Args:
        pdf_file_path (str): Ruta al archivo PDF
        fragment_size (int): Tamaño máximo de cada fragmento
        fragment_overlap (int): Superposición entre fragmentos
        
    Returns:
        List[str]: Lista de fragmentos procesados
    """
    try:
        # Extraer contenido textual del PDF
        document_content = extract_text_content(pdf_file_path)
        
        # Fragmentar el contenido
        content_fragments = fragment_text_content(document_content, fragment_size, fragment_overlap)
        
        return content_fragments
    except Exception as e:
        raise Exception(f"Error procesando documento PDF: {str(e)}")
