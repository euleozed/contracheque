# 📑 Leitor de Contracheques e Comprovantes

Uma aplicação completa desenvolvida em Python com Streamlit para extrair, processar e analisar dados de contracheques e comprovantes de pagamento usando OCR (Reconhecimento Óptico de Caracteres).

## 🚀 Funcionalidades

### ✨ Principais Features

- **📤 Upload Múltiplo**: Suporte para upload único ou múltiplo de arquivos
- **🔍 OCR Avançado**: Extração de texto com pré-processamento de imagem
- **📋 Extração Inteligente**: Reconhecimento automático de campos como nome, CPF, salários, etc.
- **🗄️ Banco de Dados**: Armazenamento persistente em SQLite
- **📊 Análises Visuais**: Gráficos e relatórios interativos
- **✅ Validação de Dados**: Verificação automática de consistência
- **📈 Dashboard**: Interface moderna e intuitiva

### 📄 Formatos Suportados

- **PDF**: Contracheques escaneados
- **Imagens**: PNG, JPG, JPEG

### 🔍 Dados Extraídos

- Nome do funcionário
- CPF (com validação)
- Período/competência
- Empresa
- Cargo
- Salário bruto
- Descontos
- Salário líquido

## 🏗️ Estrutura do Projeto

```
leitor-contracheques/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações do sistema
├── requirements.txt            # Dependências
├── README.md                   # Documentação
├── utils/                      # Módulos utilitários
│   ├── __init__.py
│   ├── ocr_processor.py        # Processamento OCR
│   ├── data_extractor.py       # Extração de dados
│   └── database.py             # Gerenciamento do banco
├── components/                 # Componentes da interface
│   ├── __init__.py
│   ├── file_uploader.py        # Upload de arquivos
│   └── data_display.py         # Exibição de dados
├── exports/                    # Arquivos exportados
├── temp/                       # Arquivos temporários
└── contracheques.db           # Banco de dados SQLite
```

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos

#### Windows
- **Tesseract OCR**: Baixar e instalar do [GitHub oficial](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler**: Baixar do [repositório oficial](https://github.com/oschwartz10612/poppler-windows)

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por
sudo apt install poppler-utils
```

#### macOS
```bash
brew install tesseract tesseract-lang
brew install poppler
```

### 2. Instalação do Projeto

```bash
# Clone ou baixe o projeto
cd leitor-contracheques

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Tesseract

O arquivo `config.py` tenta encontrar automaticamente o Tesseract, mas você pode configurar manualmente:

```python
# Editar config.py se necessário
tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows
tessdata_prefix = r"C:\Program Files\Tesseract-OCR"
```

## 🚀 Como Usar

### 1. Executar a Aplicação

```bash
streamlit run app.py
```

### 2. Interface Principal

A aplicação possui 5 seções principais:

#### 📤 Processar Documentos
- Upload de arquivos (único ou múltiplo)
- Processamento via OCR
- Extração e validação de dados
- Visualização dos resultados
- Salvamento no banco de dados

#### 📊 Visualizar Dados
- Estatísticas gerais do banco
- Filtros por nome e período
- Tabelas interativas
- Exportação de dados

#### 📈 Análises e Relatórios
- Gráficos de distribuição salarial
- Análises temporais
- Estatísticas detalhadas
- Rankings de funcionários

#### ⚙️ Configurações
- Informações do sistema
- Ferramentas de manutenção
- Configurações gerais

#### 📋 Logs do Sistema
- Histórico de operações
- Logs de processamento
- Rastreamento de erros

## 🔧 Configurações Avançadas

### OCR

```python
# config.py
OCR_CONFIG = {
    "languages": ["por", "eng"],    # Idiomas
    "confidence_threshold": 30,     # Limite de confiança
    "preprocessing": True           # Pré-processamento
}
```

### Regex Patterns

O sistema usa padrões regex configuráveis para extrair dados:

```python
REGEX_PATTERNS = {
    "nome": [
        r"(?i)Nome\s*(?:do\s*)?(?:Funcion[aá]rio|Empregado)[:\s]*([A-ZÁÊÇÕ\s]+)"
    ],
    "salario_liquido": [
        r"(?i)(?:Total\s*)?(?:L[ií]quido|Valor\s*L[ií]quido)[:\s]*(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
    ]
    # ... outros padrões
}
```

## 📊 Banco de Dados

### Estrutura das Tabelas

#### contracheques
- Dados principais dos contracheques
- Informações de validação
- Metadados de processamento

#### logs
- Histórico de operações
- Rastreamento de erros
- Auditoria do sistema

#### configuracoes
- Configurações personalizadas
- Preferências do usuário

## 🔍 Validações

### Dados Obrigatórios
- Nome do funcionário
- Salário líquido

### Validações de Consistência
- Verificação de CPF
- Consistência matemática (bruto - descontos = líquido)
- Valores não negativos

### Qualidade do OCR
- Confiança mínima configurável
- Pré-processamento de imagem
- Fallback para OCR simples

## 📈 Análises Disponíveis

### Estatísticas Gerais
- Total de registros
- Funcionários únicos
- Períodos cobertos
- Confiança média do OCR

### Análises Salariais
- Distribuição de salários
- Estatísticas descritivas
- Comparações por empresa
- Rankings

### Análises Temporais
- Evolução salarial
- Tendências por período
- Sazonalidade

## 🔧 Solução de Problemas

### Erro: Tesseract não encontrado
```bash
# Verificar instalação
tesseract --version

# No Windows, verificar o PATH ou configurar manualmente no config.py
```

### Erro: Poppler não encontrado
```bash
# Linux/macOS
sudo apt install poppler-utils  # Ubuntu/Debian
brew install poppler           # macOS

# Windows: baixar e extrair o Poppler, configurar o caminho no config.py
```

### OCR com baixa qualidade
- Verificar qualidade da imagem
- Ajustar configurações de pré-processamento
- Usar imagens com maior resolução
- Verificar se o idioma português está instalado no Tesseract

### Problemas de Performance
- Processar arquivos menores
- Reduzir número de arquivos simultâneos
- Verificar disponibilidade de memória

## 📝 Changelog

### Versão 2.0.0
- ✨ Interface completamente refeita
- 🏗️ Arquitetura modular
- 📊 Sistema de análises avançado
- 🗄️ Banco de dados SQLite
- 📤 Upload múltiplo
- ✅ Validação de dados
- 📈 Gráficos interativos

### Versão 1.0.0
- 🔍 OCR básico
- 📋 Extração simples de dados
- 📄 Upload único de PDF

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para suporte ou dúvidas:
- Abra uma issue no repositório
- Consulte a documentação
- Verifique os logs do sistema na aplicação

## 🔮 Roadmap

### Próximas Funcionalidades
- 🌐 API REST
- 📧 Notificações por email
- 🔐 Sistema de autenticação
- 📱 Interface responsiva
- 🤖 IA para melhoria da extração
- 📊 Relatórios em PDF
- 🔄 Sincronização em nuvem 