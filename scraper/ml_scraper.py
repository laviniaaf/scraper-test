import csv
import time
import os
import random
import logging
from typing import List, Optional
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def human_pause(min_s: float = 0.3, max_s: float = 1.2) -> None:
    """
    Simula o tempo que um usuário real levaria para ler ou decidir uma ação (tempo min_s e max_s segundos)
    """
    time.sleep(random.uniform(min_s, max_s))


def human_scroll(page, distance: int = 500) -> None:
    """
    Rola a página simulando scroll humano
    
    Args:
        page: Objeto page do Playwright
        distance: Distância total em pixels (positivo = rolar para baixo, negativo = para cima)
    
    A função divide o scroll em varios passos pequenos e aleatórios,
    com pausas, imitando o comportamento de scroll de um user real
    """
    remaining = distance
    direction = 1 if remaining > 0 else -1  # 1 para baixo, -1 para cima
    
    # Continuar rolando até completar a distância total
    while abs(remaining) > 0:
        step = min(200, abs(remaining))
        if step < 50:
            step = abs(remaining)
        step = random.randint(min(50, step), step)
        
        try:
            page.mouse.wheel(0, direction * step)
        except Exception:
            pass
        
        remaining -= direction * step
        time.sleep(random.uniform(0.05, 0.25))


