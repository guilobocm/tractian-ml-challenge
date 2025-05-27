import os
import json
import logging
import asyncio
from datetime import datetime
import sys

from src.scraper import get_product_urls
from src.parser import parse_product_page
from src.downloader import download_assets

# Configuração de logging mais detalhada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

BASE_URL = 'https://www.baldor.com/catalog'
LIMIT = 12  # Entre 10-15 produtos conforme especificado
OUTPUT_DIR = 'output'
ASSETS_DIR = os.path.join(OUTPUT_DIR, 'assets')

async def main():
    """
    Função principal que coordena todo o processo de scraping
    """
    start_time = datetime.now()
    logging.info("=" * 60)
    logging.info("INICIANDO PROCESSO DE SCRAPING DA BALDOR")
    logging.info("=" * 60)
    
    # Cria diretórios necessários
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    successful_products = 0
    failed_products = 0
    
    try:
        # 1. Extrai URLs dos produtos
        logging.info(f"Buscando URLs de produtos (limite: {LIMIT})")
        urls = get_product_urls(limit=LIMIT)
        
        if not urls:
            logging.error("Nenhuma URL de produto encontrada!")
            return
            
        logging.info(f"URLs encontradas ({len(urls)}): {urls[:3]}...")  # Mostra apenas as 3 primeiras
        
        # 2. Processa cada produto
        for i, url in enumerate(urls, 1):
            logging.info(f"\n--- Processando produto {i}/{len(urls)} ---")
            logging.info(f"URL: {url}")
            
            try:
                # Parse da página do produto
                data = parse_product_page(url)
                
                if 'error' in data:
                    logging.warning(f"Erro no parsing: {data['error']}")
                    failed_products += 1
                    continue
                
                product_id = data['product_id']
                logging.info(f"Produto ID: {product_id}")
                logging.info(f"Nome: {data['name']}")
                logging.info(f"Assets encontrados: {list(data['assets'].keys())}")
                
                # Download dos assets
                if data['assets']:
                    logging.info(f"Iniciando download de {len(data['assets'])} assets...")
                    await download_assets(product_id, data['assets'], ASSETS_DIR)
                    
                    # Atualiza os caminhos dos assets no JSON para os arquivos locais
                    update_asset_paths(data, product_id)
                else:
                    logging.warning(f"Nenhum asset encontrado para {product_id}")
                
                # Salva os dados em JSON
                save_product_data(data, product_id)
                
                successful_products += 1
                logging.info(f"✓ Produto {product_id} processado com sucesso")
                
            except Exception as e:
                logging.error(f"✗ Erro ao processar {url}: {e}")
                failed_products += 1
                continue
        
        # Relatório final
        end_time = datetime.now()
        duration = end_time - start_time
        
        logging.info("\n" + "=" * 60)
        logging.info("RELATÓRIO FINAL")
        logging.info("=" * 60)
        logging.info(f"Produtos processados com sucesso: {successful_products}")
        logging.info(f"Produtos com falha: {failed_products}")
        logging.info(f"Total de URLs processadas: {len(urls)}")
        logging.info(f"Tempo total: {duration}")
        logging.info(f"Arquivos salvos em: {os.path.abspath(OUTPUT_DIR)}")
        
        # Cria um resumo em JSON
        create_summary_report(urls, successful_products, failed_products, duration)
        
    except Exception as e:
        logging.error(f"Erro crítico no processo principal: {e}")
        raise

def update_asset_paths(data, product_id):
    """
    Atualiza os caminhos dos assets no JSON para apontar para os arquivos locais
    conforme especificação do desafio: assets/PRODUCT_ID/filename.ext
    """
    for asset_name, url in list(data['assets'].items()):
        # Determina a extensão baseada na URL original
        if '.' in url:
            ext = '.' + url.split('.')[-1].split('?')[0]  # Remove query params
        else:
            # Mapeia tipos de asset para extensões padrão
            ext_mapping = {
                'manual': '.pdf',
                'cad': '.dwg',
                'image': '.jpg',
                'datasheet': '.pdf',
                'certificate': '.pdf'
            }
            ext = ext_mapping.get(asset_name, '.bin')
        
        # Caminho relativo conforme especificado: assets/PRODUCT_ID/filename.ext
        filename = f"{asset_name}{ext}"
        local_path = f"assets/{product_id}/{filename}"
        data['assets'][asset_name] = local_path

def save_product_data(data, product_id):
    """
    Salva os dados do produto em um arquivo JSON
    """
    json_path = os.path.join(OUTPUT_DIR, f"{product_id}.json")
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Dados salvos em: {json_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar JSON para {product_id}: {e}")

def create_summary_report(urls, successful, failed, duration):
    """
    Cria um relatório resumo da execução
    """
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_urls': len(urls),
        'successful_products': successful,
        'failed_products': failed,
        'duration_seconds': duration.total_seconds(),
        'output_directory': os.path.abspath(OUTPUT_DIR),
        'urls_processed': urls
    }
    
    summary_path = os.path.join(OUTPUT_DIR, 'scraping_summary.json')
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logging.info(f"Relatório resumo salvo em: {summary_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar relatório resumo: {e}")

if __name__ == '__main__':
    try:
        # Verifica se estamos em um ambiente async
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Executa o main de forma assíncrona
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logging.info("Processo interrompido pelo usuário")
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        raise