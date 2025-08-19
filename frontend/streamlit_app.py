#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================
Copiloto Conversacional - Frontend Interface
===============================================
Copyright (c) 2025 Cristian Soto
Desarrollado como prueba técnica

Uso comercial requiere licencia separada.
Ver LICENSE para términos completos.
Contacto: https://github.com/Cristian-Soto
===============================================
"""

import streamlit as st
import requests
import json
from typing import Optional

# Configuración de página - DEBE ser lo primero
st.set_page_config(
    page_title="Copiloto Conversacional",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    /* TEMA OSCURO COMPLETO */
    
    /* Configuración del body y elementos raíz */
    .main {
        padding-top: 2rem;
        background: linear-gradient(135deg, #0f1419 0%, #1a1d23 50%, #0f1419 100%);
        color: #e0e6ed;
    }
    
    /* Forzar modo oscuro en toda la aplicación */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1d23 50%, #0f1419 100%);
        color: #e0e6ed;
    }
    
    /* Header moderno oscuro */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #1e2328 0%, #2d3339 100%);
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        color: #e0e6ed;
    }
    
    /* Chat container oscuro */
    .chat-container {
        background: linear-gradient(135deg, #1e2328 0%, #2d3339 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        border: 1px solid rgba(102, 126, 234, 0.2);
        color: #e0e6ed;
    }
    
    /* Mensajes de chat oscuros */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .ai-message {
        background: linear-gradient(135deg, #2d3339 0%, #3d444d 100%);
        color: #e0e6ed;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        max-width: 80%;
        margin-right: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar oscuro */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f1419 0%, #1a1d23 100%);
        color: #e0e6ed;
    }
    
    /* Botones modernos oscuros */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #7c8ef7 0%, #8a5bb8 100%);
    }
    
    /* Input de texto oscuro */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, #2d3339 0%, #3d444d 100%) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        color: #e0e6ed !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.4) !important;
        transform: scale(1.02) !important;
        outline: none !important;
        background: linear-gradient(135deg, #3d444d 0%, #4d545d 100%) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #8a9ba8 !important;
        font-style: italic !important;
    }
    
    /* Selectbox oscuro */
    .stSelectbox > div > div > select {
        background: linear-gradient(135deg, #2d3339 0%, #3d444d 100%) !important;
        color: #e0e6ed !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 15px !important;
    }
    
    /* Slider oscuro */
    .stSlider > div > div > div > div {
        background: #667eea !important;
    }
    
    .stSlider > div > div > div {
        background: #2d3339 !important;
    }
    
    /* Métricas oscuras */
    .metric-value {
        color: #e0e6ed !important;
    }
    
    .metric-delta {
        color: #8a9ba8 !important;
    }
    
    /* Expanders oscuros */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        color: #e0e6ed !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3)) !important;
        transform: scale(1.01) !important;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #1e2328 0%, #2d3339 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 0 0 10px 10px !important;
        color: #e0e6ed !important;
    }
    
    /* Tabs oscuras */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #1e2328 0%, #2d3339 100%);
        border-radius: 15px;
        padding: 0.5rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8a9ba8;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Contenido de tabs oscuro */
    .stTabs > div[data-baseweb="tab-panel"] {
        background: linear-gradient(135deg, #1e2328 0%, #2d3339 100%);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
        color: #e0e6ed;
    }
    
    /* File uploader oscuro */
    .stFileUploader > div {
        background: linear-gradient(135deg, #2d3339 0%, #3d444d 100%) !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
        border-radius: 15px !important;
        color: #e0e6ed !important;
    }
    
    /* Columnas oscuras */
    .element-container {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Spinner oscuro */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Alertas oscuras */
    .stAlert {
        background: linear-gradient(135deg, #2d3339 0%, #3d444d 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        color: #e0e6ed !important;
    }
    
    /* Status indicators oscuros */
    .status-online {
        color: #4ade80;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
    }
    
    .status-offline {
        color: #f87171;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
    }
    
    /* Animaciones */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Texto general oscuro */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #e0e6ed !important;
    }
    
    /* Markdown oscuro */
    .markdown-text-container {
        color: #e0e6ed !important;
    }
    
    /* Caption oscuro */
    .caption {
        color: #8a9ba8 !important;
    }
    
    /* Form submit button oscuro */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #7c8ef7 0%, #8a5bb8 100%) !important;
    }
    
    /* Efectos adicionales para modo oscuro */
    .fade-in {
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Cards de documentos oscuras */
    .document-card {
        background: linear-gradient(135deg, #1e2328 0%, #2d3339 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        color: #e0e6ed !important;
        transition: all 0.3s ease !important;
    }
    
    .document-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.4) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuración de la API
API_BASE_URL = "http://backend:8000"

def send_document_to_api(uploaded_file) -> Optional[dict]:
    """
    Envía un documento PDF al backend para su procesamiento.
    
    Args:
        uploaded_file: Archivo subido desde Streamlit
        
    Returns:
        dict: Respuesta del backend o None si hay error
    """
    try:
        files = {"uploaded_file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error del servidor: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("No se puede conectar al backend. Verifica que los servicios estén ejecutándose.")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return None

def main():
    # Watermark de evaluación (reducido)
    st.markdown("""
    <div style="position: fixed; top: 10px; right: 10px; background: rgba(102, 126, 234, 0.9); 
                color: white; padding: 6px 12px; border-radius: 15px; z-index: 1000; 
                font-size: 11px; font-weight: 600; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        📋 Evaluación Técnica
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header fade-in">
        <p style="font-size: 1.4rem; color: #8a9ba8; margin-top: 1rem; font-weight: 400; line-height: 1.3;">
            Copiloto Conversacional
        </p>
        <p style="font-size: 1rem; color: #8a9ba8; margin-top: 1.2rem; font-style: italic; opacity: 0.8;">
            💡 Desarrollado por Cristian Soto como prueba técnica • © 2025
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegación moderna con tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat Inteligente", "📄 Mis Documentos", "🔬 Análisis Avanzado"])
    
    with tab1:
        modern_chat_page()
    
    with tab2:
        modern_documents_page()
        
    with tab3:
        modern_analysis_page()

