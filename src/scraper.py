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
    Extrai URLs de produtos do catálogo da Baldor usando Selenium para lidar com JavaScript
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa em modo headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    product_urls = []
    
    try:
        # Navega para a página de catálogo
        base_url = "https://www.baldor.com/catalog"
        logging.info(f"Navegando para: {base_url}")
        driver.get(base_url)
        
        # Aguarda a página carregar
        wait = WebDriverWait(driver, 15)
        
        # Tenta diferentes estratégias para encontrar produtos
        product_selectors = [
            "a[href*='/catalog/']",
            ".product-link",
            ".product-item a",
            "[data-product-id] a",
            "a[href*='product']",
            ".catalog-item a"
        ]
        
        products_found = []
        for selector in product_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logging.info(f"Encontrado {len(elements)} elementos com seletor: {selector}")
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/catalog/' in href and href not in products_found:
                            products_found.append(href)
                    break
            except Exception as e:
                logging.debug(f"Seletor {selector} falhou: {e}")
                continue
        
        # Se não encontrou produtos com seletores específicos, tenta buscar todos os links
        if not products_found:
            logging.info("Tentando buscar todos os links da página...")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                href = link.get_attribute('href')
                if href and 'baldor.com' in href and ('/product/' in href or '/catalog/' in href):
                    if href not in products_found:
                        products_found.append(href)
        
        # Limita o resultado se especificado
        if limit:
            products_found = products_found[:limit]
            
        product_urls = products_found
        logging.info(f"Total de URLs encontradas: {len(product_urls)}")
        
    except Exception as e:
        logging.error(f"Erro ao extrair URLs: {e}")
        
        # Fallback: tenta com requests + BeautifulSoup
        try:
            logging.info("Tentando fallback com requests...")
            response = requests.get("https://www.baldor.com/catalog", timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Busca por links que possam ser produtos
            links = soup.find_all('a', href=True)
            fallback_urls = []
            for link in links:
                href = link['href']
                if '/product/' in href or '/catalog/' in href:
                    if not href.startswith('http'):
                        href = f"https://www.baldor.com{href}"
                    fallback_urls.append(href)
            
            if limit:
                fallback_urls = fallback_urls[:limit]
            product_urls = fallback_urls
            logging.info(f"Fallback encontrou {len(product_urls)} URLs")
            
        except Exception as fallback_error:
            logging.error(f"Fallback também falhou: {fallback_error}")
            
    finally:
        driver.quit()
    
    return product_urls
