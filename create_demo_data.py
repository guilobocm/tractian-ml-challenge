#!/usr/bin/env python3
"""
Script para criar dados de demonstração completos com assets simulados
para o TRACTIAN Challenge
"""

import os
import json
import shutil
from pathlib import Path

def create_demo_product_data():
    """
    Cria dados de demonstração com 10 produtos completos incluindo assets simulados
    """
    output_dir = Path("output")
    assets_dir = output_dir / "assets"
    
    # Remove dados existentes
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    # Cria estrutura de diretórios
    output_dir.mkdir(exist_ok=True)
    assets_dir.mkdir(exist_ok=True)
    
    # Dados de produtos simulados baseados em produtos reais da Baldor
    products = [
        {
            "product_id": "M3546T",
            "name": "3 HP General Purpose Motor - 1800 RPM",
            "description": "TEFC motor designed for general purpose applications. Features Class F insulation system with Class B temperature rise.",
            "specs": {
                "Horsepower": "3 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V",
                "Frame": "182T",
                "Enclosure": "TEFC",
                "Efficiency": "89.5%"
            },
            "bom": [
                {"part_number": "ST-001", "description": "Main stator with windings", "quantity": 1},
                {"part_number": "RT-001", "description": "Cast iron rotor assembly", "quantity": 1},
                {"part_number": "BR-001", "description": "Ball bearing 6206ZZ", "quantity": 2},
                {"part_number": "FN-001", "description": "External cooling fan", "quantity": 1}
            ],
            "assets": {
                "manual": "assets/M3546T/manual.pdf",
                "datasheet": "assets/M3546T/datasheet.pdf",
                "cad_dwg": "assets/M3546T/cad_dwg.dwg",
                "cad_step": "assets/M3546T/cad_step.step",
                "image_main": "assets/M3546T/image_main.jpg",
                "image_dimensions": "assets/M3546T/image_dimensions.jpg",
                "certificate_ul": "assets/M3546T/certificate_ul.pdf",
                "wiring_diagram": "assets/M3546T/wiring_diagram.pdf"
            }
        },
        {
            "product_id": "L3514T",
            "name": "1 HP Single Phase Motor - 1800 RPM",
            "description": "Capacitor start, capacitor run motor for commercial and light industrial applications.",
            "specs": {
                "Horsepower": "1 HP",
                "RPM": "1800", 
                "Voltage": "115/208-230V",
                "Frame": "143T",
                "Enclosure": "ODP",
                "Starting": "Capacitor Start/Run"
            },
            "bom": [
                {"part_number": "ST-002", "description": "Single phase stator", "quantity": 1},
                {"part_number": "RT-002", "description": "Aluminum rotor", "quantity": 1},
                {"part_number": "CP-001", "description": "Start capacitor 88-108 μF", "quantity": 1}
            ],
            "assets": {
                "manual": "assets/L3514T/manual.pdf",
                "datasheet": "assets/L3514T/datasheet.pdf",
                "image_main": "assets/L3514T/image_main.jpg"
            }
        },
        {
            "product_id": "M2513T",
            "name": "2 HP Three Phase Motor - 1800 RPM",
            "description": "Premium efficient motor with die cast aluminum rotor for reliable performance.",
            "specs": {
                "Horsepower": "2 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V", 
                "Frame": "145T",
                "Enclosure": "TEFC",
                "Efficiency": "87.5%"
            },
            "bom": [
                {"part_number": "ST-003", "description": "Three phase stator assembly", "quantity": 1},
                {"part_number": "RT-003", "description": "Die cast aluminum rotor", "quantity": 1},
                {"part_number": "BR-002", "description": "Ball bearing 6205ZZ", "quantity": 2}
            ],
            "assets": {
                "manual": "assets/M2513T/manual.pdf",
                "image_main": "assets/M2513T/image_main.jpg",
                "wiring_diagram": "assets/M2513T/wiring_diagram.pdf"
            }
        },
        {
            "product_id": "VM3554T",
            "name": "5 HP Severe Duty Motor - 1800 RPM",
            "description": "Designed for harsh environments with enhanced moisture and contamination protection.",
            "specs": {
                "Horsepower": "5 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V",
                "Frame": "184T", 
                "Enclosure": "TEFC",
                "Duty": "Severe Duty"
            },
            "bom": [
                {"part_number": "ST-004", "description": "Heavy duty stator", "quantity": 1},
                {"part_number": "RT-004", "description": "Balanced rotor assembly", "quantity": 1},
                {"part_number": "SL-001", "description": "Enhanced shaft seal", "quantity": 2}
            ],
            "assets": {
                "manual": "assets/VM3554T/manual.pdf",
                "datasheet": "assets/VM3554T/datasheet.pdf",
                "image_main": "assets/VM3554T/image_main.jpg",
                "certificate": "assets/VM3554T/certificate.pdf"
            }
        },
        {
            "product_id": "L1408T",
            "name": "1/2 HP Single Phase Motor - 1800 RPM",
            "description": "Compact motor ideal for pumps, fans and light duty applications.",
            "specs": {
                "Horsepower": "0.5 HP",
                "RPM": "1800",
                "Voltage": "115/208-230V",
                "Frame": "56",
                "Enclosure": "ODP"
            },
            "bom": [
                {"part_number": "ST-005", "description": "Compact stator", "quantity": 1},
                {"part_number": "RT-005", "description": "Small rotor assembly", "quantity": 1}
            ],
            "assets": {
                "manual": "assets/L1408T/manual.pdf",
                "image_main": "assets/L1408T/image_main.jpg"
            }
        },
        {
            "product_id": "M3711T",
            "name": "7.5 HP Three Phase Motor - 1800 RPM",
            "description": "High efficiency motor for industrial applications requiring reliable continuous operation.",
            "specs": {
                "Horsepower": "7.5 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V",
                "Frame": "213T",
                "Enclosure": "TEFC",
                "Efficiency": "91.0%"
            },
            "bom": [
                {"part_number": "ST-006", "description": "High power stator", "quantity": 1},
                {"part_number": "RT-006", "description": "Heavy duty rotor", "quantity": 1},
                {"part_number": "BR-003", "description": "Ball bearing 6207ZZ", "quantity": 2}
            ],
            "assets": {
                "manual": "assets/M3711T/manual.pdf",
                "datasheet": "assets/M3711T/datasheet.pdf",
                "cad_dwg": "assets/M3711T/cad_dwg.dwg",
                "image_main": "assets/M3711T/image_main.jpg"
            }
        },
        {
            "product_id": "VM3615T",
            "name": "15 HP Inverter Duty Motor - 1800 RPM",
            "description": "Variable frequency drive compatible motor with enhanced insulation system.",
            "specs": {
                "Horsepower": "15 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V",
                "Frame": "254T",
                "Enclosure": "TEFC",
                "Special": "Inverter Duty"
            },
            "bom": [
                {"part_number": "ST-007", "description": "VFD compatible stator", "quantity": 1},
                {"part_number": "RT-007", "description": "Precision balanced rotor", "quantity": 1},
                {"part_number": "IN-001", "description": "Enhanced insulation system", "quantity": 1}
            ],
            "assets": {
                "manual": "assets/VM3615T/manual.pdf",
                "datasheet": "assets/VM3615T/datasheet.pdf",
                "image_main": "assets/VM3615T/image_main.jpg",
                "vfd_guide": "assets/VM3615T/vfd_guide.pdf"
            }
        },
        {
            "product_id": "L1510T",
            "name": "1 HP Single Phase Motor - 3600 RPM",
            "description": "High speed motor for applications requiring increased RPM operation.",
            "specs": {
                "Horsepower": "1 HP",
                "RPM": "3600",
                "Voltage": "115/208-230V",
                "Frame": "143T",
                "Enclosure": "ODP"
            },
            "bom": [
                {"part_number": "ST-008", "description": "High speed stator", "quantity": 1},
                {"part_number": "RT-008", "description": "High speed rotor", "quantity": 1}
            ],
            "assets": {
                "manual": "assets/L1510T/manual.pdf",
                "image_main": "assets/L1510T/image_main.jpg"
            }
        },
        {
            "product_id": "M2394T",
            "name": "25 HP Three Phase Motor - 1800 RPM",
            "description": "Premium efficiency motor for demanding industrial applications.",
            "specs": {
                "Horsepower": "25 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V",
                "Frame": "284T",
                "Enclosure": "TEFC",
                "Efficiency": "93.0%"
            },
            "bom": [
                {"part_number": "ST-009", "description": "Large frame stator", "quantity": 1},
                {"part_number": "RT-009", "description": "Heavy duty rotor assembly", "quantity": 1},
                {"part_number": "BR-004", "description": "Ball bearing 6209ZZ", "quantity": 2}
            ],
            "assets": {
                "manual": "assets/M2394T/manual.pdf",
                "datasheet": "assets/M2394T/datasheet.pdf",
                "cad_dwg": "assets/M2394T/cad_dwg.dwg",
                "image_main": "assets/M2394T/image_main.jpg",
                "certificate": "assets/M2394T/certificate.pdf"
            }
        },
        {
            "product_id": "VM3709T",
            "name": "10 HP Washdown Duty Motor - 1800 RPM",
            "description": "Stainless steel motor designed for food processing and washdown environments.",
            "specs": {
                "Horsepower": "10 HP",
                "RPM": "1800",
                "Voltage": "208-230/460V",
                "Frame": "215T",
                "Enclosure": "TEFC",
                "Special": "Washdown Duty",
                "Material": "Stainless Steel"
            },
            "bom": [
                {"part_number": "ST-010", "description": "Stainless steel stator", "quantity": 1},
                {"part_number": "RT-010", "description": "Corrosion resistant rotor", "quantity": 1},
                {"part_number": "SS-001", "description": "Stainless steel housing", "quantity": 1}
            ],
            "assets": {
                "manual": "assets/VM3709T/manual.pdf",
                "datasheet": "assets/VM3709T/datasheet.pdf",
                "image_main": "assets/VM3709T/image_main.jpg",
                "washdown_guide": "assets/VM3709T/washdown_guide.pdf"
            }
        }
    ]
    
    # Gera os arquivos JSON e assets para cada produto
    for product in products:
        product_id = product["product_id"]
        
        # Salva o JSON do produto
        json_path = output_dir / f"{product_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(product, f, ensure_ascii=False, indent=2)
        
        # Cria pasta de assets do produto
        product_assets_dir = assets_dir / product_id
        product_assets_dir.mkdir(exist_ok=True)
        
        # Cria arquivos de assets simulados
        for asset_name, asset_path in product["assets"].items():
            asset_file_path = output_dir / asset_path
            create_dummy_asset(asset_file_path, asset_name)
    
    print(f"✅ Criados {len(products)} produtos com assets completos!")
    print(f"📁 Dados salvos em: {output_dir.absolute()}")
    
    # Cria resumo
    create_summary(products, output_dir)