def modern_chat_page():
    
    # Verificar estado del sistema
    system_status = get_system_status()
    
    # Contenedor principal del chat
    #st.markdown('<div class="chat-container fade-in">', unsafe_allow_html=True)
    
    # Status bar moderno
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        if system_status.get("ai_online", False):
            st.markdown('<p class="status-online">🟢 IA Local Activa</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-offline">🔴 IA Local Desconectada</p>', unsafe_allow_html=True)
    
    with col_status2:
        total_docs = system_status.get("total_documents", 0)
        st.markdown(f'<p style="font-weight: 600; color: #667eea;">📚 {total_docs} documentos</p>', unsafe_allow_html=True)
    
    with col_status3:
        total_fragments = system_status.get("total_fragments", 0)
        st.markdown(f'<p style="font-weight: 600; color: #f093fb;">🧩 {total_fragments} fragmentos</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload area moderna
    st.markdown("### 📤 Subir Nuevo Documento")
    
    uploaded_file = st.file_uploader(
        "",
        type=['pdf'],
        help="Arrastra tu PDF aquí o haz clic para seleccionar",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.markdown("""
        <div class="upload-area">
            <h4 style="color: #667eea; margin: 0;">✨ Archivo Listo para Procesar</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col_upload1, col_upload2 = st.columns([2, 1])
        
        with col_upload1:
            st.write(f"� **{uploaded_file.name}**")
            st.write(f"📊 Tamaño: {uploaded_file.size / 1024:.1f} KB")
        
        with col_upload2:
            if st.button("� Procesar Documento", type="primary", use_container_width=True):
                process_uploaded_document(uploaded_file)
    
    st.markdown("---")
    
    # Chat area moderno con IA
    st.markdown("### Conversación con IA")
    
    # Configuración avanzada colapsable
    with st.expander("⚙️ Configuración Avanzada", expanded=False):
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            max_results = st.slider("📄 Documentos relevantes", 1, 10, 7, key="modern_max_results")
        
        with col_config2:
            similarity_threshold = st.slider("🎯 Precisión de búsqueda", 0.1, 1.0, 0.3, 0.1, key="modern_similarity")
    
    # Inicializar historial de chat
    if "modern_chat_history" not in st.session_state:
        st.session_state.modern_chat_history = []
    
    # Mostrar historial de chat con diseño moderno
    chat_history_container = st.container()
    
    with chat_history_container:
        for message in st.session_state.modern_chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>🙋‍♂️ Tú:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                ai_icon = "🤖" if message.get("llm_used") == "ollama_direct" else "�"
                st.markdown(f"""
                <div class="ai-message">
                    <strong>{ai_icon} IA:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar documentos consultados
                if message.get("documents"):
                    with st.expander(f"� {len(message['documents'])} documentos consultados", expanded=False):
                        for doc in message["documents"][:3]:
                            st.caption(f"📄 {doc.get('filename', 'Sin nombre')} (relevancia: {doc.get('similarity_score', 0):.2f})")
    
    # Input moderno para nuevos mensajes
    st.markdown("---")
    
    # Área de input moderna
    # Área de input moderna con formulario (evita error de st.chat_input en contenedores)
    with st.form(key="chat_form_modern", clear_on_submit=True):
        user_input = st.text_area(
            "💭 Escribe tu pregunta aquí:",
            placeholder="Pregunta sobre tus documentos...",
            height=100,
            help="Escribe tu pregunta y presiona el botón para enviar"
        )
        submit_button = st.form_submit_button("🚀 Enviar Mensaje", type="primary", use_container_width=True)
    
    if submit_button and user_input:
        # Agregar mensaje del usuario
        st.session_state.modern_chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Procesar respuesta
        with st.spinner("🤔 IA está pensando..."):
            ai_response = process_chat_query(user_input, max_results, similarity_threshold)
            
            if ai_response:
                st.session_state.modern_chat_history.append(ai_response)
        
        st.rerun()
    
    # Botones de acción
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            st.session_state.modern_chat_history = []
            st.rerun()
    
    with col_action2:
        if st.button("📄 Resumir Conversación", use_container_width=True):
            if st.session_state.modern_chat_history:
                generate_conversation_summary()
    
    with col_action3:
        if st.button("💾 Exportar Chat", use_container_width=True):
            if st.session_state.modern_chat_history:
                export_chat_history()
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_system_status():
    """Obtiene el estado del sistema de manera simplificada"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Obtener información de documentos
            docs_response = requests.get(f"{API_BASE_URL}/api/chat/documents", timeout=5)
            docs_data = {}
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
            
            return {
                "ai_online": data.get("llm_service", {}).get("ollama_connected", False),
                "total_documents": docs_data.get("total_documents", 0),
                "total_fragments": docs_data.get("total_fragments", 0),
                "vector_db_connected": data.get("vector_database", {}).get("connected", False)
            }
    except:
        pass
    
    return {
        "ai_online": False,
        "total_documents": 0,
        "total_fragments": 0,
        "vector_db_connected": False
    }

def process_uploaded_document(uploaded_file):
    """Procesa un documento subido con interfaz moderna"""
    try:
        with st.spinner("🚀 Procesando documento..."):
            result = send_document_to_api(uploaded_file)
            
            if result:
                st.success("✅ ¡Documento procesado exitosamente!")
                
                # Estadísticas en cards modernas
                doc_stats = result.get('document_stats', {})
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #667eea; margin: 0;">📄</h3>
                        <p style="font-size: 1.5rem; font-weight: bold; margin: 0;">{doc_stats.get('total_pages', 0)}</p>
                        <p style="color: #666; margin: 0;">Páginas</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #f093fb; margin: 0;">🧩</h3>
                        <p style="font-size: 1.5rem; font-weight: bold; margin: 0;">{doc_stats.get('fragments_count', 0)}</p>
                        <p style="color: #666; margin: 0;">Fragmentos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #27ae60; margin: 0;">📏</h3>
                        <p style="font-size: 1.5rem; font-weight: bold; margin: 0;">{doc_stats.get('text_length', 0):,}</p>
                        <p style="color: #666; margin: 0;">Caracteres</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Error procesando el archivo")
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def process_chat_query(question, max_results, similarity_threshold):
    """Procesa una consulta de chat y retorna la respuesta"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/chat",
            json={
                "question": question,
                "max_results": max_results,
                "similarity_threshold": similarity_threshold
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "role": "assistant",
                "content": result.get("answer", "No pude generar una respuesta."),
                "documents": result.get("relevant_documents", []),
                "confidence": result.get("confidence_score", 0),
                "llm_used": result.get("llm_used", "unknown")
            }
        else:
            return {
                "role": "assistant",
                "content": f"❌ Error del servidor: {response.status_code}",
                "documents": [],
                "confidence": 0,
                "llm_used": "error"
            }
            
    except requests.exceptions.Timeout:
        return {
            "role": "assistant", 
            "content": "⏰ La consulta está tomando más tiempo del esperado",
            "documents": [],
            "confidence": 0,
            "llm_used": "timeout"
        }
    except Exception as e:
        return {
            "role": "assistant",
            "content": f"❌ Error: {str(e)}",
            "documents": [],
            "confidence": 0,
            "llm_used": "error"
        }

def generate_conversation_summary():
    """Genera un resumen de la conversación"""
    if not st.session_state.modern_chat_history:
        st.info("No hay conversación para resumir")
        return
    
    # Combinar todas las preguntas y respuestas
    chat_text = "\n\n".join([
        f"{'Usuario' if msg['role'] == 'user' else 'IA'}: {msg['content']}"
        for msg in st.session_state.modern_chat_history
    ])
    
    st.markdown("### 📄 Resumen de la Conversación")
    st.text_area("", chat_text, height=300, key="conversation_summary")

def export_chat_history():
    """Exporta el historial de chat"""
    if not st.session_state.modern_chat_history:
        st.info("No hay conversación para exportar")
        return
    
    # Crear archivo de exportación
    chat_export = {
        "timestamp": str(st.session_state.get('chat_timestamp', '')),
        "messages": st.session_state.modern_chat_history,
        "total_messages": len(st.session_state.modern_chat_history)
    }
    
    st.download_button(
        label="⬇️ Descargar Conversación",
        data=json.dumps(chat_export, indent=2, ensure_ascii=False),
        file_name=f"conversacion_{len(st.session_state.modern_chat_history)}_mensajes.json",
        mime="application/json"
    )

def modern_documents_page():
    """Página moderna para gestión de documentos"""
    st.markdown('<div class="chat-container fade-in">', unsafe_allow_html=True)
    
    st.markdown("### 📚 Gestión de Documentos")
    
    # Obtener documentos
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/documents", timeout=10)
        if response.status_code == 200:
            docs_data = response.json()
            if docs_data.get('success', False):
                documents = docs_data.get('documents', [])
                
                # Estadísticas generales con cards modernas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #667eea; margin: 0;">📄</h3>
                        <p style="font-size: 2rem; font-weight: bold; margin: 0;">{len(documents)}</p>
                        <p style="color: #666; margin: 0;">Documentos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    total_fragments = docs_data.get('total_fragments', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #f093fb; margin: 0;">🧩</h3>
                        <p style="font-size: 2rem; font-weight: bold; margin: 0;">{total_fragments}</p>
                        <p style="color: #666; margin: 0;">Fragmentos</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_fragments = round(total_fragments / len(documents), 1) if documents else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="color: #27ae60; margin: 0;">📊</h3>
                        <p style="font-size: 2rem; font-weight: bold; margin: 0;">{avg_fragments}</p>
                        <p style="color: #666; margin: 0;">Promedio</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Lista de documentos con diseño moderno
                if documents:
                    for i, doc in enumerate(documents):
                        st.markdown(f"""
                        <div class="doc-card">
                            <h4 style="color: #667eea; margin: 0 0 0.5rem 0;">📄 {doc.get('filename', 'Sin nombre')}</h4>
                            <p style="color: #666; margin: 0.2rem 0;"><strong>Páginas:</strong> {doc.get('total_pages', 0)} | <strong>Fragmentos:</strong> {doc.get('fragment_count', 0)}</p>
                            <p style="color: #888; font-size: 0.9rem; margin: 0.5rem 0;">{doc.get('content_preview', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botones de acción
                        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
                        
                        with col_action1:
                            if st.button("🔍 Ver", key=f"view_{i}", use_container_width=True):
                                st.session_state[f'view_doc_{i}'] = True
                        
                        with col_action2:
                            if st.button("📝 Resumir", key=f"summarize_{i}", use_container_width=True):
                                st.info("🚧 Función en desarrollo")
                        
                        with col_action3:
                            if st.button("🔍 Buscar", key=f"search_{i}", use_container_width=True):
                                st.info("🚧 Función en desarrollo")
                        
                        with col_action4:
                            if st.button("🗑️ Eliminar", key=f"delete_{i}", use_container_width=True):
                                st.session_state[f'delete_doc_{i}'] = True
                        
                        # Manejo de eliminación
                        if st.session_state.get(f'delete_doc_{i}', False):
                            st.warning(f"⚠️ ¿Eliminar '{doc.get('filename', '')}'?")
                            
                            col_confirm1, col_confirm2 = st.columns(2)
                            
                            with col_confirm1:
                                if st.button("✅ Confirmar", key=f"confirm_{i}"):
                                    delete_document(doc.get('filename', ''), i)
                            
                            with col_confirm2:
                                if st.button("❌ Cancelar", key=f"cancel_{i}"):
                                    st.session_state[f'delete_doc_{i}'] = False
                                    st.rerun()
                        
                        st.markdown("---")
                    
                    # Botón de limpieza general
                    st.markdown("### 🛠️ Administración")
                    
                    col_admin1, col_admin2 = st.columns(2)
                    
                    with col_admin1:
                        if st.button("🗑️ Limpiar Todo", type="secondary", use_container_width=True):
                            st.session_state['confirm_clear_all'] = True
                    
                    with col_admin2:
                        if st.button("🔄 Actualizar", use_container_width=True):
                            st.rerun()
                    
                    # Confirmación de limpieza total
                    if st.session_state.get('confirm_clear_all', False):
                        st.error("⚠️ **ATENCIÓN**: Esta acción eliminará TODOS los documentos")
                        
                        col_final1, col_final2 = st.columns(2)
                        
                        with col_final1:
                            if st.button("💀 SÍ, ELIMINAR TODO"):
                                clear_all_documents()
                        
                        with col_final2:
                            if st.button("❌ Cancelar operación"):
                                st.session_state['confirm_clear_all'] = False
                                st.rerun()
                
                else:
                    st.markdown("""
                    <div class="upload-area">
                        <h3 style="color: #667eea;">📭 No hay documentos</h3>
                        <p>Ve a la pestaña "💬 Chat Inteligente" para subir tu primer documento</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Error obteniendo documentos")
        else:
            st.error("❌ Error de conexión")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def delete_document(filename, index):
    """Elimina un documento específico"""
    try:
        with st.spinner(f"🗑️ Eliminando '{filename}'..."):
            response = requests.delete(f"{API_BASE_URL}/api/chat/documents/{filename}", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    st.success(f"✅ Documento '{filename}' eliminado")
                    st.session_state[f'delete_doc_{index}'] = False
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")
            else:
                st.error(f"❌ Error del servidor: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def clear_all_documents():
    """Elimina todos los documentos"""
    try:
        with st.spinner("🗑️ Eliminando todos los documentos..."):
            response = requests.delete(f"{API_BASE_URL}/api/chat/documents", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    st.success("✅ Todos los documentos eliminados")
                    st.session_state['confirm_clear_all'] = False
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error')}")
            else:
                st.error(f"❌ Error del servidor: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def modern_analysis_page():
    """Página moderna de análisis avanzado"""
    st.markdown("### 🔬 Análisis Avanzado")
    
    # Tabs para diferentes tipos de análisis
    tab1, tab2, tab3 = st.tabs(["📝 Resúmenes", "🏷️ Clasificación", "⚖️ Comparaciones"])
    
    with tab1:
        st.markdown("#### 📝 Generación de Resúmenes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            summary_type = st.selectbox(
                "Tipo de resumen:",
                ["comprehensive", "executive", "technical", "bullet_points"],
                format_func=lambda x: {
                    "comprehensive": "📊 Completo",
                    "executive": "💼 Ejecutivo",
                    "technical": "🔧 Técnico", 
                    "bullet_points": "📋 Puntos Clave"
                }.get(x, x)
            )
        
        with col2:
            max_tokens = st.slider("Longitud:", 200, 1500, 800, 100)
        
        if st.button("📝 Generar Resumen", type="primary", use_container_width=True):
            st.info("🚧 Función en desarrollo - Próximamente disponible")
    
    with tab2:
        st.markdown("#### 🏷️ Clasificación de Temas")
        
        st.info("🚧 Clasificación automática de documentos - En desarrollo")
    
    with tab3:
        st.markdown("#### ⚖️ Análisis Comparativo")
        
        st.info("🚧 Comparación de documentos - En desarrollo")

def main_page():
    """Página principal: Upload + Chat integrado"""
    
    # Layout en dos columnas
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📤 Subir Documentos")
        
        # Upload simplificado
        uploaded_file = st.file_uploader(
            "Arrastra tu PDF aquí",
            type=['pdf'],
            help="Máximo 50MB por archivo"
        )
        
        if uploaded_file is not None:
            st.success(f"📄 {uploaded_file.name}")
            st.caption(f"📊 {uploaded_file.size / 1024:.1f} KB")
            
            # Procesar automáticamente cuando se sube un archivo
            if f"processed_{uploaded_file.name}" not in st.session_state:
                with st.spinner("🚀 Procesando automáticamente..."):
                    result = send_document_to_api(uploaded_file)
                    
                    if result:
                        st.success("✅ Procesado automáticamente!")
                        st.session_state[f"processed_{uploaded_file.name}"] = True
                        
                        # Estadísticas compactas
                        doc_stats = result.get('document_stats', {})
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("📄", doc_stats.get('total_pages', 0))
                        with col_b:
                            st.metric("🧩", doc_stats.get('fragments_count', 0))
                    else:
                        st.error("❌ Error procesando el archivo")
            else:
                st.info("✅ Ya procesado - Listo para chat")
        
        # Estado del sistema compacto
        st.divider()
        try:
            status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=3)
            if status_response.status_code == 200:
                status_data = status_response.json()
                llm_status = status_data.get("llm_service", {})
                vector_status = status_data.get("vector_database", {})
                
                if llm_status.get("ollama_connected", False):
                    st.success("🤖 IA Local Activa")
                else:
                    st.warning("🤖 IA Local: Desconectada")
                
                if vector_status.get("connected", False):
                    chunks = vector_status.get("total_chunks", 0)
                    st.info(f"🗄️ {chunks} fragmentos en BD")
                else:
                    st.error("❌ Base de datos desconectada")
            else:
                st.error("❌ Backend no disponible")
        except:
            st.error("❌ Error de conexión")
    
    with col2:
        st.subheader("💬 Chat Conversacional")
        
        # Configuración del chat
        with st.expander("⚙️ Configuración", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                max_results = st.slider("Documentos relevantes:", 1, 10, 7, key="chat_max_results")
            with col_b:
                similarity_threshold = st.slider("Umbral similaridad:", 0.1, 1.0, 0.3, 0.1, key="chat_similarity")
        
        # Área de chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Mostrar historial
        chat_container = st.container()
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f"**🙋‍♂️ Tú:** {message['content']}")
                else:
                    st.markdown(f"**🤖 IA:** {message['content']}")
                    
                    # Mostrar documentos relevantes de forma compacta
                    if message.get("documents"):
                        with st.expander(f"📚 {len(message['documents'])} documentos consultados", expanded=False):
                            for doc in message["documents"][:3]:  # Máximo 3
                                st.caption(f"📄 {doc.get('filename', 'Sin nombre')} (similaridad: {doc.get('similarity_score', 0):.2f})")
                st.divider()
        
        # Input de chat
        user_question = st.text_input(
            "Escribe tu pregunta:",
            placeholder="¿Qué quieres saber sobre tus documentos?",
            key="chat_input"
        )
        
        col_send, col_clear = st.columns([3, 1])
        
        with col_send:
            if st.button("📤 Enviar", type="primary", use_container_width=True, key="main_send_chat") and user_question:
                process_chat_message(user_question, max_results, similarity_threshold)
        
        with col_clear:
            if st.button("🗑️ Limpiar", use_container_width=True, key="main_clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

def process_chat_message(question: str, max_results: int, similarity_threshold: float):
    """Procesa un mensaje de chat"""
    try:
        # Agregar pregunta del usuario al historial
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        # Hacer request al backend
        with st.spinner("🤔 Pensando..."):
            response = requests.post(
                f"{API_BASE_URL}/api/chat/chat",
                json={
                    "question": question,
                    "max_results": max_results,
                    "similarity_threshold": similarity_threshold
                },
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Agregar respuesta de la IA al historial
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("answer", "No pude generar una respuesta."),
                "documents": result.get("relevant_documents", []),
                "confidence": result.get("confidence_score", 0),
                "llm_used": result.get("llm_used", "unknown")
            })
        else:
            st.error(f"Error del servidor: {response.status_code}")
            
    except requests.exceptions.Timeout:
        st.error("⏰ La consulta está tomando más tiempo del esperado")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Error de conexión con el backend")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    # Refrescar la página para mostrar la nueva conversación
    st.rerun()

def documents_page():
    """Página para visualizar documentos procesados"""
    st.subheader("📄 Documentos Procesados")
    
    # Botón para refrescar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Visualiza todos los documentos que están en el sistema**")
    with col2:
        refresh_button = st.button("🔄 Refrescar", key="refresh_docs")
    
    if refresh_button:
        # Limpiar caché si existe
        if 'documents_data' in st.session_state:
            del st.session_state['documents_data']
    
    # Obtener lista de documentos
    if 'documents_data' not in st.session_state or refresh_button:
        with st.spinner("📚 Cargando documentos..."):
            try:
                response = requests.get(f"{API_BASE_URL}/api/chat/documents", timeout=10)
                
                if response.status_code == 200:
                    st.session_state['documents_data'] = response.json()
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    return
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 Error de conexión con el backend")
                return
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return
    
    # Mostrar información general
    docs_data = st.session_state.get('documents_data', {})
    
    if docs_data.get('success', False):
        documents = docs_data.get('documents', [])
        total_docs = docs_data.get('total_documents', 0)
        total_fragments = docs_data.get('total_fragments', 0)
        
        # Estadísticas generales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Total Documentos", total_docs)
        with col2:
            st.metric("🧩 Total Fragmentos", total_fragments)
        with col3:
            avg_fragments = round(total_fragments / total_docs, 1) if total_docs > 0 else 0
            st.metric("📊 Promedio Fragmentos", avg_fragments)
        
        if documents:
            st.divider()
            
            # Ordenar documentos por fecha de subida (más recientes primero)
            try:
                documents_sorted = sorted(documents, 
                                        key=lambda x: x.get('upload_date', ''), 
                                        reverse=True)
            except:
                documents_sorted = documents
            
            # Mostrar cada documento
            for i, doc in enumerate(documents_sorted):
                with st.expander(f"📄 {doc.get('filename', 'Sin nombre')}", expanded=False):
                    
                    # Información básica del documento
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📅 Fecha de subida:** {doc.get('upload_date', 'No disponible')}")
                        st.write(f"**📏 Tamaño:** {doc.get('file_size', 0):,} bytes")
                        st.write(f"**📑 Páginas:** {doc.get('total_pages', 0)}")
                    
                    with col2:
                        st.write(f"**🧩 Fragmentos:** {doc.get('fragment_count', 0)}")
                        
                        # Calcular densidad de fragmentos
                        pages = doc.get('total_pages', 1)
                        fragments = doc.get('fragment_count', 0)
                        density = round(fragments / pages, 1) if pages > 0 else 0
                        st.write(f"**📊 Fragmentos/página:** {density}")
                    
                    # Vista previa del contenido
                    content_preview = doc.get('content_preview', '')
                    if content_preview:
                        st.markdown("**👀 Vista previa del contenido:**")
                        st.text_area(
                            "",
                            content_preview,
                            height=120,
                            disabled=True,
                            key=f"preview_{i}"
                        )
                    
                    # Acciones del documento
                    col_actions = st.columns(3)
                    
                    with col_actions[0]:
                        if st.button(f"🔍 Buscar en documento", key=f"search_{i}"):
                            st.session_state[f'search_doc_{i}'] = True
                    
                    with col_actions[1]:
                        if st.button(f"📝 Resumir documento", key=f"summarize_{i}"):
                            st.session_state[f'summarize_doc_{i}'] = True
                    
                    with col_actions[2]:
                        if st.button(f"❌ Eliminar", key=f"delete_{i}"):
                            st.session_state[f'delete_doc_{i}'] = True
                    
                    # Manejo de acciones
                    if st.session_state.get(f'search_doc_{i}', False):
                        st.info("🚧 Función de búsqueda en documento específico en desarrollo")
                        st.session_state[f'search_doc_{i}'] = False
                    
                    if st.session_state.get(f'summarize_doc_{i}', False):
                        st.info("🚧 Función de resumen de documento específico en desarrollo")
                        st.session_state[f'summarize_doc_{i}'] = False
                    
                    if st.session_state.get(f'delete_doc_{i}', False):
                        # Implementar eliminación real
                        filename = doc.get('filename', '')
                        
                        # Confirmación de eliminación
                        st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar '{filename}'?")
                        
                        col_confirm = st.columns(2)
                        with col_confirm[0]:
                            if st.button(f"✅ Sí, eliminar", key=f"confirm_delete_{i}"):
                                # Ejecutar eliminación
                                with st.spinner(f"🗑️ Eliminando '{filename}'..."):
                                    try:
                                        response = requests.delete(
                                            f"{API_BASE_URL}/api/chat/documents/{filename}",
                                            timeout=30
                                        )
                                        
                                        if response.status_code == 200:
                                            result = response.json()
                                            if result.get('success', False):
                                                st.success(f"✅ Documento '{filename}' eliminado exitosamente")
                                                # Limpiar caché para refrescar
                                                if 'documents_data' in st.session_state:
                                                    del st.session_state['documents_data']
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                                        else:
                                            st.error(f"❌ Error del servidor: {response.status_code}")
                                            
                                    except requests.exceptions.ConnectionError:
                                        st.error("🔌 Error de conexión con el backend")
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                                
                                st.session_state[f'delete_doc_{i}'] = False
                        
                        with col_confirm[1]:
                            if st.button(f"❌ Cancelar", key=f"cancel_delete_{i}"):
                                st.session_state[f'delete_doc_{i}'] = False
                                st.rerun()
            
            # Información adicional
            st.divider()
            
            # Acciones de administración
            st.subheader("🛠️ Administración de Base de Datos")
            
            col_admin = st.columns(3)
            
            with col_admin[0]:
                if st.button("🗑️ Limpiar todo", type="secondary", help="Elimina TODOS los documentos"):
                    st.session_state['show_clear_all_confirm'] = True
            
            with col_admin[1]:
                if st.button("📊 Ver fragmentos", help="Ver fragmentos detallados"):
                    st.session_state['show_fragments_view'] = True
            
            with col_admin[2]:
                if st.button("🔄 Reconstruir índice", help="Reconstruir índice de búsqueda"):
                    st.info("🚧 Función en desarrollo")
            
            # Confirmación para limpiar todo
            if st.session_state.get('show_clear_all_confirm', False):
                st.warning("⚠️ **ATENCIÓN**: Esta acción eliminará TODOS los documentos y fragmentos.")
                st.markdown("**Esta acción NO se puede deshacer.**")
                
                col_clear_confirm = st.columns(2)
                with col_clear_confirm[0]:
                    if st.button("💀 SÍ, ELIMINAR TODO", type="primary"):
                        with st.spinner("🗑️ Eliminando todos los documentos..."):
                            try:
                                response = requests.delete(
                                    f"{API_BASE_URL}/api/chat/documents",
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    if result.get('success', False):
                                        st.success(f"✅ {result.get('message', 'Todos los documentos eliminados')}")
                                        st.info(f"🗑️ Fragmentos eliminados: {result.get('fragments_deleted', 0)}")
                                        # Limpiar caché
                                        if 'documents_data' in st.session_state:
                                            del st.session_state['documents_data']
                                        st.session_state['show_clear_all_confirm'] = False
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                                else:
                                    st.error(f"❌ Error del servidor: {response.status_code}")
                                    
                            except requests.exceptions.ConnectionError:
                                st.error("🔌 Error de conexión con el backend")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                with col_clear_confirm[1]:
                    if st.button("❌ Cancelar"):
                        st.session_state['show_clear_all_confirm'] = False
                        st.rerun()
            
            # Vista de fragmentos detallada
            if st.session_state.get('show_fragments_view', False):
                st.markdown("### 🧩 Vista detallada de fragmentos")
                
                # Selector de documento para ver fragmentos
                document_names = [doc.get('filename', '') for doc in documents if doc.get('filename')]
                if document_names:
                    selected_doc = st.selectbox(
                        "Selecciona un documento para ver sus fragmentos:",
                        document_names,
                        key="fragment_view_selector"
                    )
                    
                    if st.button("🔍 Ver fragmentos"):
                        with st.spinner(f"📚 Cargando fragmentos de '{selected_doc}'..."):
                            try:
                                response = requests.get(
                                    f"{API_BASE_URL}/api/chat/documents/{selected_doc}/fragments",
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    if result.get('success', False):
                                        fragments = result.get('fragments', [])
                                        total_fragments = result.get('total_fragments', 0)
                                        
                                        st.success(f"📊 {total_fragments} fragmentos encontrados en '{selected_doc}'")
                                        
                                        for j, fragment in enumerate(fragments):
                                            with st.expander(f"Fragmento {j+1} (ID: {fragment.get('id', 'N/A')[:8]}...)", expanded=False):
                                                st.write(f"**Longitud:** {fragment.get('content_length', 0)} caracteres")
                                                st.text_area(
                                                    "Contenido:",
                                                    fragment.get('content_preview', ''),
                                                    height=100,
                                                    disabled=True,
                                                    key=f"fragment_content_{j}"
                                                )
                                                
                                                # Metadatos del fragmento
                                                metadata = fragment.get('metadata', {})
                                                if metadata:
                                                    st.json(metadata)
                                                
                                                # Botón para eliminar fragmento individual
                                                if st.button(f"🗑️ Eliminar fragmento", key=f"delete_fragment_{j}"):
                                                    fragment_id = fragment.get('id')
                                                    if fragment_id:
                                                        with st.spinner("Eliminando fragmento..."):
                                                            try:
                                                                del_response = requests.delete(
                                                                    f"{API_BASE_URL}/api/chat/fragments",
                                                                    json=[fragment_id],
                                                                    timeout=30
                                                                )
                                                                
                                                                if del_response.status_code == 200:
                                                                    del_result = del_response.json()
                                                                    if del_result.get('success', False):
                                                                        st.success("✅ Fragmento eliminado")
                                                                        st.rerun()
                                                                    else:
                                                                        st.error(f"❌ Error: {del_result.get('error')}")
                                                                else:
                                                                    st.error(f"❌ Error del servidor: {del_response.status_code}")
                                                            except Exception as e:
                                                                st.error(f"❌ Error: {str(e)}")
                                    else:
                                        st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                                else:
                                    st.error(f"❌ Error del servidor: {response.status_code}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                if st.button("❌ Cerrar vista de fragmentos"):
                    st.session_state['show_fragments_view'] = False
                    st.rerun()
            
            with st.expander("ℹ️ Información del Sistema"):
                db_status = docs_data.get('database_status', {})
                st.json(db_status)
                
        else:
            st.info("📭 No hay documentos procesados en el sistema.")
            st.markdown("**Para agregar documentos:**")
            st.markdown("1. Ve a la página '💬 Chat & Upload'")
            st.markdown("2. Sube un archivo PDF")
            st.markdown("3. El documento se procesará automáticamente")
            
    else:
        st.error(f"❌ Error obteniendo documentos: {docs_data.get('error', 'Error desconocido')}")

def advanced_analysis_page():
    """Página de análisis avanzado"""
    st.subheader("🔬 Análisis Avanzado de Documentos")
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3 = st.tabs(["📝 Resumen", "🏷️ Clasificación", "⚖️ Comparación"])
    
    with tab1:
        st.markdown("**Genera resúmenes especializados**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            summary_type = st.selectbox(
                "Tipo de resumen:",
                ["comprehensive", "executive", "technical", "bullet_points"],
                format_func=lambda x: {
                    "comprehensive": "📊 Completo",
                    "executive": "💼 Ejecutivo", 
                    "technical": "🔧 Técnico",
                    "bullet_points": "📋 Puntos Clave"
                }.get(x, x),
                key="advanced_summary_type"
            )
        
        with col2:
            max_tokens = st.slider("Longitud:", 200, 1500, 800, 100, key="advanced_max_tokens")
        
        if st.button("📝 Generar Resumen", type="primary", key="advanced_generate_summary"):
            with st.spinner("Generando resumen..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat/summarize/advanced",
                        json={
                            "summary_type": summary_type,
                            "max_tokens": max_tokens
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success("✅ Resumen generado!")
                            
                            # Métricas
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("📄 Docs", result.get("documents_processed", 0))
                            with col_b:
                                st.metric("🔤 Tokens", result.get("tokens_used", 0))
                            with col_c:
                                st.metric("🤖", result.get("method", "").replace("_", " ").title())
                            
                            # Resumen
                            st.markdown("**Resumen:**")
                            st.text_area("", result.get("summary", ""), height=300, disabled=True, key="advanced_summary_text")
                            
                            # Descarga
                            st.download_button(
                                "💾 Descargar",
                                result.get("summary", ""),
                                f"resumen_{summary_type}.txt",
                                "text/plain"
                            )
                        else:
                            st.error(f"❌ {result.get('error', 'Error desconocido')}")
                    else:
                        st.error(f"❌ Error del servidor: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown("**Clasifica documentos por temas**")
        
        # Configuración
        col1, col2 = st.columns(2)
        
        with col1:
            use_custom = st.checkbox("Etiquetas personalizadas", key="advanced_custom_labels")
            if use_custom:
                custom_labels = st.text_input(
                    "Etiquetas (separadas por comas):",
                    "tecnología, ciencia, negocios, salud, educación"
                )
                labels = [l.strip() for l in custom_labels.split(",") if l.strip()]
            else:
                labels = None
        
        with col2:
            confidence_threshold = st.slider("Confianza mínima:", 0.1, 0.9, 0.3, 0.1, key="classification_confidence")
        
        if st.button("🏷️ Clasificar", type="primary", key="advanced_classify_docs"):
            with st.spinner("Clasificando documentos..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat/classify/topics",
                        json={
                            "custom_labels": labels,
                            "confidence_threshold": confidence_threshold
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success("✅ Clasificación completada!")
                            
                            # Estadísticas
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("📄 Documentos", result.get("total_documents", 0))
                            with col_b:
                                st.metric("🏷️ Temas", len([t for t in result.get("topic_statistics", {}).values() if t > 0]))
                            
                            # Distribución
                            topic_stats = result.get("topic_statistics", {})
                            if topic_stats:
                                st.markdown("**Distribución de temas:**")
                                for topic, count in sorted(topic_stats.items(), key=lambda x: x[1], reverse=True):
                                    if count > 0:
                                        percentage = (count / result.get("total_documents", 1)) * 100
                                        st.write(f"**{topic.title()}**: {count} docs ({percentage:.1f}%)")
                        else:
                            st.error(f"❌ {result.get('error', 'Error desconocido')}")
                    else:
                        st.error(f"❌ Error del servidor: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.markdown("**Compara conjuntos de documentos**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            query1 = st.text_input("Consulta 1:", placeholder="ej: ventajas del enfoque A", key="advanced_query1")
        
        with col2:
            query2 = st.text_input("Consulta 2:", placeholder="ej: ventajas del enfoque B", key="advanced_query2")
        
        if st.button("⚖️ Comparar", type="primary", key="advanced_compare_docs") and query1 and query2:
            with st.spinner("Comparando documentos..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat/summarize/comparative",
                        json={
                            "doc1_query": query1,
                            "doc2_query": query2,
                            "max_results": 3
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success("✅ Comparación completada!")
                            
                            # Estadísticas
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("📄 Grupo 1", result.get("doc1_fragments", 0))
                            with col_b:
                                st.metric("📄 Grupo 2", result.get("doc2_fragments", 0))
                            
                            # Comparación
                            st.markdown("**Análisis comparativo:**")
                            st.text_area("", result.get("comparative_summary", ""), height=300, disabled=True, key="advanced_comparison_text")
                        else:
                            st.error(f"❌ {result.get('error', 'Error desconocido')}")
                    else:
                        st.error(f"❌ Error del servidor: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def upload_page():
    """Página para subir archivos PDF"""
    st.header("📤 Subir Documentos PDF")
    
    # Mostrar información sobre el procesamiento
    with st.expander("ℹ️ ¿Cómo funciona el procesamiento?"):
        st.markdown("""
        1. **Extracción de texto**: Se extrae todo el texto del PDF usando PyMuPDF
        2. **División en fragmentos**: El texto se divide en chunks de ~1000 caracteres
        3. **Generación de embeddings**: Cada chunk se convierte en un vector usando IA
        4. **Almacenamiento**: Los vectores se guardan en ChromaDB para búsquedas rápidas
        """)
    
    # Subida de archivo
    uploaded_file = st.file_uploader(
        "Selecciona un archivo PDF",
        type=['pdf'],
        help="Solo se permiten archivos PDF"
    )
    
    if uploaded_file is not None:
        # Mostrar información del archivo
        st.success(f"📄 Archivo seleccionado: {uploaded_file.name}")
        st.info(f"📊 Tamaño: {uploaded_file.size / 1024:.2f} KB")
        
        # Botón para procesar
        if st.button("🚀 Procesar Documento", type="primary"):
            with st.spinner("Procesando documento... Esto puede tomar unos momentos."):
                processing_result = send_document_to_api(uploaded_file)
                
                if processing_result:
                    st.success("✅ ¡Documento procesado exitosamente!")
                    
                    # Mostrar estadísticas del procesamiento en columnas
                    col1, col2, col3 = st.columns(3)
                    
                    doc_stats = processing_result.get('document_stats', {})
                    with col1:
                        st.metric("📄 Páginas", doc_stats.get('total_pages', 0))
                        st.metric("📝 Caracteres", doc_stats.get('text_length', 0))
                    
                    with col2:
                        st.metric("🧩 Fragmentos", doc_stats.get('fragments_count', 0))
                        st.metric("🔢 Embeddings", doc_stats.get('embeddings_count', 0))
                    
                    with col3:
                        transformer_info = processing_result.get('model_info', {})
                        st.metric("📐 Dimensión", doc_stats.get('vector_dimension', 0))
                        st.metric("🤖 Modelo", transformer_info.get('model_name', 'N/A').split('/')[-1])
                    
                    # Mostrar metadatos del documento
                    with st.expander("📋 Metadatos del Documento"):
                        doc_metadata = processing_result.get('document_metadata', {})
                        if doc_metadata.get('title'):
                            st.write(f"**Título:** {doc_metadata.get('title')}")
                        if doc_metadata.get('author'):
                            st.write(f"**Autor:** {doc_metadata.get('author')}")
                        if doc_metadata.get('subject'):
                            st.write(f"**Tema:** {doc_metadata.get('subject')}")
                        if doc_metadata.get('creator'):
                            st.write(f"**Creador:** {doc_metadata.get('creator')}")
                    
                    # Mostrar vista previa de fragmentos
                    with st.expander("👀 Vista Previa de Fragmentos"):
                        sample_fragments = processing_result.get('sample_fragments', [])
                        for index, fragment in enumerate(sample_fragments[:3]):
                            st.write(f"**Fragmento {index+1}:**")
                            st.text_area(f"fragment_{index}", fragment, height=100, disabled=True, key=f"fragment_text_{index}")
                    
                    # Información de la base de datos vectorial
                    with st.expander("🗄️ Estado de la Base de Datos"):
                        db_status = processing_result.get('database_status', {})
                        st.json(db_status)

def chat_page():
    """Página para chat con documentos"""
    st.header("💬 Chat con Documentos")
    
    # Verificar estado del sistema
    try:
        status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            llm_status = status_data.get("llm_service", {})
            
            # Mostrar estado del sistema
            col1, col2, col3 = st.columns(3)
            with col1:
                if llm_status.get("ollama_connected", False):
                    st.success("🤖 Ollama Conectado")
                else:
                    st.error("❌ Ollama Desconectado")
            
            with col2:
                if llm_status.get("langchain_available", False):
                    st.success("🔗 LangChain Activo")
                else:
                    st.warning("⚠️ LangChain No Disponible")
            
            with col3:
                vector_db = status_data.get("vector_database", {})
                total_chunks = vector_db.get("total_chunks", 0)
                st.info(f"📚 {total_chunks} fragmentos disponibles")
        else:
            st.error("❌ No se puede conectar al sistema de chat")
            return
    except Exception as e:
        st.error(f"❌ Error verificando estado: {str(e)}")
        return
    
    # Inicializar historial de chat en session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    
    # Configuración del chat
    st.subheader("⚙️ Configuración")
    col1, col2 = st.columns(2)
    
    with col1:
        max_results = st.slider(
            "� Máximo de fragmentos relevantes:", 
            min_value=1, max_value=10, value=5,
            help="Número máximo de fragmentos de documentos a considerar"
        )
    
    with col2:
        similarity_threshold = st.slider(
            "🎯 Umbral de similitud:", 
            min_value=0.0, max_value=1.0, value=0.5, step=0.1,
            help="Umbral mínimo de similitud para considerar un fragmento relevante"
        )
    
    # Área de chat
    st.subheader("💬 Conversación")
    
    # Mostrar historial de chat
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Mostrar metadatos si están disponibles
                    if "metadata" in message:
                        metadata = message["metadata"]
                        with st.expander("📊 Detalles de la respuesta"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Método:** {metadata.get('method', 'N/A')}")
                                st.write(f"**Fragmentos usados:** {metadata.get('relevant_documents', 0)}")
                            with col2:
                                if metadata.get('langchain_used'):
                                    st.success("🔗 LangChain utilizado")
                                else:
                                    st.info("🤖 Ollama directo")
    
    # Campo de entrada para nueva pregunta
    st.subheader("✍️ Haz tu pregunta")
    
    # Usar form para mejor UX
    with st.form(key=f"chat_form_{st.session_state.chat_input_key}", clear_on_submit=True):
        user_question = st.text_area(
            "Pregunta:",
            placeholder="Ej: ¿Cuáles son los puntos principales del documento?",
            height=100,
            help="Escribe tu pregunta sobre los documentos subidos"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_button = st.form_submit_button("🚀 Enviar", type="primary")
        with col2:
            clear_button = st.form_submit_button("🗑️ Limpiar Chat")
    
    # Procesar envío de pregunta
    if submit_button and user_question.strip():
        # Agregar pregunta del usuario al historial
        st.session_state.chat_history.append({
            "role": "user", 
            "content": user_question
        })
        
        # Mostrar la pregunta inmediatamente
        with chat_container:
            st.chat_message("user").write(user_question)
        
        # Enviar pregunta al backend
        with st.spinner("🤔 Generando respuesta..."):
            try:
                chat_request = {
                    "question": user_question,
                    "max_results": max_results,
                    "similarity_threshold": similarity_threshold
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/chat/simple",
                    json=chat_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    chat_response = response.json()
                    
                    if "error" in chat_response:
                        answer = f"❌ Error: {chat_response['error']}"
                        metadata = {"method": "error", "relevant_documents": 0}
                    else:
                        answer = chat_response.get("response", "No se recibió respuesta")
                        metadata = {
                            "method": chat_response.get("method", "unknown"),
                            "relevant_documents": chat_response.get("relevant_documents", 0),
                            "langchain_used": chat_response.get("langchain_used", False)
                        }
                    
                    # Agregar respuesta al historial
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "metadata": metadata
                    })
                    
                    # Mostrar respuesta inmediatamente
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.write(answer)
                            
                            with st.expander("📊 Detalles de la respuesta"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Método:** {metadata.get('method', 'N/A')}")
                                    st.write(f"**Fragmentos usados:** {metadata.get('relevant_documents', 0)}")
                                with col2:
                                    if metadata.get('langchain_used'):
                                        st.success("🔗 LangChain utilizado")
                                    else:
                                        st.info("🤖 Ollama directo")
                else:
                    error_msg = f"❌ Error del servidor: {response.status_code}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {"method": "error", "relevant_documents": 0}
                    })
                    
                    with chat_container:
                        st.chat_message("assistant").write(error_msg)
                        
            except requests.exceptions.Timeout:
                timeout_msg = "⏱️ Tiempo de espera agotado. El modelo puede estar procesando una consulta compleja."
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": timeout_msg,
                    "metadata": {"method": "timeout", "relevant_documents": 0}
                })
                
                with chat_container:
                    st.chat_message("assistant").write(timeout_msg)
                    
            except Exception as e:
                error_msg = f"❌ Error inesperado: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "metadata": {"method": "error", "relevant_documents": 0}
                })
                
                with chat_container:
                    st.chat_message("assistant").write(error_msg)
        
        # Incrementar key para limpiar el form
        st.session_state.chat_input_key += 1
        st.rerun()
    
    # Procesar limpieza de chat
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.chat_input_key += 1
        st.success("🗑️ Chat limpiado exitosamente")
        st.rerun()
    
    # Botones adicionales
    st.subheader("🛠️ Acciones Adicionales")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generar Resumen de Chat"):
            if st.session_state.chat_history:
                # Combinar todas las preguntas y respuestas
                chat_text = "\n\n".join([
                    f"{'Usuario' if msg['role'] == 'user' else 'Asistente'}: {msg['content']}"
                    for msg in st.session_state.chat_history
                ])
                
                st.text_area("📄 Resumen de la conversación:", chat_text, height=200, key="chat_summary_text")
            else:
                st.info("No hay conversación para resumir")
    
    with col2:
        if st.button("💾 Descargar Chat"):
            if st.session_state.chat_history:
                # Crear archivo de descarga
                chat_export = {
                    "timestamp": str(st.timestamp if hasattr(st, 'timestamp') else ""),
                    "messages": st.session_state.chat_history
                }
                
                st.download_button(
                    label="⬇️ Descargar JSON",
                    data=json.dumps(chat_export, indent=2, ensure_ascii=False),
                    file_name="chat_conversation.json",
                    mime="application/json"
                )
            else:
                st.info("No hay conversación para descargar")
    
    # Ayuda y ejemplos
    with st.expander("💡 Ejemplos de preguntas"):
        st.markdown("""
        **Preguntas de análisis:**
        - ¿Cuáles son los puntos principales del documento?
        - ¿Qué conclusiones presenta el autor?
        - ¿Hay datos estadísticos relevantes?
        
        **Preguntas específicas:**
        - ¿Qué dice sobre [tema específico]?
        - ¿Cuáles son las recomendaciones mencionadas?
        - ¿Hay fechas o números importantes?
        
        **Preguntas comparativas:**
        - ¿Cómo se relaciona esto con [concepto]?
        - ¿Cuáles son las ventajas y desventajas mencionadas?
        """)
    
    # Información técnica
    with st.expander("🔧 Información Técnica"):
        st.markdown(f"""
        **Configuración actual:**
        - Fragmentos máximos: {max_results}
        - Umbral de similitud: {similarity_threshold}
        - Mensajes en historial: {len(st.session_state.chat_history)}
        
        **Estado del sistema:**
        - Backend: {API_BASE_URL}
        - LLM: {"Ollama + LangChain" if llm_status.get("langchain_available") else "Ollama directo"}
        - Base vectorial: ChromaDB
        """)

def summary_page():
    """Página para generar resúmenes"""
    st.header("📄 Generar Resúmenes")
    
    # Verificar estado del sistema
    try:
        status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            vector_db = status_data.get("vector_database", {})
            total_chunks = vector_db.get("total_chunks", 0)
            
            if total_chunks == 0:
                st.warning("⚠️ No hay documentos cargados. Ve a 'Subir Documentos' primero.")
                return
            else:
                st.success(f"📚 {total_chunks} fragmentos de documentos disponibles")
        else:
            st.error("❌ No se puede conectar al sistema")
            return
    except Exception as e:
        st.error(f"❌ Error verificando estado: {str(e)}")
        return
    
    st.markdown("Genera resúmenes automáticos de tus documentos usando IA.")
    
    # Opciones de resumen
    st.subheader("⚙️ Configuración del Resumen")
    
    col1, col2 = st.columns(2)
    with col1:
        summary_type = st.selectbox(
            "Tipo de resumen:",
            ["Colección completa", "Documento específico"],
            help="Elige si quieres resumir todos los documentos o uno específico"
        )
    
    with col2:
        max_length = st.slider(
            "Longitud máxima:",
            min_value=100, max_value=1000, value=500,
            help="Número máximo de caracteres en el resumen"
        )
    
    # Generar resumen
    if st.button("📝 Generar Resumen", type="primary"):
        with st.spinner("🤖 Generando resumen..."):
            try:
                summary_request = {
                    "max_length": max_length
                }
                
                if summary_type == "Documento específico":
                    # TODO: Implementar selección de documento específico
                    st.info("🚧 Selección de documento específico en desarrollo")
                    return
                
                response = requests.post(
                    f"{API_BASE_URL}/api/summarize",
                    json=summary_request,
                    timeout=60
                )
                
                if response.status_code == 200:
                    summary_response = response.json()
                    
                    if summary_response.get("success", False):
                        st.success("✅ Resumen generado exitosamente")
                        
                        # Mostrar resumen
                        st.subheader("📋 Resumen Generado")
                        summary_text = summary_response.get("summary", "")
                        st.markdown(summary_text)
                        
                        # Mostrar estadísticas
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("📊 Documentos analizados", summary_response.get("documents_analyzed", 0))
                        with col2:
                            st.metric("🔧 Método usado", summary_response.get("method", "unknown"))
                        
                        # Opción de descarga
                        st.download_button(
                            label="⬇️ Descargar Resumen",
                            data=summary_text,
                            file_name="resumen_documentos.txt",
                            mime="text/plain"
                        )
                        
                    else:
                        st.error(f"❌ Error generando resumen: {summary_response.get('error', 'Error desconocido')}")
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Tiempo de espera agotado. El resumen puede estar tardando más de lo esperado.")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    
    # Información adicional
    with st.expander("💡 Tipos de resumen disponibles"):
        st.markdown("""
        **Resumen de colección completa:**
        - Analiza todos los documentos cargados
        - Identifica temas principales y patrones comunes
        - Proporciona una vista general de toda la información
        
        **Resumen de documento específico:**
        - Analiza un documento individual
        - Extrae puntos clave específicos del documento
        - Más detallado y enfocado
        """)
    
    with st.expander("🔧 Cómo funciona"):
        st.markdown("""
        1. **Selección de contenido**: Se seleccionan fragmentos representativos de los documentos
        2. **Análisis con IA**: El modelo de lenguaje analiza el contenido
        3. **Estructuración**: Se genera un resumen estructurado con:
           - Resumen ejecutivo
           - Puntos clave
           - Temas principales
           - Conclusiones relevantes
        """)

def comparison_page():
    """Página para comparar documentos"""
    st.header("⚖️ Comparar Documentos")
    
    # Verificar estado del sistema
    try:
        status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            vector_db = status_data.get("vector_database", {})
            total_chunks = vector_db.get("total_chunks", 0)
            
            if total_chunks == 0:
                st.warning("⚠️ No hay documentos cargados. Ve a 'Subir Documentos' primero.")
                return
            else:
                st.success(f"📚 {total_chunks} fragmentos de documentos disponibles")
        else:
            st.error("❌ No se puede conectar al sistema")
            return
    except Exception as e:
        st.error(f"❌ Error verificando estado: {str(e)}")
        return
    
    st.markdown("Compara diferentes aspectos o temas entre tus documentos usando IA.")
    
    # Configuración de comparación
    st.subheader("🔍 Configurar Comparación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Primer conjunto de documentos:**")
        query1 = st.text_area(
            "Describe qué buscar en el primer grupo:",
            placeholder="Ej: metodología de investigación, conclusiones sobre X tema",
            height=100,
            help="Describe el tema o aspecto que quieres encontrar en el primer grupo de documentos"
        )
    
    with col2:
        st.markdown("**📄 Segundo conjunto de documentos:**")
        query2 = st.text_area(
            "Describe qué buscar en el segundo grupo:",
            placeholder="Ej: resultados experimentales, recomendaciones sobre Y tema",
            height=100,
            help="Describe el tema o aspecto que quieres encontrar en el segundo grupo de documentos"
        )
    
    # Configuración adicional
    col1, col2 = st.columns(2)
    with col1:
        max_results = st.slider(
            "📊 Fragmentos por grupo:",
            min_value=1, max_value=5, value=3,
            help="Número máximo de fragmentos relevantes por cada grupo"
        )
    
    with col2:
        comparison_focus = st.selectbox(
            "🎯 Enfoque de comparación:",
            ["Similitudes y diferencias", "Solo similitudes", "Solo diferencias", "Análisis complementario"],
            help="Tipo de análisis comparativo a realizar"
        )
    
    # Generar comparación
    if st.button("⚖️ Generar Comparación", type="primary"):
        if not query1.strip() or not query2.strip():
            st.error("❌ Por favor, completa ambas descripciones de búsqueda")
            return
        
        with st.spinner("🤖 Analizando y comparando documentos..."):
            try:
                comparison_request = {
                    "doc1_query": query1,
                    "doc2_query": query2,
                    "max_results": max_results
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/compare",
                    json=comparison_request,
                    timeout=60
                )
                
                if response.status_code == 200:
                    comparison_response = response.json()
                    
                    if comparison_response.get("success", False):
                        st.success("✅ Comparación generada exitosamente")
                        
                        # Mostrar estadísticas de la búsqueda
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📄 Fragmentos Grupo 1", comparison_response.get("doc1_fragments", 0))
                        with col2:
                            st.metric("� Fragmentos Grupo 2", comparison_response.get("doc2_fragments", 0))
                        with col3:
                            st.metric("🔧 Método", comparison_response.get("method", "unknown"))
                        
                        # Mostrar consultas utilizadas
                        with st.expander("🔍 Consultas utilizadas"):
                            queries = comparison_response.get("queries", {})
                            st.write(f"**Grupo 1:** {queries.get('doc1_query', 'N/A')}")
                            st.write(f"**Grupo 2:** {queries.get('doc2_query', 'N/A')}")
                        
                        # Mostrar comparación
                        st.subheader("📊 Análisis Comparativo")
                        comparison_text = comparison_response.get("comparison", "")
                        st.markdown(comparison_text)
                        
                        # Opción de descarga
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="⬇️ Descargar Comparación",
                                data=comparison_text,
                                file_name="comparacion_documentos.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            # Descargar datos completos como JSON
                            comparison_data = {
                                "queries": queries,
                                "statistics": {
                                    "doc1_fragments": comparison_response.get("doc1_fragments", 0),
                                    "doc2_fragments": comparison_response.get("doc2_fragments", 0),
                                    "method": comparison_response.get("method", "unknown")
                                },
                                "comparison": comparison_text
                            }
                            
                            st.download_button(
                                label="📋 Descargar Datos JSON",
                                data=json.dumps(comparison_data, indent=2, ensure_ascii=False),
                                file_name="comparacion_completa.json",
                                mime="application/json"
                            )
                        
                    else:
                        st.error(f"❌ Error generando comparación: {comparison_response.get('error', 'Error desconocido')}")
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Tiempo de espera agotado. La comparación puede estar tardando más de lo esperado.")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    
    # Ejemplos de comparación
    with st.expander("💡 Ejemplos de comparaciones"):
        st.markdown("""
        **Comparación metodológica:**
        - Grupo 1: "metodología cuantitativa"
        - Grupo 2: "metodología cualitativa"
        
        **Comparación temporal:**
        - Grupo 1: "resultados del primer trimestre"
        - Grupo 2: "resultados del segundo trimestre"
        
        **Comparación conceptual:**
        - Grupo 1: "ventajas del enfoque A"
        - Grupo 2: "ventajas del enfoque B"
        
        **Comparación de perspectivas:**
        - Grupo 1: "opinión de expertos"
        - Grupo 2: "datos estadísticos"
        """)
    
    with st.expander("🔧 Cómo funciona la comparación"):
        st.markdown("""
        1. **Búsqueda dirigida**: Se buscan fragmentos relevantes para cada consulta
        2. **Agrupación**: Los fragmentos se organizan en dos grupos basados en las consultas
        3. **Análisis con IA**: El modelo de lenguaje analiza ambos grupos
        4. **Comparación estructurada**: Se genera un análisis que incluye:
           - Similitudes encontradas
           - Diferencias clave identificadas
           - Aspectos complementarios
           - Conclusiones del análisis comparativo
        """)
    
    # Consejos de uso
    with st.expander("📝 Consejos para mejores comparaciones"):
        st.markdown("""
        **Para obtener mejores resultados:**
        - Sé específico en las descripciones de búsqueda
        - Usa términos clave relevantes de tus documentos
        - Considera diferentes perspectivas del mismo tema
        - Experimenta con diferentes enfoques de comparación
        
        **Ejemplos de términos efectivos:**
        - Nombres de metodologías, teorías o conceptos específicos
        - Fechas, períodos o fases temporales
        - Tipos de datos o evidencia
        - Diferentes stakeholders o perspectivas
        """)

def advanced_summary_page():
    """Página para resumen avanzado de documentos"""
    st.header("📊 Resumen Avanzado de Documentos")
    
    # Verificar tipos de resumen disponibles
    try:
        types_response = requests.get(f"{API_BASE_URL}/api/chat/summarize/types", timeout=5)
        if types_response.status_code == 200:
            types_data = types_response.json()
            summary_types = types_data.get("summary_types", {})
        else:
            summary_types = {}
    except:
        summary_types = {}
    
    # Configuración del resumen
    st.subheader("⚙️ Configuración del Resumen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selección de tipo de resumen
        summary_type = st.selectbox(
            "Tipo de Resumen:",
            options=list(summary_types.keys()) if summary_types else ["comprehensive", "executive", "technical", "bullet_points"],
            format_func=lambda x: summary_types.get(x, {}).get("name", x.title()) if summary_types else x.title(),
            help="Selecciona el tipo de resumen que mejor se adapte a tus necesidades"
        )
        
        # Mostrar descripción del tipo seleccionado
        if summary_types and summary_type in summary_types:
            type_info = summary_types[summary_type]
            st.info(f"**{type_info.get('name', '')}**: {type_info.get('description', '')}")
            st.markdown(f"*Recomendado para: {type_info.get('recommended_for', '')}*")
    
    with col2:
        # Configuraciones adicionales
        max_tokens = st.slider(
            "Longitud máxima (tokens):",
            min_value=200,
            max_value=1500,
            value=800,
            step=50,
            help="Controla la longitud del resumen generado"
        )
        
        # Opción para documentos específicos (placeholder)
        st.markdown("**Documentos a resumir:**")
        all_documents = st.checkbox("Todos los documentos en la base de datos", value=True, key="advanced_all_documents")
        
        if not all_documents:
            st.info("💡 Función de selección específica de documentos próximamente")
    
    # Botón para generar resumen
    if st.button("📝 Generar Resumen Avanzado", type="primary"):
        with st.spinner(f"Generando resumen {summary_type}... Esto puede tomar unos momentos."):
            try:
                # Preparar request
                request_data = {
                    "summary_type": summary_type,
                    "max_tokens": max_tokens
                }
                
                # Si no se seleccionan todos los documentos, se puede agregar document_ids
                if not all_documents:
                    request_data["document_ids"] = []  # Lista vacía por ahora
                
                # Hacer request al endpoint avanzado
                response = requests.post(
                    f"{API_BASE_URL}/api/chat/summarize/advanced",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success", False):
                        st.success("✅ Resumen generado exitosamente!")
                        
                        # Mostrar estadísticas del resumen
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📄 Documentos", result.get("documents_processed", 0))
                        with col2:
                            st.metric("🔤 Tokens usados", result.get("tokens_used", 0))
                        with col3:
                            st.metric("🤖 Método", result.get("method", "Unknown").replace("_", " ").title())
                        with col4:
                            st.metric("📋 Tipo", result.get("summary_type", "").title())
                        
                        # Mostrar el resumen
                        st.subheader(f"📋 Resumen {summary_type.title()}")
                        summary_text = result.get("summary", "")
                        st.markdown(summary_text)
                        
                        # Botón para descargar
                        if summary_text:
                            st.download_button(
                                label="💾 Descargar Resumen",
                                data=summary_text,
                                file_name=f"resumen_{summary_type}_{result.get('documents_processed', 0)}_docs.txt",
                                mime="text/plain"
                            )
                        
                        # Información adicional
                        if result.get("model_used") and result.get("model_used") != "unknown":
                            st.info(f"🤖 Modelo utilizado: {result.get('model_used')}")
                    
                    else:
                        st.error(f"❌ Error generando resumen: {result.get('error', 'Error desconocido')}")
                
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Timeout: El resumen está tomando más tiempo del esperado")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Error de conexión con el backend")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    
    # Información sobre tipos de resumen
    if summary_types:
        st.subheader("📖 Información sobre Tipos de Resumen")
        for type_key, type_info in summary_types.items():
            with st.expander(f"📋 {type_info.get('name', type_key.title())}"):
                st.markdown(f"**Descripción:** {type_info.get('description', '')}")
                st.markdown(f"**Recomendado para:** {type_info.get('recommended_for', '')}")
    
    # Información sobre funcionalidades
    with st.expander("ℹ️ Características del Resumen Avanzado"):
        features = {
            "🤖 IA Avanzada": "Usa Llama local cuando está disponible para resúmenes sofisticados",
            "🔄 Fallback Inteligente": "Sistema de respaldo con resumen extractivo si no hay LLM",
            "📚 Multi-documento": "Puede resumir múltiples documentos simultáneamente",
            "🎯 Tipos Especializados": "Diferentes tipos de resumen para diferentes audiencias",
            "⚙️ Configurable": "Control sobre longitud y enfoque del resumen"
        }
        
        for feature, description in features.items():
            st.markdown(f"**{feature}**: {description}")

def topic_classification_page():
    """Página para clasificación de temas de documentos"""
    st.header("🏷️ Clasificación de Temas")
    
    # Obtener etiquetas disponibles
    try:
        labels_response = requests.get(f"{API_BASE_URL}/api/chat/classify/labels", timeout=5)
        if labels_response.status_code == 200:
            labels_data = labels_response.json()
            default_labels = labels_data.get("default_labels", [])
            label_categories = labels_data.get("label_categories", {})
        else:
            default_labels = []
            label_categories = {}
    except:
        default_labels = ["tecnología", "ciencia", "negocios", "salud", "educación"]
        label_categories = {}
    
    # Configuración de clasificación
    st.subheader("⚙️ Configuración de Clasificación")
    
    # Pestañas para diferentes opciones
    tab1, tab2, tab3 = st.tabs(["🏷️ Clasificación por Colección", "📄 Documento Individual", "📊 Análisis de Insights"])
    
    with tab1:
        st.subheader("📚 Clasificar Colección de Documentos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Usar etiquetas por defecto o personalizadas
            use_custom_labels = st.checkbox("Usar etiquetas personalizadas", value=False, key="comparison_custom_labels")
            
            if use_custom_labels:
                st.markdown("**Etiquetas personalizadas:**")
                custom_labels_input = st.text_area(
                    "Ingresa etiquetas separadas por comas:",
                    value=", ".join(default_labels[:5]),
                    help="Ejemplo: tecnología, medicina, educación, finanzas"
                )
                labels_to_use = [label.strip() for label in custom_labels_input.split(",") if label.strip()]
            else:
                labels_to_use = default_labels
                st.markdown("**Etiquetas por defecto:**")
                st.write(", ".join(labels_to_use))
        
        with col2:
            # Configuraciones avanzadas
            confidence_threshold = st.slider(
                "Umbral de confianza:",
                min_value=0.1,
                max_value=0.9,
                value=0.3,
                step=0.1,
                help="Clasificaciones con confianza menor serán marcadas como 'unknown'"
            )
            
            # Selección de documentos (placeholder)
            st.markdown("**Documentos a clasificar:**")
            all_docs_classify = st.checkbox("Todos los documentos", value=True, key="classify_all")
            
            if not all_docs_classify:
                st.info("💡 Selección específica próximamente")
        
        # Botón para clasificar
        if st.button("🏷️ Clasificar Documentos", type="primary", key="classify_collection"):
            with st.spinner("Clasificando documentos... Esto puede tomar unos momentos."):
                try:
                    request_data = {
                        "confidence_threshold": confidence_threshold
                    }
                    
                    if use_custom_labels and labels_to_use:
                        request_data["custom_labels"] = labels_to_use
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat/classify/topics",
                        json=request_data,
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("success", False):
                            st.success("✅ Clasificación completada!")
                            
                            # Estadísticas generales
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📄 Documentos", result.get("total_documents", 0))
                            with col2:
                                st.metric("🏷️ Temas encontrados", len([t for t in result.get("topic_statistics", {}).values() if t > 0]))
                            with col3:
                                st.metric("🎯 Método", result.get("method", "unknown").replace("_", " ").title())
                            
                            # Gráfico de distribución de temas
                            topic_stats = result.get("topic_statistics", {})
                            if topic_stats:
                                st.subheader("📊 Distribución de Temas")
                                
                                # Preparar datos para gráfico
                                topics = list(topic_stats.keys())
                                counts = list(topic_stats.values())
                                
                                # Mostrar en columnas
                                cols = st.columns(min(4, len([c for c in counts if c > 0])))
                                col_idx = 0
                                for topic, count in zip(topics, counts):
                                    if count > 0:
                                        with cols[col_idx % len(cols)]:
                                            st.metric(topic.title(), count)
                                        col_idx += 1
                            
                            # Temas dominantes
                            dominant_topics = result.get("dominant_topics", [])
                            if dominant_topics:
                                st.subheader("🏆 Temas Dominantes")
                                for i, (topic, count) in enumerate(dominant_topics[:5]):
                                    percentage = (count / result.get("total_documents", 1)) * 100
                                    st.write(f"**{i+1}. {topic.title()}**: {count} documentos ({percentage:.1f}%)")
                            
                            # Clasificaciones individuales
                            classifications = result.get("classification_results", {}).get("classifications", [])
                            if classifications:
                                st.subheader("📋 Clasificaciones Individuales")
                                
                                # Filtros
                                show_all = st.checkbox("Mostrar todos los documentos", value=False, key="comparison_show_all")
                                if not show_all:
                                    min_confidence = st.slider("Confianza mínima a mostrar:", 0.0, 1.0, 0.3, 0.1)
                                    filtered_classifications = [c for c in classifications if c.get("confidence", 0) >= min_confidence]
                                else:
                                    filtered_classifications = classifications
                                
                                for doc_class in filtered_classifications[:10]:  # Mostrar primeros 10
                                    with st.expander(f"📄 {doc_class.get('document', 'Documento')} - {doc_class.get('primary_topic', 'unknown').title()}"):
                                        st.write(f"**Tema principal:** {doc_class.get('primary_topic', 'unknown').title()}")
                                        st.write(f"**Confianza:** {doc_class.get('confidence', 0):.2f}")
                                        
                                        # Mostrar todos los scores si están disponibles
                                        all_scores = doc_class.get('all_scores', {})
                                        if all_scores:
                                            st.write("**Puntuaciones por tema:**")
                                            for topic, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
                                                if score > 0.1:  # Solo mostrar scores significativos
                                                    st.write(f"  - {topic.title()}: {score:.3f}")
                            
                            # Insights si están disponibles
                            insights = result.get("insights", {})
                            if insights:
                                st.subheader("💡 Insights de la Colección")
                                
                                collection_profile = insights.get("collection_profile", {})
                                if collection_profile:
                                    st.write(f"**Enfoque principal:** {collection_profile.get('primary_focus', 'Desconocido').title()}")
                                    st.write(f"**Porcentaje de enfoque:** {collection_profile.get('focus_percentage', 0):.1f}%")
                                    
                                    if collection_profile.get('is_specialized'):
                                        st.info("📚 Esta es una colección especializada")
                                    if collection_profile.get('is_diverse'):
                                        st.info("🌈 Esta colección tiene buena diversidad temática")
                                
                                diversity_analysis = insights.get("diversity_analysis", {})
                                if diversity_analysis:
                                    st.write(f"**Clasificación de diversidad:** {diversity_analysis.get('classification', 'Desconocida')}")
                                    st.write(f"**Puntuación de diversidad:** {diversity_analysis.get('diversity_score', 0):.1f}%")
                        
                        else:
                            st.error(f"❌ Error en clasificación: {result.get('error', 'Error desconocido')}")
                    
                    else:
                        st.error(f"❌ Error del servidor: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏰ Timeout: La clasificación está tomando más tiempo del esperado")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Error de conexión con el backend")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")
    
    with tab2:
        st.subheader("📄 Clasificar Documento Individual")
        
        # Entrada de texto
        document_content = st.text_area(
            "Ingresa el contenido del documento:",
            height=200,
            placeholder="Pega aquí el texto que deseas clasificar..."
        )
        
        if document_content.strip():
            col1, col2 = st.columns(2)
            
            with col1:
                # Configuración para documento individual
                use_custom_single = st.checkbox("Etiquetas personalizadas", value=False, key="single_custom")
                if use_custom_single:
                    custom_single_labels = st.text_input(
                        "Etiquetas (separadas por comas):",
                        value=", ".join(default_labels[:5])
                    )
                    single_labels = [label.strip() for label in custom_single_labels.split(",") if label.strip()]
                else:
                    single_labels = default_labels
            
            with col2:
                single_threshold = st.slider(
                    "Umbral de confianza:",
                    min_value=0.1,
                    max_value=0.9,
                    value=0.3,
                    step=0.1,
                    key="single_threshold"
                )
            
            if st.button("🏷️ Clasificar Texto", type="primary", key="classify_single"):
                with st.spinner("Clasificando contenido..."):
                    try:
                        params = {
                            "content": document_content,
                            "confidence_threshold": single_threshold
                        }
                        
                        if use_custom_single and single_labels:
                            params["custom_labels"] = single_labels
                        
                        response = requests.post(
                            f"{API_BASE_URL}/api/chat/classify/single",
                            params=params,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            if result.get("success", False):
                                st.success("✅ Texto clasificado!")
                                
                                # Resultado principal
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("🏷️ Tema principal", result.get("primary_topic", "unknown").title())
                                with col2:
                                    st.metric("🎯 Confianza", f"{result.get('confidence', 0):.2f}")
                                with col3:
                                    st.metric("📏 Caracteres", result.get("content_length", 0))
                                
                                # Razón de la clasificación
                                if result.get("reason"):
                                    st.info(f"💭 **Razón:** {result.get('reason')}")
                                
                                # Puntuaciones detalladas
                                scores = result.get("scores", {})
                                if scores:
                                    st.subheader("📊 Puntuaciones por Tema")
                                    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                                    
                                    for topic, score in sorted_scores:
                                        if score > 0.05:  # Solo mostrar scores relevantes
                                            progress_val = min(score, 1.0)
                                            st.write(f"**{topic.title()}**")
                                            st.progress(progress_val)
                                            st.write(f"Puntuación: {score:.3f}")
                                            st.write("")
                            
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                        
                        else:
                            st.error(f"❌ Error del servidor: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("📊 Análisis de Insights")
        st.info("💡 Ejecuta primero una clasificación por colección para ver insights detallados")
        
        # Información sobre qué insights se pueden obtener
        with st.expander("🔍 ¿Qué insights puedes obtener?"):
            st.markdown("""
            **Perfil de la Colección:**
            - Tema principal y su porcentaje de dominancia
            - Si la colección es especializada o diversa
            - Distribución temática general
            
            **Análisis de Diversidad:**
            - Puntuación de diversidad (0-100%)
            - Clasificación cualitativa de la diversidad
            - Número de temas presentes
            
            **Recomendaciones:**
            - Sugerencias basadas en la distribución temática
            - Identificación de posibles mejoras
            - Orientación para análisis adicionales
            """)
    
    # Información sobre categorías de etiquetas
    if label_categories:
        st.subheader("📂 Categorías de Etiquetas Disponibles")
        for category, labels in label_categories.items():
            with st.expander(f"📁 {category.title()}"):
                st.write(", ".join(labels))
    
    # Información sobre funcionalidades
    with st.expander("ℹ️ Características de Clasificación"):
        st.markdown("""
        **🤖 Métodos de Clasificación:**
        - **LLM Local**: Usa Llama para clasificación inteligente cuando está disponible
        - **Palabras Clave**: Sistema de respaldo basado en coincidencias de palabras clave
        - **HuggingFace**: Zero-shot classification (en desarrollo futuro)
        
        **🎯 Características:**
        - Etiquetas personalizables para dominios específicos
        - Control de umbral de confianza
        - Análisis de insights automático
        - Estadísticas detalladas de distribución
        - Clasificación individual o por lotes
        """)

if __name__ == "__main__":
    main()
