#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BSB Park — Exportação de tabelas do Supabase para CSV
Baseado no guia técnico do Claude Code
"""

import requests
import csv
import os
from datetime import datetime

# CONFIGURAÇÃO
SUPABASE_URL = 'https://clxuxrlqbkdadhkpzaly.supabase.co'
SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

OUTPUT_DIR = 'csvs'

# Apenas a tabela calendario por enquanto
TABELAS = ['calendario']

# Headers CORRETOS - com apikey!
HEADERS = {
    'apikey': SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
}

def formatar_valor(v):
    """Converte valores para padrão pt-BR"""
    if isinstance(v, float):
        return f'{v:.2f}'.replace('.', ',')
    if isinstance(v, bool):
        return 'Verdadeiro' if v else 'Falso'
    return str(v) if v is not None else ''

def exportar_tabela(tabela):
    """Exporta tabela com paginação"""
    todos = []
    limit = 1000
    offset = 0
    
    while True:
        resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/{tabela}',
            headers=HEADERS,
            params={'select': '*', 'limit': limit, 'offset': offset},
            timeout=30,
        )
        resp.raise_for_status()
        dados = resp.json()
        
        if not dados:
            break
        
        todos.extend(dados)
        
        if len(dados) < limit:
            break
        
        offset += limit
    
    return todos

def salvar_csv(tabela, dados):
    """Salva dados em CSV com padrão pt-BR"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    caminho = os.path.join(OUTPUT_DIR, f'{tabela}.csv')
    
    with open(caminho, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys(), delimiter=';')
        writer.writeheader()
        for row in dados:
            writer.writerow({k: formatar_valor(v) for k, v in row.items()})
    
    return caminho

# EXECUÇÃO
if __name__ == '__main__':
    inicio = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    print(f'=== BSB Park — Exportação {inicio} ===')
    erros = 0
    
    for tabela in TABELAS:
        try:
            dados = exportar_tabela(tabela)
            if not dados:
                print(f'[AVISO] {tabela}: sem registros.')
                continue
            caminho = salvar_csv(tabela, dados)
            print(f'[OK] {tabela}: {len(dados)} registros → {caminho}')
        except Exception as e:
            print(f'[ERRO] {tabela}: {e}')
            erros += 1
    
    print(f'=== Concluído. Erros: {erros} ===')
    if erros:
        exit(1)