def create_dummy_asset(file_path, asset_name):
    """
    Cria um arquivo asset simulado com conteúdo básico
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Conteúdo simulado baseado no tipo de asset
    if asset_name.endswith('.pdf') or 'manual' in asset_name or 'datasheet' in asset_name:
        content = f"% Dummy PDF content for {asset_name}\n% This is simulated content for TRACTIAN challenge demo\n"
    elif asset_name.endswith('.dwg') or 'cad' in asset_name:
        content = f"# CAD file content for {asset_name}\n# Simulated drawing data\n"
    elif asset_name.endswith('.jpg') or 'image' in asset_name:
        content = f"# Image file placeholder for {asset_name}\n# Binary image data would be here\n"
    else:
        content = f"# Asset content for {asset_name}\n# Simulated file content\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_summary(products, output_dir):
    """
    Cria arquivo de resumo da execução
    """
    summary = {
        "timestamp": "2025-05-27T14:40:00Z",
        "total_products": len(products),
        "successful_products": len(products),
        "failed_products": 0,
        "demo_mode": True,
        "products_generated": [p["product_id"] for p in products],
        "asset_types": ["manual", "datasheet", "cad_dwg", "cad_step", "image_main", "certificate", "wiring_diagram"],
        "notes": "Demo data generated for TRACTIAN challenge submission"
    }
    
    summary_path = output_dir / "demo_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    create_demo_product_data()
