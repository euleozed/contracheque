import streamlit as st
import os
from datetime import datetime

class FileUploader:
    def __init__(self):
        self.supported_types = ["pdf", "png", "jpg", "jpeg"]
    
    def render(self):
        """Renderiza a interface de upload de arquivos"""
        st.subheader("📁 Upload de Documentos")
        
        # Opções de upload
        upload_option = st.radio(
            "Escolha o tipo de upload:",
            ["Upload único", "Upload múltiplo"],
            horizontal=True
        )
        
        if upload_option == "Upload único":
            return self._single_upload()
        else:
            return self._multiple_upload()
    
    def _single_upload(self):
        """Upload de arquivo único"""
        uploaded_file = st.file_uploader(
            "Envie um contracheque ou comprovante",
            type=self.supported_types,
            help="Formatos suportados: PDF, PNG, JPG, JPEG"
        )
        
        if uploaded_file:
            # Mostrar informações do arquivo
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📄 Nome", uploaded_file.name)
            
            with col2:
                size_mb = uploaded_file.size / (1024 * 1024)
                st.metric("💾 Tamanho", f"{size_mb:.2f} MB")
            
            with col3:
                file_type = uploaded_file.type
                st.metric("🔧 Tipo", file_type.split('/')[-1].upper())
            
            return [uploaded_file]
        
        return []
    
    def _multiple_upload(self):
        """Upload de múltiplos arquivos"""
        uploaded_files = st.file_uploader(
            "Envie múltiplos contracheques ou comprovantes",
            type=self.supported_types,
            accept_multiple_files=True,
            help="Formatos suportados: PDF, PNG, JPG, JPEG"
        )
        
        if uploaded_files:
            # Mostrar resumo dos arquivos
            st.write(f"**{len(uploaded_files)} arquivo(s) selecionado(s):**")
            
            total_size = 0
            for i, file in enumerate(uploaded_files):
                size_mb = file.size / (1024 * 1024)
                total_size += size_mb
                
                with st.expander(f"📄 {file.name} ({size_mb:.2f} MB)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {file.type}")
                    with col2:
                        st.write(f"**Tamanho:** {file.size:,} bytes")
            
            # Resumo total
            st.info(f"📊 **Total:** {len(uploaded_files)} arquivos • {total_size:.2f} MB")
            
            return uploaded_files
        
        return []
    
    def save_temp_file(self, uploaded_file, temp_folder="temp"):
        """Salva arquivo temporário no disco"""
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        
        # Criar nome único baseado em timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(temp_folder, filename)
        
        # Salvar arquivo
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    
    def validate_file(self, uploaded_file):
        """Valida o arquivo antes do processamento"""
        errors = []
        warnings = []
        
        # Verificar tamanho (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            errors.append(f"Arquivo muito grande: {uploaded_file.size / (1024*1024):.1f}MB (máximo: 10MB)")
        
        # Verificar tipo
        if not any(uploaded_file.name.lower().endswith(ext) for ext in ['.pdf', '.png', '.jpg', '.jpeg']):
            errors.append("Tipo de arquivo não suportado")
        
        # Avisos baseados no tamanho
        if uploaded_file.size < 50 * 1024:  # Menor que 50KB
            warnings.append("Arquivo muito pequeno, qualidade do OCR pode ser afetada")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        } 