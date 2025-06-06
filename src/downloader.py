import os
import aiohttp
import asyncio
import logging
from urllib.parse import urlparse, unquote
import mimetypes
from pathlib import Path

async def download_asset(session, url, save_path, max_retries=3):
    """
    Baixa um asset de forma assíncrona com retry e validação
    """
    for attempt in range(max_retries):
        try:
            logging.info(f"Baixando {url} para {save_path} (tentativa {attempt + 1})")
            
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    # Verifica o Content-Type para validar se é um arquivo válido
                    content_type = resp.headers.get('content-type', '')
                    content_length = resp.headers.get('content-length')
                    
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        if size_mb > 100:  # Arquivo muito grande (>100MB)
                            logging.warning(f"Arquivo muito grande ({size_mb:.1f}MB): {url}")
                            return False
                    
                    # Baixa o arquivo em chunks
                    with open(save_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    # Verifica se o arquivo foi criado e tem conteúdo
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                        logging.info(f"Download concluído: {save_path}")
                        return True
                    else:
                        logging.error(f"Arquivo vazio ou não criado: {save_path}")
                        return False
                        
                else:
                    logging.warning(f"HTTP {resp.status} ao baixar {url}")
                    if attempt == max_retries - 1:
                        return False
                    
        except asyncio.TimeoutError:
            logging.warning(f"Timeout ao baixar {url} (tentativa {attempt + 1})")
        except Exception as e:
            logging.error(f"Erro ao baixar {url} (tentativa {attempt + 1}): {e}")
            
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Backoff exponencial
    
    return False

async def download_assets(product_id, assets, output_dir):
    """
    Baixa todos os assets de um produto de forma assíncrona
    """
    if not assets:
        logging.info(f"Nenhum asset encontrado para o produto {product_id}")
        return
    
    product_dir = os.path.join(output_dir, sanitize_filename(product_id))
    os.makedirs(product_dir, exist_ok=True)
    
    logging.info(f"Baixando {len(assets)} assets para {product_dir}")
    
    # Configuração do cliente HTTP
    timeout = aiohttp.ClientTimeout(total=60, connect=10)
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=3)
    
    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    ) as session:
        tasks = []
        
        for asset_name, url in assets.items():
            if not url or not isinstance(url, str):
                logging.warning(f"URL inválida para asset {asset_name}: {url}")
                continue
                
            # Determina a extensão do arquivo
            file_extension = get_file_extension(url)
            safe_asset_name = sanitize_filename(asset_name)
            save_path = os.path.join(product_dir, f"{safe_asset_name}{file_extension}")
            
            # Evita sobrescrever arquivos existentes
            counter = 1
            original_save_path = save_path
            while os.path.exists(save_path):
                name_part = safe_asset_name
                save_path = os.path.join(product_dir, f"{name_part}_{counter}{file_extension}")
                counter += 1
            
            task = download_asset(session, url, save_path)
            tasks.append(task)
        
        # Executa todos os downloads em paralelo
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log dos resultados
            successful = sum(1 for r in results if r is True)
            failed = len(results) - successful
            
            logging.info(f"Downloads para {product_id}: {successful} sucessos, {failed} falhas")
        else:
            logging.warning(f"Nenhuma tarefa de download criada para {product_id}")

def get_file_extension(url):
    """
    Extrai a extensão do arquivo da URL de forma inteligente
    """
    # Remove parâmetros da query string
    url_path = urlparse(url).path
    url_path = unquote(url_path)  # Decodifica URL encoding
    
    # Tenta extrair extensão do caminho
    _, ext = os.path.splitext(url_path)
    
    if ext and len(ext) <= 5:  # Extensão válida (.pdf, .dwg, etc.)
        return ext.lower()
    
    # Extensões comuns baseadas em palavras-chave
    common_extensions = {
        'manual': '.pdf',
        'cad': '.dwg',
        'image': '.jpg',
        'datasheet': '.pdf',
        'certificate': '.pdf',
    }

    lower_url = (url_path + urlparse(url).query).lower()
    for key, default_ext in common_extensions.items():
        if key in lower_url:
            return default_ext

    # Se não conseguiu determinar, usa .bin como padrão
    return '.bin'

def sanitize_filename(filename):
    """
    Remove caracteres inválidos de nomes de arquivo
    """
    if not filename:
        return "unnamed"
    
    # Remove ou substitui caracteres problemáticos
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove espaços múltiplos e espaços no início/fim
    filename = ' '.join(filename.split())
    
    # Limita o tamanho do nome
    if len(filename) > 50:
        filename = filename[:50]
    
    return filename or "unnamed"
