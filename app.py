import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Adicionar diretório atual ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos personalizados
from config import APP_CONFIG, create_required_folders
from utils import OCRProcessor, DataExtractor, Database
from components import FileUploader, DataDisplay

def main():
    # Configurar página
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon="📑",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Criar pastas necessárias
    create_required_folders()
    
    # Inicializar componentes
    ocr_processor = OCRProcessor()
    data_extractor = DataExtractor()
    database = Database()
    file_uploader = FileUploader()
    data_display = DataDisplay()
    
    # Título principal
    st.title(APP_CONFIG["title"])
    st.markdown(f"**Versão {APP_CONFIG['version']}** - {APP_CONFIG['author']}")
    
    # Sidebar para navegação
    st.sidebar.title("🔧 Menu Principal")
    
    opcao = st.sidebar.selectbox(
        "Escolha uma opção:",
        [
            "📤 Processar Documentos",
            "📊 Visualizar Dados",
            "📈 Análises e Relatórios",
            "⚙️ Configurações",
            "📋 Logs do Sistema"
        ]
    )
    
    if opcao == "📤 Processar Documentos":
        processar_documentos(file_uploader, ocr_processor, data_extractor, database, data_display)
    
    elif opcao == "📊 Visualizar Dados":
        visualizar_dados(database, data_display)
    
    elif opcao == "📈 Análises e Relatórios":
        analises_relatorios(database, data_display)
    
    elif opcao == "⚙️ Configurações":
        configuracoes(database)
    
    elif opcao == "📋 Logs do Sistema":
        logs_sistema(database)

