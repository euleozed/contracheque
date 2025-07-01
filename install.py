#!/usr/bin/env python3
"""
Script de instalação e verificação do ambiente para o Leitor de Contracheques
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("=" * 60)
    print("📑 LEITOR DE CONTRACHEQUES - INSTALAÇÃO")
    print("=" * 60)

def check_python_version():
    """Verifica a versão do Python"""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("⚠️  É necessário Python 3.8 ou superior")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_requirements():
    """Instala as dependências do requirements.txt"""
    print("\n📦 Instalando dependências...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def check_tesseract():
    """Verifica se o Tesseract está instalado"""
    print("\n🔍 Verificando Tesseract OCR...")
    
    try:
        result = subprocess.run(
            ["tesseract", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ Tesseract não encontrado no PATH")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Tesseract não encontrado")
        return False

def check_tesseract_languages():
    """Verifica se os idiomas necessários estão instalados"""
    print("🌐 Verificando idiomas do Tesseract...")
    
    try:
        result = subprocess.run(
            ["tesseract", "--list-langs"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            languages = result.stdout.strip().split('\n')[1:]  # Primeira linha é "List of available languages"
            
            required_langs = ['eng', 'por']
            missing_langs = []
            
            for lang in required_langs:
                if lang in languages:
                    print(f"✅ Idioma {lang} disponível")
                else:
                    print(f"❌ Idioma {lang} não encontrado")
                    missing_langs.append(lang)
            
            if missing_langs:
                print(f"⚠️  Idiomas faltando: {', '.join(missing_langs)}")
                show_tesseract_install_instructions()
                return False
            
            return True
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Não foi possível verificar idiomas")
        return False

def show_tesseract_install_instructions():
    """Mostra instruções de instalação do Tesseract"""
    system = platform.system().lower()
    
    print("\n📋 INSTRUÇÕES DE INSTALAÇÃO DO TESSERACT:")
    print("-" * 50)
    
    if system == "windows":
        print("🪟 Windows:")
        print("1. Baixe o instalador do Tesseract:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Execute o instalador como administrador")
        print("3. Certifique-se de marcar a opção para adicionar ao PATH")
        print("4. Instale o pacote de idioma português")
        
    elif system == "linux":
        print("🐧 Linux (Ubuntu/Debian):")
        print("sudo apt update")
        print("sudo apt install tesseract-ocr tesseract-ocr-por")
        
    elif system == "darwin":
        print("🍎 macOS:")
        print("brew install tesseract tesseract-lang")

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = ["temp", "exports"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Diretório '{directory}' criado/verificado")

def test_imports():
    """Testa se as importações principais funcionam"""
    print("\n🧪 Testando importações...")
    
    try:
        import streamlit
        print("✅ Streamlit - OK")
        
        import pytesseract
        print("✅ Pytesseract - OK")
        
        import pdf2image
        print("✅ PDF2Image - OK")
        
        import pandas
        print("✅ Pandas - OK")
        
        import plotly
        print("✅ Plotly - OK")
        
        import cv2
        print("✅ OpenCV - OK")
        
        # Testar importações dos módulos do projeto
        from config import APP_CONFIG
        print("✅ Config - OK")
        
        from utils import OCRProcessor, DataExtractor, Database
        print("✅ Utils - OK")
        
        from components import FileUploader, DataDisplay
        print("✅ Components - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def run_basic_test():
    """Executa um teste básico do sistema"""
    print("\n🎯 Executando teste básico...")
    
    try:
        from config import create_required_folders
        create_required_folders()
        print("✅ Criação de pastas - OK")
        
        from utils import Database
        db = Database()
        stats = db.get_summary_statistics()
        print("✅ Conexão com banco de dados - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        return False

def show_next_steps():
    """Mostra os próximos passos"""
    print("\n" + "=" * 60)
    print("🎉 INSTALAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print("\n🚀 Para executar a aplicação:")
    print("streamlit run app.py")
    print("\n📖 Para mais informações, consulte o README.md")
    print("\n🌐 A aplicação abrirá automaticamente no navegador")
    print("   URL padrão: http://localhost:8501")

def main():
    print_header()
    
    success = True
    
    # Verificações básicas
    success &= check_python_version()
    
    # Instalação de dependências
    if success:
        success &= install_requirements()
    
    # Verificações de ferramentas externas
    tesseract_ok = check_tesseract()
    if tesseract_ok:
        check_tesseract_languages()
    else:
        show_tesseract_install_instructions()
        success = False
    
    # Configuração do ambiente
    if success:
        create_directories()
        success &= test_imports()
        success &= run_basic_test()
    
    # Resultado final
    if success:
        show_next_steps()
    else:
        print("\n❌ Instalação incompleta. Resolva os problemas acima e execute novamente.")
        print("💡 Consulte o README.md para mais detalhes sobre a instalação.")

if __name__ == "__main__":
    main() 