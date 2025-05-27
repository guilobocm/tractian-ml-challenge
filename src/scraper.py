import requests
from bs4 import BeautifulSoup
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_product_urls(limit=None):
    """
    Extrai URLs de produtos do catálogo da Baldor usando múltiplas estratégias
    """
    logging.info("Iniciando extração de URLs de produtos...")
    
    # Estratégia 1: Tentar extrair URLs reais da página de catálogo
    real_urls = extract_real_product_urls()
    
    # Estratégia 2: URLs baseadas em padrões conhecidos da Baldor (fallback)
    if not real_urls or len(real_urls) < (limit or 10):
        logging.info("Usando URLs de produtos baseadas em padrões conhecidos da Baldor...")
        sample_urls = get_sample_baldor_product_urls()
        real_urls.extend(sample_urls)
    
    # Remove duplicatas e limita resultado
    unique_urls = list(dict.fromkeys(real_urls))  # Remove duplicatas preservando ordem
    if limit:
        unique_urls = unique_urls[:limit]
    
    logging.info(f"Total de URLs selecionadas: {len(unique_urls)}")
    return unique_urls

def extract_real_product_urls():
    """
    Tenta extrair URLs reais usando Selenium
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    product_urls = []
    
    try:
        # Tenta diferentes páginas de entrada da Baldor
        entry_pages = [
            "https://www.baldor.com/catalog",
            "https://www.baldor.com/products",
            "https://www.baldor.com/motors"
        ]
        
        for page_url in entry_pages:
            try:
                logging.info(f"Tentando extrair URLs de: {page_url}")
                driver.get(page_url)
                time.sleep(3)  # Aguarda carregar
                
                # Múltiplos seletores
                product_selectors = [
                    "a[href*='/catalog/']",
                    "a[href*='/product/']",
                    "a[href*='/motors/']",
                    ".product-link",
                    ".product-item a",
                    "[data-product-id] a",
                    "a[href*='motor']",
                    "a[href*='baldor']"
                ]
                
                for selector in product_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            href = element.get_attribute('href')
                            if href and is_valid_product_url(href):
                                product_urls.append(href)
                    except:
                        continue
                
                if product_urls:
                    break  # Se encontrou URLs, para de tentar outras páginas
                    
            except Exception as e:
                logging.debug(f"Erro ao processar {page_url}: {e}")
                continue
        
    except Exception as e:
        logging.error(f"Erro geral na extração: {e}")
    finally:
        driver.quit()
    
    return list(set(product_urls))  # Remove duplicatas

def get_sample_baldor_product_urls():
    """
    Retorna URLs de produtos baseadas em padrões conhecidos da Baldor
    Estas são URLs reais de produtos industriais da Baldor
    """
    sample_urls = [
        "https://www.baldor.com/catalog/M3546T",
        "https://www.baldor.com/catalog/L3514T", 
        "https://www.baldor.com/catalog/M2513T",
        "https://www.baldor.com/catalog/VM3554T",
        "https://www.baldor.com/catalog/L1408T",
        "https://www.baldor.com/catalog/M3711T",
        "https://www.baldor.com/catalog/VM3615T",
        "https://www.baldor.com/catalog/L1510T",
        "https://www.baldor.com/catalog/M2394T",
        "https://www.baldor.com/catalog/VM3709T",
        "https://www.baldor.com/catalog/L3609T",
        "https://www.baldor.com/catalog/M3158T"
    ]
    
    # Verifica quais URLs respondem corretamente
    valid_urls = []
    for url in sample_urls:
        if verify_url_accessibility(url):
            valid_urls.append(url)
    
    return valid_urls

def verify_url_accessibility(url):
    """
    Verifica se uma URL está acessível
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def is_valid_product_url(url):
    """
    Verifica se uma URL parece ser de um produto válido
    """
    if not url:
        return False
    
    # Deve ser da Baldor e conter indicadores de produto
    if 'baldor.com' not in url:
        return False
    
    product_indicators = ['/catalog/', '/product/', '/motors/']
    if not any(indicator in url for indicator in product_indicators):
        return False
    
    # Evita URLs genéricas
    exclude_patterns = ['/search', '/category', '/index', '/home', '/about']
    if any(pattern in url for pattern in exclude_patterns):
        return False
    
    return True
