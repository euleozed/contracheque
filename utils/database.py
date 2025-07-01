import sqlite3
import pandas as pd
from datetime import datetime
import json
from config import APP_CONFIG

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or APP_CONFIG["database_file"]
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela principal de contracheques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contracheques (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    cpf TEXT,
                    periodo TEXT,
                    empresa TEXT,
                    cargo TEXT,
                    salario_bruto REAL,
                    salario_liquido REAL,
                    descontos REAL,
                    data_processamento TEXT,
                    texto_original TEXT,
                    confianca_ocr REAL,
                    arquivo_origem TEXT,
                    validacao_status TEXT,
                    validacao_erros TEXT,
                    validacao_avisos TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes (
                    chave TEXT PRIMARY KEY,
                    valor TEXT,
                    descricao TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de logs de processamento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT,
                    mensagem TEXT,
                    detalhes TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def insert_contracheque(self, data, ocr_confidence=None, arquivo_origem=None, 
                           validacao=None):
        """Insere um novo contracheque no banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Preparar dados de validação
            validacao = validacao or {}
            validacao_status = "válido" if validacao.get('is_valid', False) else "inválido"
            validacao_erros = json.dumps(validacao.get('errors', []))
            validacao_avisos = json.dumps(validacao.get('warnings', []))
            
            cursor.execute('''
                INSERT INTO contracheques (
                    nome, cpf, periodo, empresa, cargo, salario_bruto, 
                    salario_liquido, descontos, data_processamento, 
                    texto_original, confianca_ocr, arquivo_origem,
                    validacao_status, validacao_erros, validacao_avisos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('nome'),
                data.get('cpf'),
                data.get('periodo'),
                data.get('empresa'),
                data.get('cargo'),
                data.get('salario_bruto'),
                data.get('salario_liquido'),
                data.get('descontos'),
                data.get('data_processamento'),
                data.get('texto_original'),
                ocr_confidence,
                arquivo_origem,
                validacao_status,
                validacao_erros,
                validacao_avisos
            ))
            
            contracheque_id = cursor.lastrowid
            conn.commit()
            
            # Log da inserção
            self.log_action("insert", f"Contracheque inserido para {data.get('nome', 'N/A')}", 
                          {"id": contracheque_id, "arquivo": arquivo_origem})
            
            return contracheque_id
    
    def get_all_contracheques(self):
        """Retorna todos os contracheques do banco"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT id, nome, cpf, periodo, empresa, cargo, 
                       salario_bruto, salario_liquido, descontos,
                       data_processamento, confianca_ocr, arquivo_origem,
                       validacao_status, created_at
                FROM contracheques 
                ORDER BY created_at DESC
            ''', conn)
            
            return df
    
    def get_contracheques_by_period(self, periodo):
        """Retorna contracheques de um período específico"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM contracheques 
                WHERE periodo = ?
                ORDER BY nome
            ''', conn, params=[periodo])
            
            return df
    
    def get_contracheques_by_name(self, nome):
        """Retorna contracheques de uma pessoa específica"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM contracheques 
                WHERE nome LIKE ?
                ORDER BY periodo DESC
            ''', conn, params=[f"%{nome}%"])
            
            return df
    
    def get_summary_statistics(self):
        """Retorna estatísticas resumidas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total de registros
            cursor.execute("SELECT COUNT(*) FROM contracheques")
            stats['total_registros'] = cursor.fetchone()[0]
            
            # Registros válidos
            cursor.execute("SELECT COUNT(*) FROM contracheques WHERE validacao_status = 'válido'")
            stats['registros_validos'] = cursor.fetchone()[0]
            
            # Períodos únicos
            cursor.execute("SELECT COUNT(DISTINCT periodo) FROM contracheques WHERE periodo IS NOT NULL")
            stats['periodos_unicos'] = cursor.fetchone()[0]
            
            # Funcionários únicos
            cursor.execute("SELECT COUNT(DISTINCT nome) FROM contracheques WHERE nome IS NOT NULL")
            stats['funcionarios_unicos'] = cursor.fetchone()[0]
            
            # Valor total líquido
            cursor.execute("SELECT SUM(salario_liquido) FROM contracheques WHERE salario_liquido IS NOT NULL")
            total_liquido = cursor.fetchone()[0]
            stats['total_liquido'] = total_liquido or 0
            
            # Valor médio líquido
            cursor.execute("SELECT AVG(salario_liquido) FROM contracheques WHERE salario_liquido IS NOT NULL")
            media_liquido = cursor.fetchone()[0]
            stats['media_liquido'] = media_liquido or 0
            
            # Confiança média OCR
            cursor.execute("SELECT AVG(confianca_ocr) FROM contracheques WHERE confianca_ocr IS NOT NULL")
            media_confianca = cursor.fetchone()[0]
            stats['media_confianca_ocr'] = media_confianca or 0
            
            return stats
    
    def delete_contracheque(self, contracheque_id):
        """Remove um contracheque do banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Buscar dados antes de deletar para log
            cursor.execute("SELECT nome, arquivo_origem FROM contracheques WHERE id = ?", [contracheque_id])
            result = cursor.fetchone()
            
            if result:
                cursor.execute("DELETE FROM contracheques WHERE id = ?", [contracheque_id])
                conn.commit()
                
                # Log da exclusão
                self.log_action("delete", f"Contracheque deletado para {result[0]}", 
                              {"id": contracheque_id, "arquivo": result[1]})
                
                return True
            
            return False
    
    def update_contracheque(self, contracheque_id, data):
        """Atualiza um contracheque existente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Construir query de update dinamicamente
            fields = []
            values = []
            
            for field, value in data.items():
                if field in ['nome', 'cpf', 'periodo', 'empresa', 'cargo', 
                           'salario_bruto', 'salario_liquido', 'descontos']:
                    fields.append(f"{field} = ?")
                    values.append(value)
            
            if fields:
                query = f"UPDATE contracheques SET {', '.join(fields)} WHERE id = ?"
                values.append(contracheque_id)
                
                cursor.execute(query, values)
                conn.commit()
                
                # Log da atualização
                self.log_action("update", f"Contracheque atualizado ID {contracheque_id}", data)
                
                return cursor.rowcount > 0
            
            return False
    
    def log_action(self, tipo, mensagem, detalhes=None):
        """Registra uma ação no log"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs (tipo, mensagem, detalhes)
                VALUES (?, ?, ?)
            ''', (tipo, mensagem, json.dumps(detalhes) if detalhes else None))
            
            conn.commit()
    
    def get_logs(self, limit=100):
        """Retorna logs do sistema"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', conn, params=[limit])
            
            return df
    
    def export_to_excel(self, filepath, periodo=None):
        """Exporta dados para Excel"""
        if periodo:
            df = self.get_contracheques_by_period(periodo)
        else:
            df = self.get_all_contracheques()
        
        if not df.empty:
            # Formatar valores monetários
            for col in ['salario_bruto', 'salario_liquido', 'descontos']:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else "R$ 0,00")
            
            df.to_excel(filepath, index=False)
            
            # Log da exportação
            self.log_action("export", f"Dados exportados para {filepath}", 
                          {"registros": len(df), "periodo": periodo})
            
            return True
        
        return False 