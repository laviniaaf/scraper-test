# Shopee Scraper

Web scraper para coletar informações de produtos da shopee usando playwright.

## Descrição

Automação que coleta de dados de produtos da loja Shopee, incluindo:
- Nome do produto
- Preço
- Link do produto
- Screenshot da página do produto

## Funcionalidades

- Acessa a loja da Shopee 
- Seleciona produto aleatório
- Extrai nome, preço e URL
- Captura screenshot completo da página
- Salva dados em CSV

## Instalação

### Pré-requisitos
- Python 3.12+
- pip

### Configurar ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual 
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar navegadores do Playwright
playwright install
```

## Como usar

- Abrir o ambiente virtual:
source .venv/bin/activate

- Rodar o sricpt do scraper:
python -m scripts.run_scraper

### Executar testes

```bash
# Testes unitários
pytest tests/test_shopee_scraper.py -v

# Com cobertura
pytest tests/test_shopee_scraper.py --cov=scraper --cov-report=html
```

## Saída

### CSV (`produtos.csv`)
Formato: `nome,preço,link`

### Screenshots
Salvos em `screenshots/produto_YYYYMMDD_HHMMSS.png`

### Tecnologias

- **Playwright** - Automação de navegador
- **Python 3.12** - Linguagem principal
- **pytest** - Framework de testes

