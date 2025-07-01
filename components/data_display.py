import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

class DataDisplay:
    def __init__(self):
        pass
    
    def show_extraction_results(self, extracted_data, validation_result, ocr_result):
        """Exibe os resultados da extração de dados"""
        
        # Status da validação
        if validation_result['is_valid']:
            st.success("✅ Dados extraídos com sucesso!")
        else:
            st.error("❌ Problemas encontrados na extração")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            confidence = ocr_result.get('confidence', 0)
            color = "normal" if confidence > 70 else "inverse"
            st.metric("🎯 Confiança OCR", f"{confidence:.1f}%", delta_color=color)
        
        with col2:
            pages = ocr_result.get('pages', 0)
            st.metric("📄 Páginas", pages)
        
        with col3:
            errors_count = len(validation_result.get('errors', []))
            st.metric("❌ Erros", errors_count, delta_color="inverse" if errors_count > 0 else "normal")
        
        with col4:
            warnings_count = len(validation_result.get('warnings', []))
            st.metric("⚠️ Avisos", warnings_count, delta_color="inverse" if warnings_count > 0 else "normal")
        
        # Dados extraídos
        st.subheader("📋 Dados Extraídos")
        
        # Organizar dados em duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Informações Pessoais**")
            nome = extracted_data.get('nome', 'Não encontrado')
            cpf = extracted_data.get('cpf', 'Não encontrado')
            
            st.write(f"**Nome:** {nome}")
            st.write(f"**CPF:** {cpf}")
            
            st.markdown("**🏢 Informações Profissionais**")
            empresa = extracted_data.get('empresa', 'Não encontrado')
            cargo = extracted_data.get('cargo', 'Não encontrado')
            periodo = extracted_data.get('periodo', 'Não encontrado')
            
            st.write(f"**Empresa:** {empresa}")
            st.write(f"**Cargo:** {cargo}")
            st.write(f"**Período:** {periodo}")
        
        with col2:
            st.markdown("**💰 Informações Financeiras**")
            
            bruto = extracted_data.get('salario_bruto', 0) or 0
            liquido = extracted_data.get('salario_liquido', 0) or 0
            descontos = extracted_data.get('descontos', 0) or 0
            
            st.write(f"**Salário Bruto:** R$ {bruto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            st.write(f"**Descontos:** R$ {descontos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            st.write(f"**Salário Líquido:** R$ {liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            # Gráfico simples de composição salarial
            if bruto > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['Salário Líquido', 'Descontos'],
                    values=[liquido, descontos],
                    hole=0.4
                )])
                fig.update_layout(
                    title="Composição Salarial",
                    height=300,
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Erros e avisos
        if validation_result.get('errors'):
            st.error("❌ **Erros encontrados:**")
            for error in validation_result['errors']:
                st.write(f"• {error}")
        
        if validation_result.get('warnings'):
            st.warning("⚠️ **Avisos:**")
            for warning in validation_result['warnings']:
                st.write(f"• {warning}")
        
        return extracted_data
    
    def show_database_summary(self, db_stats):
        """Exibe resumo dos dados do banco"""
        st.subheader("📊 Resumo do Banco de Dados")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Total de Registros", db_stats.get('total_registros', 0))
        
        with col2:
            st.metric("✅ Registros Válidos", db_stats.get('registros_validos', 0))
        
        with col3:
            st.metric("👥 Funcionários", db_stats.get('funcionarios_unicos', 0))
        
        with col4:
            st.metric("📅 Períodos", db_stats.get('periodos_unicos', 0))
        
        # Métricas financeiras
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_liquido = db_stats.get('total_liquido', 0)
            st.metric("💰 Total Líquido", f"R$ {total_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        with col2:
            media_liquido = db_stats.get('media_liquido', 0)
            st.metric("📈 Média Líquida", f"R$ {media_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        with col3:
            media_confianca = db_stats.get('media_confianca_ocr', 0)
            st.metric("🎯 Confiança Média OCR", f"{media_confianca:.1f}%")
    
    def show_dataframe(self, df, title="Dados"):
        """Exibe DataFrame com funcionalidades de filtro e busca"""
        if df.empty:
            st.info("Nenhum dado encontrado.")
            return
        
        st.subheader(f"📋 {title}")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por nome
            if 'nome' in df.columns:
                nomes_unicos = ['Todos'] + sorted(df['nome'].dropna().unique().tolist())
                nome_filtro = st.selectbox("Filtrar por Nome", nomes_unicos)
            else:
                nome_filtro = 'Todos'
        
        with col2:
            # Filtro por período
            if 'periodo' in df.columns:
                periodos_unicos = ['Todos'] + sorted(df['periodo'].dropna().unique().tolist())
                periodo_filtro = st.selectbox("Filtrar por Período", periodos_unicos)
            else:
                periodo_filtro = 'Todos'
        
        with col3:
            # Filtro por status de validação
            if 'validacao_status' in df.columns:
                status_unicos = ['Todos'] + sorted(df['validacao_status'].dropna().unique().tolist())
                status_filtro = st.selectbox("Filtrar por Status", status_unicos)
            else:
                status_filtro = 'Todos'
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if nome_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['nome'] == nome_filtro]
        
        if periodo_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['periodo'] == periodo_filtro]
        
        if status_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['validacao_status'] == status_filtro]
        
        # Mostrar contadores
        st.write(f"**Exibindo {len(df_filtrado)} de {len(df)} registros**")
        
        # Configurar exibição da tabela
        if not df_filtrado.empty:
            # Selecionar colunas para exibir
            colunas_display = []
            if 'nome' in df_filtrado.columns:
                colunas_display.append('nome')
            if 'periodo' in df_filtrado.columns:
                colunas_display.append('periodo')
            if 'empresa' in df_filtrado.columns:
                colunas_display.append('empresa')
            if 'salario_liquido' in df_filtrado.columns:
                colunas_display.append('salario_liquido')
            if 'validacao_status' in df_filtrado.columns:
                colunas_display.append('validacao_status')
            
            # Manter colunas existentes
            colunas_display = [col for col in colunas_display if col in df_filtrado.columns]
            
            # Exibir tabela
            st.dataframe(
                df_filtrado[colunas_display] if colunas_display else df_filtrado,
                use_container_width=True,
                height=400
            )
            
            # Opções de exportação
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Baixar CSV"):
                    csv = df_filtrado.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"contracheques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📊 Exportar Excel"):
                    # Esta funcionalidade seria implementada no app principal
                    st.info("Funcionalidade de exportação Excel será implementada")
        
        else:
            st.info("Nenhum registro corresponde aos filtros aplicados.")
        
        return df_filtrado
    
    def show_charts(self, df):
        """Exibe gráficos dos dados"""
        if df.empty:
            return
        
        st.subheader("📈 Gráficos e Análises")
        
        # Tabs para diferentes tipos de gráficos
        tab1, tab2, tab3 = st.tabs(["💰 Salários", "📅 Períodos", "👥 Funcionários"])
        
        with tab1:
            if 'salario_liquido' in df.columns:
                # Histograma de salários
                fig = px.histogram(
                    df, 
                    x='salario_liquido',
                    title="Distribuição de Salários Líquidos",
                    nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Box plot por empresa
                if 'empresa' in df.columns:
                    fig = px.box(
                        df,
                        x='empresa',
                        y='salario_liquido',
                        title="Salários por Empresa"
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if 'periodo' in df.columns:
                # Evolução temporal
                df_periodo = df.groupby('periodo').agg({
                    'salario_liquido': 'mean',
                    'nome': 'count'
                }).reset_index()
                df_periodo.columns = ['periodo', 'salario_medio', 'quantidade']
                
                fig = px.line(
                    df_periodo,
                    x='periodo',
                    y='salario_medio',
                    title="Evolução do Salário Médio por Período"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if 'nome' in df.columns:
                # Top funcionários por salário
                df_funcionarios = df.groupby('nome')['salario_liquido'].mean().sort_values(ascending=False).head(10)
                
                fig = px.bar(
                    x=df_funcionarios.values,
                    y=df_funcionarios.index,
                    orientation='h',
                    title="Top 10 Funcionários por Salário Médio"
                )
                st.plotly_chart(fig, use_container_width=True) 