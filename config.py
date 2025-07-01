import os
import platform

# Configurações do Tesseract baseadas no sistema operacional
def get_tesseract_config():
    system = platform.system().lower()
    
    if system == "windows":
        # Configuração para Windows
        tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        tessdata_prefix = r"C:\Program Files\Tesseract-OCR"
        
        # Verificar se existe, senão usar paths alternativos
        if not os.path.exists(tesseract_cmd):
            # Tentar outros caminhos comuns no Windows
            alternative_paths = [
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\tesseract\tesseract.exe"
            ]
            for path in alternative_paths:
                if os.path.exists(path):
                    tesseract_cmd = path
                    tessdata_prefix = os.path.dirname(path)
                    break
    
    elif system == "linux":
        tesseract_cmd = "tesseract"  # Usar do PATH
        tessdata_prefix = "/usr/share/tesseract-ocr"
    
    elif system == "darwin":  # macOS
        tesseract_cmd = "/usr/local/bin/tesseract"
        tessdata_prefix = "/usr/local/share/tessdata"
    
    return tesseract_cmd, tessdata_prefix

# Configurações do Poppler
def get_poppler_config():
    system = platform.system().lower()
    
    if system == "windows":
        # Tentar encontrar poppler automaticamente
        possible_paths = [
            r"C:\Users\00840207255\Desktop\poppler-24.08.0\Library\bin",
            r"C:\poppler\bin",
            r"C:\Program Files\poppler\bin"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None  # Se não encontrar, deixar None (pdf2image tentará usar do PATH)
    
    return None  # Linux e macOS geralmente não precisam especificar

# Configurações da aplicação
APP_CONFIG = {
    "title": "📑 Leitor de Contracheques e Comprovantes",
    "version": "2.0.0",
    "author": "Sistema de Análise de Pagamentos",
    "database_file": "contracheques.db",
    "export_folder": "exports",
    "temp_folder": "temp"
}

# Configurações de OCR
OCR_CONFIG = {
    "languages": ["por", "eng"],  # Português e Inglês
    "confidence_threshold": 30,
    "preprocessing": True
}

# Padrões de regex para extração de dados
REGEX_PATTERNS = {
    "nome": [
        r"(?i)Nome\s*(?:do\s*)?(?:Funcion[aá]rio|Empregado|Colaborador)[:\s]*([A-ZÁÊÇÕ\s]+)",
        r"(?i)Funcion[aá]rio[:\s]*([A-ZÁÊÇÕ\s]+)",
        r"(?i)Nome[:\s]*([A-ZÁÊÇÕ\s]+)"
    ],
    "cpf": [
        r"(?i)CPF[:\s]*(\d{3}\.?\d{3}\.?\d{3}[-\.]?\d{2})",
        r"(\d{3}\.?\d{3}\.?\d{3}[-\.]?\d{2})"
    ],
    "periodo": [
        r"(?i)(?:Per[ií]odo|Compet[eê]ncia)[:\s]*(\d{2}/\d{4})",
        r"(?i)(?:Ref|M[eê]s)[:\s]*(\d{2}/\d{4})",
        r"(\d{2}/\d{4})"
    ],
    "salario_bruto": [
        r"(?i)(?:Sal[aá]rio|Bruto|Total\s*Bruto)[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)",
        r"(?i)Vencimentos[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
    ],
    "salario_liquido": [
        r"(?i)(?:Total\s*)?(?:L[ií]quido|Valor\s*L[ií]quido)[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)",
        r"(?i)(?:Valor\s*a\s*Receber|Receber)[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
    ],
    "descontos": [
        r"(?i)(?:Total\s*)?Descontos?[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)",
        r"(?i)(?:Dedu[çc][õo]es|INSS|IRRF)[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
    ],
    "empresa": [
        r"(?i)(?:Empresa|Raz[ãa]o\s*Social|Empregador)[:\s]*([A-ZÁÊÇÕ\s&\.-]+)",
        r"(?i)CNPJ[:\s]*\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\s*([A-ZÁÊÇÕ\s&\.-]+)"
    ],
    "cargo": [
        r"(?i)(?:Cargo|Fun[çc][ãa]o|Ocupa[çc][ãa]o)[:\s]*([A-ZÁÊÇÕ\s\.-]+)",
        r"(?i)CBO[:\s]*\d+\s*([A-ZÁÊÇÕ\s\.-]+)"
    ]
}

# Criar pastas necessárias
def create_required_folders():
    folders = [APP_CONFIG["export_folder"], APP_CONFIG["temp_folder"]]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder) 