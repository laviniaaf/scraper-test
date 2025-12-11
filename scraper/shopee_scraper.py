import csv
import random
import time
import os
from typing import List, Optional, Dict
from playwright.sync_api import sync_playwright


def human_pause(min_s: float = 0.3, max_s: float = 1.2) -> None:
    """
    Simula o tempo que um usuário real levaria para ler ou decidir uma ação (tempo min_s e max_s segundos)
    """
    time.sleep(random.uniform(min_s, max_s))

def human_move_mouse(page, start: tuple, end: tuple, steps: int = 20) -> None:
    """
    Move o mouse de forma suave e natural do ponto inicial ao ponto final.
    
    Args:
        page: Objeto page do Playwright
        start: Tupla (x, y) com coordenadas iniciais
        end: Tupla (x, y) com coordenadas finais
        steps: Número de passos intermediários (mais passos = movimento mais suave)
    
    Usa uma curva ease-in-out para acelerar no início e desacelerar no fim,
    simulando movimento natural e add desvios aleatórios (jitter) para
    parecer mais humano.
    """
    sx, sy = start
    ex, ey = end
    
    # interpolar posição do mouse em varios passos
    for i in range(1, steps + 1):
        t = i / steps  # progresso de 0 a 1
        
        # Aplicar curva ease-in-out: acelera no início, desacelera no fim
        # Fórmula: 3t² - 2t³ com movimento suave
        easing = 3 * t * t - 2 * t * t * t
        
        # Calcular posição com desvio aleatório (jitter)
        ix = sx + (ex - sx) * easing + random.uniform(-1.5, 1.5)
        iy = sy + (ey - sy) * easing + random.uniform(-1.5, 1.5)
        
        try:
            page.mouse.move(ix, iy)
        except Exception:
            pass  
    
        time.sleep(random.uniform(0.005, 0.02))  # pausa curta entre cada passo do movimento


def human_scroll(page, distance: int = 500) -> None:
    """
    Rola a página de forma gradual e natural, simulando scroll humano.
    
    Args:
        page: Objeto page do Playwright
        distance: Distância total em pixels (positivo = rolar para baixo, negativo = para cima)
    
    A função divide o scroll em múltiplos passos pequenos e aleatórios,
    com pausas entre eles, imitando o comportamento de scroll de um usuário real.
    """
    remaining = distance
    direction = 1 if remaining > 0 else -1  # 1 para baixo, -1 para cima
    
    # Continuar rolando até completar a distância total
    while abs(remaining) > 0:
        step = min(200, abs(remaining)) #tamanho do passo: max de 200px 
        
        # Se restar menos de 50px, usar o que sobrou
        if step < 50:
            step = abs(remaining)
        
        step = random.randint(min(50, step), step) # add variação aleatória ao tamanho do passo
        
        # Executar o scroll
        try:
            page.mouse.wheel(0, direction * step)
        except Exception:
            pass  
        remaining -= direction * step  # atualiza a distância restante
        time.sleep(random.uniform(0.05, 0.25)) # pausa entre cada passo (50-250ms)


