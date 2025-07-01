import re
import pandas as pd
from datetime import datetime
from config import REGEX_PATTERNS

class DataExtractor:
    def __init__(self):
        self.patterns = REGEX_PATTERNS
    
    def clean_currency_value(self, value_str):
        """Limpa e converte valor monetário para float"""
        if not value_str:
            return 0.0
        
        # Remove símbolos e espaços
        cleaned = re.sub(r'[R$\s]', '', value_str)
        # Substitui vírgula por ponto
        cleaned = cleaned.replace(',', '.')
        # Remove pontos que não são decimais (milhares)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
        
        try:
            return float(cleaned)
        except:
            return 0.0
    
    def clean_cpf(self, cpf_str):
        """Limpa e formata CPF"""
        if not cpf_str:
            return ""
        
        # Remove tudo que não é dígito
        digits = re.sub(r'[^\d]', '', cpf_str)
        
        if len(digits) == 11:
            # Formatar CPF
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        
        return cpf_str.strip()
    
    def extract_field(self, text, field_name):
        """Extrai um campo específico do texto usando regex"""
        patterns = self.patterns.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                
                # Limpeza específica por tipo de campo
                if field_name in ['salario_bruto', 'salario_liquido', 'descontos']:
                    return self.clean_currency_value(value)
                elif field_name == 'cpf':
                    return self.clean_cpf(value)
                elif field_name in ['nome', 'empresa', 'cargo']:
                    return self.clean_text_field(value)
                else:
                    return value
        
        return None
    
    def clean_text_field(self, text):
        """Limpa campos de texto removendo caracteres indesejados"""
        if not text:
            return ""
        
        # Remove quebras de linha e espaços extras
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove caracteres especiais no final
        cleaned = re.sub(r'[:\-_]+$', '', cleaned)
        
        # Capitalizar primeira letra de cada palavra
        return cleaned.title()
    
    def extract_all_data(self, text):
        """Extrai todos os dados disponíveis do texto"""
        extracted_data = {}
        
        # Campos básicos
        fields = ['nome', 'cpf', 'periodo', 'salario_bruto', 'salario_liquido', 
                 'descontos', 'empresa', 'cargo']
        
        for field in fields:
            extracted_data[field] = self.extract_field(text, field)
        
        # Campos calculados
        bruto = extracted_data.get('salario_bruto', 0) or 0
        liquido = extracted_data.get('salario_liquido', 0) or 0
        descontos = extracted_data.get('descontos', 0) or 0
        
        # Se não encontrou descontos, calcular
        if not descontos and bruto and liquido:
            extracted_data['descontos'] = bruto - liquido
        
        # Se não encontrou bruto, calcular
        if not bruto and liquido and descontos:
            extracted_data['salario_bruto'] = liquido + descontos
        
        # Adicionar metadados
        extracted_data['data_processamento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        extracted_data['texto_original'] = text[:500] + "..." if len(text) > 500 else text
        
        return extracted_data
    
    def validate_data(self, data):
        """Valida os dados extraídos"""
        validation_errors = []
        warnings = []
        
        # Validações obrigatórias
        if not data.get('nome'):
            validation_errors.append("Nome não encontrado")
        
        if not data.get('salario_liquido'):
            validation_errors.append("Salário líquido não encontrado")
        
        # Validações de consistência
        bruto = data.get('salario_bruto', 0) or 0
        liquido = data.get('salario_liquido', 0) or 0
        descontos = data.get('descontos', 0) or 0
        
        if bruto and liquido and abs((bruto - descontos) - liquido) > 0.01:
            warnings.append("Inconsistência nos valores: Bruto - Descontos ≠ Líquido")
        
        if bruto and bruto < 0:
            validation_errors.append("Salário bruto não pode ser negativo")
        
        if liquido and liquido < 0:
            validation_errors.append("Salário líquido não pode ser negativo")
        
        # Validação de CPF
        cpf = data.get('cpf', '')
        if cpf and not self.validate_cpf(cpf):
            warnings.append("CPF pode estar incorreto")
        
        return {
            'is_valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'warnings': warnings
        }
    
    def validate_cpf(self, cpf):
        """Valida CPF usando algoritmo oficial"""
        # Remove formatação
        cpf_digits = re.sub(r'[^\d]', '', cpf)
        
        if len(cpf_digits) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf_digits == cpf_digits[0] * 11:
            return False
        
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf_digits[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        soma = sum(int(cpf_digits[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return cpf_digits[9] == str(digito1) and cpf_digits[10] == str(digito2)
    
    def create_summary_dataframe(self, data_list):
        """Cria DataFrame resumo a partir de lista de dados extraídos"""
        if not data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list)
        
        # Reordenar colunas
        column_order = ['nome', 'periodo', 'empresa', 'cargo', 'cpf', 
                       'salario_bruto', 'descontos', 'salario_liquido', 
                       'data_processamento']
        
        # Manter apenas colunas que existem
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Converter valores monetários para formato brasileiro
        for col in ['salario_bruto', 'descontos', 'salario_liquido']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) and x != 0 else "R$ 0,00")
        
        return df 