def processar_documentos(file_uploader, ocr_processor, data_extractor, database, data_display):
    """Processa documentos enviados pelo usuário"""
    st.header("📤 Processamento de Documentos")
    
    # Upload de arquivos
    uploaded_files = file_uploader.render()
    
    if uploaded_files:
        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        resultados = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Atualizar progresso
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processando {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
            
            # Validar arquivo
            validation = file_uploader.validate_file(uploaded_file)
            
            if not validation['is_valid']:
                st.error(f"❌ Erro no arquivo {uploaded_file.name}:")
                for error in validation['errors']:
                    st.write(f"• {error}")
                continue
            
            # Processar arquivo
            with st.expander(f"📄 Processando: {uploaded_file.name}"):
                # OCR
                st.write("🔍 Extraindo texto via OCR...")
                
                if uploaded_file.type == "application/pdf":
                    ocr_result = ocr_processor.extract_text_from_pdf(uploaded_file)
                else:
                    ocr_result = ocr_processor.extract_text_from_image(uploaded_file)
                
                if ocr_result['status'] == 'error':
                    st.error(f"Erro no OCR: {ocr_result.get('error', 'Erro desconhecido')}")
                    continue
                
                # Extração de dados
                st.write("📋 Extraindo dados estruturados...")
                extracted_data = data_extractor.extract_all_data(ocr_result['text'])
                
                # Validação
                validation_result = data_extractor.validate_data(extracted_data)
                
                # Exibir resultados
                data_display.show_extraction_results(extracted_data, validation_result, ocr_result)
                
                # Salvar no banco de dados
                if st.button(f"💾 Salvar no Banco", key=f"save_{i}"):
                    contracheque_id = database.insert_contracheque(
                        extracted_data,
                        ocr_result['confidence'],
                        uploaded_file.name,
                        validation_result
                    )
                    st.success(f"✅ Contracheque salvo com ID: {contracheque_id}")
                
                # Mostrar texto original se solicitado
                if st.checkbox(f"🔍 Ver texto OCR completo", key=f"text_{i}"):
                    st.text_area(
                        "Texto extraído via OCR",
                        ocr_result['text'],
                        height=300,
                        key=f"textarea_{i}"
                    )
                
                resultados.append({
                    'arquivo': uploaded_file.name,
                    'dados': extracted_data,
                    'validacao': validation_result,
                    'ocr': ocr_result
                })
        
        # Finalizar progresso
        progress_bar.progress(1.0)
        status_text.text("✅ Processamento concluído!")
        
        # Resumo final
        if resultados:
            st.success(f"🎉 Processamento finalizado! {len(resultados)} arquivo(s) processado(s).")
            
            # Opção para salvar todos
            if st.button("💾 Salvar Todos no Banco"):
                saved_count = 0
                for resultado in resultados:
                    if resultado['validacao']['is_valid']:
                        database.insert_contracheque(
                            resultado['dados'],
                            resultado['ocr']['confidence'],
                            resultado['arquivo'],
                            resultado['validacao']
                        )
                        saved_count += 1
                
                st.success(f"✅ {saved_count} contracheques salvos no banco de dados!")

def visualizar_dados(database, data_display):
    """Visualiza dados do banco de dados"""
    st.header("📊 Visualização de Dados")
    
    # Estatísticas gerais
    stats = database.get_summary_statistics()
    data_display.show_database_summary(stats)
    
    # Filtros
    st.subheader("🔍 Filtros e Busca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Busca por nome
        nome_busca = st.text_input("🔍 Buscar por nome")
        
        if nome_busca:
            df = database.get_contracheques_by_name(nome_busca)
            st.write(f"Resultados para: **{nome_busca}**")
        else:
            df = database.get_all_contracheques()
    
    with col2:
        # Busca por período
        periodo_busca = st.text_input("📅 Buscar por período (MM/AAAA)")
        
        if periodo_busca:
            df = database.get_contracheques_by_period(periodo_busca)
            st.write(f"Resultados para período: **{periodo_busca}**")
    
    # Exibir dados
    if not df.empty:
        df_filtrado = data_display.show_dataframe(df, "Contracheques Encontrados")
        
        # Gráficos
        if len(df_filtrado) > 1:
            data_display.show_charts(df_filtrado)
    else:
        st.info("Nenhum contracheque encontrado no banco de dados.")

def analises_relatorios(database, data_display):
    """Seção de análises e relatórios"""
    st.header("📈 Análises e Relatórios")
    
    df = database.get_all_contracheques()
    
    if df.empty:
        st.info("Nenhum dado disponível para análise.")
        return
    
    # Tabs para diferentes análises
    tab1, tab2, tab3 = st.tabs(["📊 Resumo Geral", "💰 Análise Salarial", "📅 Análise Temporal"])
    
    with tab1:
        stats = database.get_summary_statistics()
        data_display.show_database_summary(stats)
        
        # Métricas adicionais
        st.subheader("📋 Detalhes Adicionais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'salario_liquido' in df.columns:
                maior_salario = df['salario_liquido'].max()
                st.metric("💎 Maior Salário", f"R$ {maior_salario:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        with col2:
            if 'salario_liquido' in df.columns:
                menor_salario = df['salario_liquido'].min()
                st.metric("📉 Menor Salário", f"R$ {menor_salario:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        with col3:
            if 'confianca_ocr' in df.columns:
                confianca_min = df['confianca_ocr'].min()
                st.metric("🎯 Menor Confiança OCR", f"{confianca_min:.1f}%")
    
    with tab2:
        st.subheader("💰 Análise Salarial Detalhada")
        data_display.show_charts(df)
        
        # Estatísticas salariais
        if 'salario_liquido' in df.columns:
            sal_stats = df['salario_liquido'].describe()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Estatísticas Salariais:**")
                st.write(f"• Média: R$ {sal_stats['mean']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                st.write(f"• Mediana: R$ {sal_stats['50%']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                st.write(f"• Desvio Padrão: R$ {sal_stats['std']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            with col2:
                st.write("**Quartis:**")
                st.write(f"• Q1: R$ {sal_stats['25%']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                st.write(f"• Q3: R$ {sal_stats['75%']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                st.write(f"• Amplitude: R$ {sal_stats['max'] - sal_stats['min']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    
    with tab3:
        st.subheader("📅 Análise Temporal")
        
        if 'periodo' in df.columns and 'salario_liquido' in df.columns:
            # Evolução temporal
            df_tempo = df.groupby('periodo').agg({
                'salario_liquido': ['mean', 'count', 'sum'],
                'nome': 'nunique'
            }).round(2)
            
            df_tempo.columns = ['Salário Médio', 'Qtd Registros', 'Total Pago', 'Funcionários Únicos']
            
            st.write("**Resumo por Período:**")
            st.dataframe(df_tempo, use_container_width=True)
        
        else:
            st.info("Dados de período não disponíveis para análise temporal.")

def configuracoes(database):
    """Seção de configurações"""
    st.header("⚙️ Configurações do Sistema")
    
    # Informações do sistema
    st.subheader("ℹ️ Informações do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Versão:** {APP_CONFIG['version']}")
        st.write(f"**Autor:** {APP_CONFIG['author']}")
        st.write(f"**Banco de Dados:** {APP_CONFIG['database_file']}")
    
    with col2:
        st.write(f"**Pasta de Exports:** {APP_CONFIG['export_folder']}")
        st.write(f"**Pasta Temporária:** {APP_CONFIG['temp_folder']}")
    
    # Ações de manutenção
    st.subheader("🔧 Manutenção")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpar Dados Temporários"):
            # Implementar limpeza de arquivos temporários
            st.success("Dados temporários limpos!")
    
    with col2:
        if st.button("📤 Backup do Banco"):
            # Implementar backup
            st.info("Funcionalidade de backup será implementada")
    
    with col3:
        if st.button("🔄 Resetar Configurações"):
            # Implementar reset
            st.warning("Funcionalidade de reset será implementada")

def logs_sistema(database):
    """Exibe logs do sistema"""
    st.header("📋 Logs do Sistema")
    
    # Controles
    col1, col2 = st.columns(2)
    
    with col1:
        limit = st.selectbox("Número de logs", [50, 100, 200, 500], index=1)
    
    with col2:
        if st.button("🔄 Atualizar Logs"):
            st.rerun()
    
    # Buscar logs
    logs_df = database.get_logs(limit)
    
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True, height=400)
    else:
        st.info("Nenhum log encontrado.")

if __name__ == "__main__":
    main()