class ShopeeScraper:
    """
    Classe principal para scraping de produtos da Shopee Argentina.
    """
    
    def __init__(self):
        """Inicializa o scraper
        """
        self.proxy = None
        self.storage_state_path = None
    
    def _close_overlay_if_present(self, page) -> bool:
        """
        Tenta localizar e fechar modais/overlays que podem aparecer na página.
        
        Args:
            page: Objeto page do Playwright
            
        Returns:
            True se conseguiu fechar algum overlay, False caso contrário
        
        Tenta múltiplos seletores CSS comuns usados pela Shopee para botões de fechar.
        Usa movimento de mouse humano antes de clicar para parecer mais natural.
        """
        # seletores CSS para botões de fechar modais
        close_selectors = [
            "svg.V4lWQZ",  
            "button[aria-label='Fechar']",  
            "button[aria-label='Close']",  
            ".shopee-modal__close", 
            ".modal-close", 
            "button[data-testid='close']",  
            "button:has-text('Fechar')",  
            "button:has-text('Close')",  
        ]

        # tenta cada seletor até encontrar um elemento visível
        for sel in close_selectors:
            try:
                # Buscar elemento pelo seletor CSS
                el = page.query_selector(sel)
                if el:
                    box = el.bounding_box() # Obter coordenadas do elemento na página
                    if box:
                        # centro do elemento
                        cx = box["x"] + box["width"] / 2
                        cy = box["y"] + box["height"] / 2
                        
                        # Mover mouse até o botão de fechar coemcando de posição aleatória na tela
                        human_move_mouse(
                            page, 
                            (random.randint(50, 200), random.randint(50, 200)),  # posição inicial
                            (cx, cy),  # posição do botão
                            steps=random.randint(8, 20)  # número de passos do movimento
                        )
                        human_pause(0.2, 0.6)
                        try:
                            el.click()
                        except Exception:
                            # Fallback: clicar diretamente nas coordenadas
                            page.mouse.click(cx, cy)
                        
                        human_pause(0.5, 1.5)
                        print(f"Fechou overlay com seletor: {sel}")
                        return True
            except Exception:
                continue  
        return False

    """def _click_banner_if_present(self, page) -> bool:
        
        Tenta localizar e clicar em um banner promocional se presente na página.
        
        Args:
            page: Objeto page do Playwright
            
        Returns:
            True se conseguiu clicar no banner, False caso contrário
        
        Útil para páginas que exibem banners de promoções/ofertas que precisam
        ser clicados para acessar conteúdo específico.
        
        # seletores para banners promocionais da Shopee
        banner_selectors = [
            "img.uXN1L5",  
            "img[alt='Banner']",  
            "img[alt=\"Banner\"]",  
            "img[src*='down-ar.img.susercontent.com']",  
        ]

        # Tentar cada seletor de banner
        for sel in banner_selectors:
            try:
                el = page.query_selector(sel)
                
                # Verificar se elemento existe e está visível na página
                if el and el.is_visible():
                    box = el.bounding_box()
                    
                    if box:
                        # Calcular centro do banner
                        cx = box["x"] + box["width"] / 2
                        cy = box["y"] + box["height"] / 2
                        
                        # Mover mouse até o banner
                        human_move_mouse(
                            page, 
                            (random.randint(50, 200), random.randint(50, 200)),
                            (cx, cy), 
                            steps=random.randint(8, 20)
                        )
                        human_pause(0.2, 0.6)
                        try:
                            el.click()
                        except Exception:
                            # Fallback: clicar diretamente nas coordenadas
                            page.mouse.click(cx, cy)
                        
                        human_pause(1.0, 2.0)
                        print(f"Clicou no banner com seletor: {sel}")
                        return True
            except Exception:
                continue  

        return False  """

    def scrape_produto(self, url: str = "https://shopee.com.ar/topick_global_ar.ar"):
        """
        Método principal de scraping: acessa loja, seleciona produto aleatório e extrai dados.
        
        Args:
            url: URL da loja na Shopee Argentina (padrão: topick_global_ar.ar)
        
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
            browser = p.firefox.launch(headless=False, slow_mo=50, proxy=self.proxy) if self.proxy else p.firefox.launch(headless=False, slow_mo=50)
            
            # contexto do navegador para Argentina
            context_args = dict(
                viewport={"width": 1380, "height": 900},
                locale="es-AR",  
                timezone_id="America/Argentina/Buenos_Aires"
            )
            
            context = browser.new_context(**context_args)

            # script anti-detecção 
            context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'languages', {get: () => ['es-AR','es','en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Linux x86_64'});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            """)

            page = context.new_page()
            
            #  cabeçalhos HTTP para simular tráfego argentino
            page.set_extra_http_headers({
                "Referer": "https://www.google.com.ar/",  
                "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                "DNT": "1",
            })

            print(f"---> Acessando loja: {url}")
            page.goto(url, 
                      timeout=60000, 
                      wait_until="domcontentloaded")

            human_pause(3, 6)  
            human_scroll(page, 
                         distance=random.randint(300, 800))
            human_pause(1, 2)
            try:
                self._close_overlay_if_present(page)
                human_pause(0.5, 1.2)
            except Exception:
                pass  


            print("---> Procurando produtos na página...")    
            produtos = []
            selectors_to_try = [
                "a[href*='/product/']",  
                "div[data-sqe='item']",  
                ".shop-search-result-view__item", 
            ]
            
            # tentativa de cada seletor até encontrar produtos
            for selector in selectors_to_try:
                produtos = page.locator(selector).all()
                if produtos:
                    print(f"Encontrados {len(produtos)} produtos com seletor: {selector}")
                    break  
            
            if not produtos:
                print("Nenhum produto encontrado! Verifique os seletores.")
                return

            produto = random.choice(produtos) 
            
            # simular movimento de mouse até o produto 
            try:
                # posição do elemento na tela
                box = produto.bounding_box()
                if box:
                    #  centro do elemento
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2
                    
                    # move do ponto aleatório até o produto
                    human_move_mouse(
                        page, 
                        (random.randint(100, 300), random.randint(100, 300)), 
                        (cx, cy), 
                        steps=random.randint(15, 25)
                    )
                    human_pause(0.5, 1.5)  
            except Exception:
                pass  

            print("---> Clicando em produto aleatório...")
            try:
                produto.click(timeout=10000)
            except Exception:
                try:
                    href = produto.get_attribute("href")
                    if href:
                        # se URL for relativa add dominio
                        if not href.startswith("http"):
                            href = "https://shopee.com.ar" + href
                        page.goto(href, timeout=60000, wait_until="domcontentloaded")
                except Exception as e:
                    print(f"Erro ao clicar no produto: {e}")
                    browser.close()
                    return


            human_pause(3, 5) 
            page.wait_for_load_state("domcontentloaded", 
                                     timeout=30000)  
            human_scroll(page, 
                         distance=random.randint(200, 500))
            human_pause(1, 2)

            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, 
                        exist_ok=True)  
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"produto_{timestamp}.png")

            try:
                page.screenshot(path=screenshot_path, 
                                full_page=True)  
                print(f"Screenshot salvo em: {screenshot_path}")
            except Exception as e:
                print(f"Erro ao salvar screenshot: {e}")

            nome = "NOME NÃO ENCONTRADO"  
            
            # seletores CSS possíveis para o título do produto
            nome_selectors = [
                "span.qaNIZv",  
                "h1",  
                "div[class*='title']",  
                "span[class*='product-title']",  
            ]
 
            for sel in nome_selectors:
                try:
                    nome = page.locator(sel).first.inner_text(timeout=5000) # primeiro elemento que corresponda ao seletor
                    
                    # se o nome for valido
                    if nome and len(nome) > 3:
                        break 
                except Exception:
                    continue 
            
            print("-----> Tentando extrair nome do produto...")
            preco = "PREÇO NÃO ENCONTRADO"  
            # seletores CSS possíveis para preço
            preco_selectors = [
                "div.pmmxKx",  # Classe específica da Shopee para preço
                "div[class*='price']",  
                "span[class*='price']",  
                "div.price",  
                "[class*='PriceSection']",  
                "[class*='product-price']",  
                "div[data-testid='lblProductPrice']",  # Atributo de teste
            ]
            
            print("-----> Tentando extrair preço...")
            for sel in preco_selectors:
                try:
                    # Buscar todos os elementos que correspondam
                    elementos = page.locator(sel).all()
                    for el in elementos[:5]:
                        try:
                            texto = el.inner_text(timeout=2000)
                            
                            # Validar se o texto parece ser um preço contendo $ ou qualquer dígito
                            if texto and ("$" in texto or "AR" in texto or any(char.isdigit() for char in texto)):
                                preco = texto.strip()
                                print(f"Preço encontrado com seletor: {sel}")
                                break  
                        except Exception:
                            continue  

                    if preco != "PREÇO NÃO ENCONTRADO":
                        break
                except Exception:
                    continue  
            
            if preco == "PREÇO NÃO ENCONTRADO":
                try:
                    # busca de qualquer elemento contendo $, AR$ ou ARS usando regex
                    preco_el = page.locator("text=/\\$|AR\\$|ARS/").first
                    preco = preco_el.inner_text(timeout=3000).strip()
                    print(f"---> Preço encontrado via texto regex")
                except Exception:
                    pass  

            link_produto = page.url
            
            print(f"\nProduto encontrado:")
            print(f"Nome: {nome}")
            print(f"Preço: {preco}")
            print(f"Link: {link_produto}")

            with open("produtos.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([nome, preco, link_produto])

            print("\nDados salvos em produtos.csv")
            browser.close()
            print("Navegador fechado.")