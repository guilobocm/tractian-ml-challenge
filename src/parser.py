import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urljoin, urlparse
import time

def safe_extract_text(element, default=""):
    """Extrai texto de um elemento de forma segura"""
    if element:
        return element.get_text(strip=True)
    return default

def safe_extract_attr(element, attr, default=""):
    """Extrai atributo de um elemento de forma segura"""
    if element and element.has_attr(attr):
        return element[attr]
    return default

def parse_product_page(url):
    """
    Faz parsing de uma página de produto da Baldor
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Fazendo parsing da página: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extrai ID do produto - tenta múltiplas estratégias
        product_id = extract_product_id(soup, url)
        
        # Extrai nome do produto
        name = extract_product_name(soup)
        
        # Extrai descrição
        description = extract_description(soup)
        
        # Extrai especificações
        specs = extract_specifications(soup)
        
        # Extrai BOM (Bill of Materials)
        bom = extract_bom(soup)
        
        # Extrai assets (manual, CAD, imagens)
        assets = extract_assets(soup, url)
        
        result = {
            'product_id': product_id,
            'name': name,
            'description': description,
            'specs': specs,
            'bom': bom,
            'assets': assets
        }
        
        logging.info(f"Produto extraído com sucesso: {product_id}")
        return result
        
    except Exception as e:
        logging.error(f"Erro ao fazer parsing da página {url}: {e}")
        # Retorna estrutura básica mesmo em caso de erro
        return {
            'product_id': extract_id_from_url(url),
            'name': "Erro ao extrair nome",
            'description': "Erro ao extrair descrição",
            'specs': {},
            'bom': [],
            'assets': {},
            'source_url': url,
            'error': str(e)
        }

def extract_product_id(soup, url):
    """Extrai o ID do produto usando múltiplas estratégias"""
    # Estratégia 1: elemento com ID específico
    id_selectors = [
        '#product-id',
        '.product-id',
        '[data-product-id]',
        '.product-number',
        '.model-number'
    ]
    
    for selector in id_selectors:
        element = soup.select_one(selector)
        if element:
            text = safe_extract_text(element)
            if text:
                return clean_product_id(text)
            
            # Tenta extrair de atributo data
            data_id = safe_extract_attr(element, 'data-product-id')
            if data_id:
                return clean_product_id(data_id)
    
    # Estratégia 2: busca no texto da página
    text_patterns = [
        r'Product\s*ID\s*[:\-]\s*([A-Z0-9\-]+)',
        r'Model\s*[:\-]\s*([A-Z0-9\-]+)',
        r'Part\s*Number\s*[:\-]\s*([A-Z0-9\-]+)'
    ]
    
    page_text = soup.get_text()
    for pattern in text_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            return clean_product_id(match.group(1))
    
    # Estratégia 3: extrai da URL
    return extract_id_from_url(url)

def extract_product_name(soup):
    """Extrai o nome do produto"""
    name_selectors = [
        'h1.product-name',
        'h1.product-title',
        '.product-name h1',
        '.product-title h1',
        'h1',
        '.main-title',
        '.product-header h1'
    ]
    
    for selector in name_selectors:
        element = soup.select_one(selector)
        if element:
            name = safe_extract_text(element)
            if name and len(name) > 3:  # Nome deve ter pelo menos 3 caracteres
                return name
    
    return "Nome não encontrado"

def extract_description(soup):
    """Extrai a descrição do produto"""
    desc_selectors = [
        '.description',
        '.product-description',
        '.product-details',
        '.overview',
        '.summary',
        '.product-summary'
    ]
    
    for selector in desc_selectors:
        element = soup.select_one(selector)
        if element:
            desc = safe_extract_text(element)
            if desc and len(desc) > 10:
                return desc
    
    return "Descrição não encontrada"

def extract_specifications(soup):
    """Extrai especificações técnicas"""
    specs = {}
    
    # Busca por tabelas de especificações
    spec_tables = soup.find_all('table', class_=re.compile(r'spec|specification|technical', re.I))
    
    for table in spec_tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                key = safe_extract_text(cols[0])
                value = safe_extract_text(cols[1])
                if key and value:
                    specs[key] = value
    
    # Se não encontrou tabelas, busca por listas de definição
    if not specs:
        dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            terms = dl.find_all('dt')
            descriptions = dl.find_all('dd')
            for term, desc in zip(terms, descriptions):
                key = safe_extract_text(term)
                value = safe_extract_text(desc)
                if key and value:
                    specs[key] = value
    
    return specs

def extract_bom(soup):
    """Extrai Bill of Materials"""
    bom = []
    
    # Busca por tabelas BOM
    bom_tables = soup.find_all('table', class_=re.compile(r'bom|bill.*material|parts', re.I))
    
    for table in bom_tables:
        rows = table.find_all('tr')[1:]  # Pula o cabeçalho
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                # Tenta extrair part_number, description e quantity conforme schema
                part_number = safe_extract_text(cols[0]) if len(cols) > 0 else ""
                description = safe_extract_text(cols[1]) if len(cols) > 1 else ""
                quantity_text = safe_extract_text(cols[2]) if len(cols) > 2 else "1"
                
                # Converte quantity para número
                try:
                    quantity = int(re.search(r'\d+', quantity_text).group()) if re.search(r'\d+', quantity_text) else 1
                except:
                    quantity = 1
                
                if part_number and description:
                    bom_entry = {
                        'part_number': part_number,
                        'description': description,
                        'quantity': quantity
                    }
                    bom.append(bom_entry)
    
    # Se não encontrou tabelas específicas de BOM, tenta extrair de listas ou outras estruturas
    if not bom:
        # Busca por listas que possam conter informações de BOM
        lists = soup.find_all('ul') + soup.find_all('ol')
        for ul in lists:
            if any(keyword in ul.get_text().lower() for keyword in ['part', 'component', 'material', 'assembly']):
                items = ul.find_all('li')
                for item in items[:5]:  # Limita a 5 itens para evitar ruído
                    text = safe_extract_text(item)
                    if text and len(text) > 5:  # Apenas itens com conteúdo substancial
                        # Tenta extrair part number do texto
                        part_match = re.search(r'([A-Z0-9\-]{3,})', text)
                        part_number = part_match.group(1) if part_match else f"PART_{len(bom)+1:03d}"
                        
                        bom_entry = {
                            'part_number': part_number,
                            'description': text[:100],  # Limita descrição
                            'quantity': 1
                        }
                        bom.append(bom_entry)
    
    return bom

def extract_assets(soup, base_url):
    """Extrai assets como manuais, CAD, imagens"""
    assets = {}
    
    # Busca por links de download
    download_patterns = {
        'manual': r'manual|instruction|guide|documentation',
        'cad': r'cad|dwg|step|iges|3d|model',
        'datasheet': r'datasheet|spec.*sheet|technical.*data',
        'certificate': r'certificate|cert|ul.*listing'
    }
    
    # Busca todos os links
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        link_text = safe_extract_text(link).lower()
        link_class = ' '.join(link.get('class', [])).lower()
        
        # Converte URL relativa para absoluta
        if not href.startswith('http'):
            href = urljoin(base_url, href)
        
        # Categoriza o link baseado no texto e classe
        for asset_type, pattern in download_patterns.items():
            if re.search(pattern, link_text + ' ' + link_class, re.IGNORECASE):
                # Verifica se é um arquivo (tem extensão)
                if re.search(r'\.(pdf|doc|docx|dwg|step|iges|jpg|jpeg|png|gif)$', href, re.IGNORECASE):
                    assets[asset_type] = href
                    break
    
    # Busca por imagens do produto
    img_selectors = [
        '.product-image img',
        '.main-image img',
        '.hero-image img',
        '.gallery img'
    ]
    
    for selector in img_selectors:
        imgs = soup.select(selector)
        for i, img in enumerate(imgs[:3]):  # Máximo 3 imagens
            src = safe_extract_attr(img, 'src')
            if src:
                if not src.startswith('http'):
                    src = urljoin(base_url, src)
                key = f'image_{i+1}' if i > 0 else 'image'
                assets[key] = src
    
    return assets

def clean_product_id(product_id):
    """Limpa e padroniza o ID do produto"""
    if not product_id:
        return "UNKNOWN"
    
    # Remove espaços e caracteres especiais desnecessários
    cleaned = re.sub(r'[^\w\-]', '', product_id.strip())
    return cleaned.upper() if cleaned else "UNKNOWN"

def extract_id_from_url(url):
    """Extrai ID do produto da URL como último recurso"""
    # Tenta extrair da URL padrões como /product/ABC123 ou /catalog/XYZ789
    patterns = [
        r'/product/([A-Z0-9\-]+)',
        r'/catalog/([A-Z0-9\-]+)',
        r'[?&]id=([A-Z0-9\-]+)',
        r'[?&]product=([A-Z0-9\-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return clean_product_id(match.group(1))
    
    # Como último recurso, usa parte da URL
    path_parts = urlparse(url).path.split('/')
    for part in reversed(path_parts):
        if part and len(part) > 2:
            return clean_product_id(part)
    
    return "UNKNOWN_ID"
