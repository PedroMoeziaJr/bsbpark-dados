#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script: exportar_csvs.py (VERSÃO 2.1)
Função: Exportar APENAS tabela calendario do Supabase para CSV
Data: 21 de Maio de 2026
Atualizado por: Claude IA
"""

import os
import csv
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

import requests

SUPABASE_URL = 'https://clxuxrlqbkdadhkpzaly.supabase.co'
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

OUTPUT_DIR = 'csvs'
LOG_FILE = '_log.txt'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def formatar_valor(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}".replace('.', ',')
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False, default=str)
    return str(v)

def criar_diretorio():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"✅ Diretório criado: {OUTPUT_DIR}")

def obter_tabela(tabela: str) -> List[Dict[str, Any]]:
    url = f"{SUPABASE_URL}/rest/v1/{tabela}"
    headers = {
        'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json',
    }
    
    todos_registros = []
    offset = 0
    limite = 1000
    
    logger.info(f"🔄 Buscando tabela: {tabela}")
    
    while True:
        params = {'limit': limite, 'offset': offset, 'select': '*'}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            dados = response.json()
            
            if not dados:
                break
            
            todos_registros.extend(dados)
            offset += limite
            logger.info(f"   → Carregados {len(dados)} registros (total: {len(todos_registros)})")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao buscar {tabela}: {e}")
            return []
    
    logger.info(f"✅ {tabela}: {len(todos_registros)} registros")
    return todos_registros

def escrever_csv(tabela: str, registros: List[Dict[str, Any]]):
    if not registros:
        logger.warning(f"⚠️  Tabela vazia: {tabela}")
        return
    
    arquivo = os.path.join(OUTPUT_DIR, f"{tabela}.csv")
    
    try:
        with open(arquivo, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = registros[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            for registro in registros:
                registro_formatado = {k: formatar_valor(v) for k, v in registro.items()}
                writer.writerow(registro_formatado)
        
        logger.info(f"📄 Arquivo criado: {arquivo} ({len(registros)} linhas)")
        
    except Exception as e:
        logger.error(f"❌ Erro ao escrever {arquivo}: {e}")

def main():
    logger.info("=" * 70)
    logger.info("EXPORTAÇÃO DE CSV - CALENDARIO")
    logger.info("=" * 70)
    
    if not SUPABASE_SERVICE_ROLE_KEY:
        logger.error("❌ SUPABASE_SERVICE_ROLE_KEY não configurada!")
        return False
    
    criar_diretorio()
    registros = obter_tabela('calendario')
    
    if registros:
        escrever_csv('calendario', registros)
        sucesso = True
    else:
        logger.warning("⚠️  calendario: Sem dados ou erro")
        sucesso = False
    
    logger.info("=" * 70)
    if sucesso:
        logger.info(f"✅ SUCESSO: calendario.csv com {len(registros)} registros")
    else:
        logger.info("❌ ERRO: Não foi possível exportar")
    logger.info(f"📁 Arquivo: {OUTPUT_DIR}/calendario.csv")
    logger.info("=" * 70)
    
    return sucesso

if __name__ == '__main__':
    sucesso = main()
    exit(0 if sucesso else 1)