class MLScraper:
    """Scraper para produtos do Mercado Livre usando Playwright."""

    def _close_overlay_if_present(self, page) -> bool:
        """
        Tentativa de localizar e fechar modais/overlays que podem aparecer na página.
        
        Args:
            page: Objeto page do Playwright
            
        Returns:
            True se conseguiu fechar algum overlay, False caso contrário
        
        Tenta múltiplos seletores CSS comuns usados pelo Mercado Livre para botões de fechar.
        Usa movimento de mouse humano antes de clicar para parecer mais natural.
        """
        # lista de seletores CSS para botões de fechar os modais
        close_selectors = [
            "button[aria-label='Fechar']",
            "button[aria-label='close']",
            "button[aria-label='Close']",
            ".andes-modal__close",
            ".ui-pdp-dialog__close",
            ".modal-close",
            "button[data-testid='close']",
            "button:has-text('Fechar')",
            "button:has-text('Fechar ventana')",
        ]

        # Tentar cada seletor até encontrar um elemento visível
        for sel in close_selectors:
            try:
                el = page.query_selector(sel)    # busca elemento pelo seletor CSS
                
                if el:
                    # Obter coordenadas do elemento na página
                    box = el.bounding_box()
                    if box:
                        human_pause(0.2, 0.6)
                        try:
                            el.click()
                        except Exception:
                            # clicar diretamente no centro do elemento
                            cx = box["x"] + box["width"] / 2
                            cy = box["y"] + box["height"] / 2
                            page.mouse.click(cx, cy)
                        
                        human_pause(0.5, 1.5)
                        print(f"Fechou overlay com seletor: {sel}")
                        return True
            except Exception:
                continue  

        return False

    def _click_banner_if_present(self, page) -> bool:
        """
        Tenta localizar e clicar em um banner promocional se presente na página.
        
        Args:
            page: Objeto page do Playwright
            
        Returns:
            True se conseguiu clicar no banner, False cse não
        """
        banner_selectors = [
            "img[alt*='Banner']",
            "img[alt*='banner']",
            "img[src*='mercadolivre']",
            "img[src*='mlb-s3']",
            "div.promotions img",
        ]

        # Tentar cada seletor de banner
        for sel in banner_selectors:
            try:
                el = page.query_selector(sel)
                
                # Verificar se elemento existe e está visível na página
                if el and el.is_visible():
                    box = el.bounding_box()
                    if box:
                        human_pause(0.2, 0.6)
                        try:
                            el.click()
                        except Exception:
                            # clicar diretamente no centro do banner
                            cx = box["x"] + box["width"] / 2
                            cy = box["y"] + box["height"] / 2
                            page.mouse.click(cx, cy)
                        
                        human_pause(1.0, 2.0)
                        print(f"Clicou no banner com seletor: {sel}")
                        return True
            except Exception:
                continue  

        return False  

    def scrape_produto(self, url: str = "https://www.mercadolivre.com.br/ofertas/decoracao-de-natal?DEAL_ID=&S=MKT&V=1&T=DCVY&L=CM_MLB_FH_VERTICAL_NATALDECO_NOV_SEG"):
        """
        Método principal: acessa loja, seleciona produto aleatório e extrai dados.
        
        Args:
            url: URL inicial para navegar no Mercado Livre Brasil 
            
        O método realiza as seguintes etapas:
        1. Configura e lança navegador com anti-detecção
        2. Navega até a página da loja
        3. Localiza produtos disponíveis usando múltiplos seletores
        4. Seleciona um produto aleatório
        5. Clica no produto e extrai nome e preço
        6. Captura screenshot do produto
        7. Salva dados em CSV
        """
        with sync_playwright() as p:

            browser = p.firefox.launch(headless=True, slow_mo=50)

            # configuração do contexto do navegador 
            context = browser.new_context(
                viewport={"width": 1380, "height": 900},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            # script de anti-detecção 
            context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR','pt','en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Linux x86_64'});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            """)

            page = context.new_page()
            
            # uso de cabeçalhos HTTP para simular o tráfego brasileiro
            page.set_extra_http_headers({
                "Referer": "https://www.google.com.br/",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "DNT": "1",
            })

            logger.info(f"------> Acessando a loja: {url}")
          
            page.goto(url, 
                      timeout=60000, 
                      wait_until="domcontentloaded")

            # para simular comportamento humano
            human_pause(3, 6)  
            human_scroll(page, 
                         distance=random.randint(300, 800))
            human_pause(1, 2)

            try:
                self._close_overlay_if_present(page)
                human_pause(0.5, 1.2)
            except Exception:
                pass  

            logger.info("---> Procurando produtos na página...")
            
            # Lista de seletores CSS para produtos do ml (tentativa de varios seletores pois a estrutura HTML pode variar)
            produtos = []
            
            selectors_to_try = [
                "a.ui-search-link",  
                "li.ui-search-layout__item a.ui-search-link",
                "a[href*='/p/']",  #  (produto)
                ".ui-search-result__content",
            ]
            
            # para cada seletor até encontrar produtos
            for selector in selectors_to_try:
                produtos = page.locator(selector).all()
                if produtos:
                    logger.info(f"Encontrados {len(produtos)} produtos com seletor: {selector}")
                    break  
            
            if not produtos:
                logger.warning("Nenhum produto encontrado! Verifique os seletores.")
                return

            produto = random.choice(produtos) # produto aleatório da lista
            
            human_pause(0.5, 1.5)
            
            logger.info("Clicando em um produto aleatório.........")
            
            try:
                produto.click(timeout=10000)
            except Exception:
                # Fallback: se clicar falhar, tentar navegar diretamente pela URL
                try:
                    href = produto.get_attribute("href")
                    if href:
                        # Se URL for relativa, adicionar domínio do ML
                        if not href.startswith("http"):
                            href = "https://www.mercadolivre.com.br" + href
                        page.goto(href, timeout=60000, wait_until="domcontentloaded")
                except Exception as e:
                    logger.error(f"Erro ao clicar no produto: {e}")
                    browser.close()
                    return

            # Aguardar o carregamento completo da página do produto
            
            human_pause(3, 5)
            page.wait_for_load_state("domcontentloaded", 
                                     timeout=30000)  # Aguardar DOM
            
            human_scroll(page, 
                         distance=random.randint(200, 500))
            human_pause(1, 2)

            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)  
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"mercado_{timestamp}.png")
            
            try:
                page.screenshot(path=screenshot_path, 
                                full_page=True)  # full_page=True captura tudo
                logger.info(f"Screenshot salvo em: {screenshot_path}")
            except Exception as e:
                logger.error(f"Erro ao salvar screenshot: {e}")
            
            # para extrair nome do produto
            nome = "NOME NÃO ENCONTRADO"  
            
            # seletores CSS possíveis para o título do produto 
            nome_selectors = [
                "h1.ui-pdp-title",
                "h1[itemprop='name']",
                "h1",
                "span.ui-pdp-title",
            ]
            
            logger.info("Tentando extrair nome do produto......")

            for sel in nome_selectors:
                try:
                    # Buscar primeiro elemento que corresponda ao seletor
                    nome = page.locator(sel).first.inner_text(timeout=5000)
                    if nome and len(nome) > 3:
                        break  
                except Exception:
                    continue  

            # para extrair preço do produto
            preco = "PREÇO NÃO ENCONTRADO"  
            
            # Lseletores CSS possíveis para preço 
            preco_selectors = [
                "span.price-tag-fraction",
                "span.price-tag-symbol",
                "span.price-tag-amount",
                "div.ui-pdp-price__second-line",
                "[class*='price-tag']",
                "div.andes-money-amount", # andes classes
            ]
            
            logger.info("Tentando extrair o preço......")
            
            for sel in preco_selectors:
                try:
                    # Buscar todos os elementos que correspondam
                    elementos = page.locator(sel).all()
                    
                    # Verificar os primeiros 5 elementos encontrados
                    for el in elementos[:5]:
                        try:
                            texto = el.inner_text(timeout=2000)
                            
                            # Valida se o texto parece ser um preço
                            if texto and ("R$" in texto or "$" in texto or any(char.isdigit() for char in texto)):
                                preco = texto.strip()
                                logger.info(f"Preço encontrado com seletor: {sel}")
                                break  
                        except Exception:
                            continue  

                    if preco != "PREÇO NÃO ENCONTRADO":
                        break
                except Exception:
                    continue  
            
            # busca genérica por texto com símbolos de moeda
            if preco == "PREÇO NÃO ENCONTRADO":
                try:
                    # Buscar qualquer elemento contendo R$ ou dígitos usando regex
                    preco_el = page.locator(r"text=/R\$|\$|\d{2,}/").first
                    preco = preco_el.inner_text(timeout=3000).strip()
                    logger.info(f"---> Preço encontrado via texto regex.....")
                except Exception:
                    pass  # mantem "PREÇO NÃO ENCONTRADO" se falhar

            
            link_produto = page.url   # get da URL completa da página do produto
            
            logger.info(f"\nProduto encontrado:")
            logger.info(f"Nome: {nome}")
            logger.info(f"Preço: {preco}")
            logger.info(f"Link: {link_produto}")

            with open("produtos.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([nome, preco, link_produto])

            logger.info("\nDados salvos em produtos.csv")
            browser.close()
            logger.info("Navegador fechado.")