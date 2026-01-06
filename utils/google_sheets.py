"""
Módulo de conexão com Google Sheets
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st


@st.cache_resource
def conectar_google_sheets():
    """
    Conecta com Google Sheets usando as credenciais
    Returns: cliente gspread autenticado
    """
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', 
            scope
        )
        
        client = gspread.authorize(credentials)
        return client
    
    except FileNotFoundError:
        st.error("❌ Arquivo credentials.json não encontrado!")
        return None
    
    except Exception as e:
        st.error(f"❌ Erro ao conectar: {str(e)}")
        return None


@st.cache_data(ttl=300)
def carregar_planilha(nome_ou_url_ou_id, aba=0):
    """
    Carrega dados de uma planilha do Google Sheets
    
    Args:
        nome_ou_url_ou_id: Nome da planilha, URL completa OU ID direto
        aba: Índice da aba (0 = primeira) ou nome da aba
    
    Returns:
        DataFrame com os dados
    """
    try:
        client = conectar_google_sheets()
        
        if client is None:
            return None
        
        # Detectar automaticamente se é URL, ID ou nome
        if 'docs.google.com' in str(nome_ou_url_ou_id):
            planilha = client.open_by_url(nome_ou_url_ou_id)
        elif len(str(nome_ou_url_ou_id)) > 30 and '/' not in str(nome_ou_url_ou_id):
            planilha = client.open_by_key(nome_ou_url_ou_id)
        else:
            planilha = client.open(nome_ou_url_ou_id)
        
        # Abrir aba específica
        if isinstance(aba, int):
            worksheet = planilha.get_worksheet(aba)
        else:
            worksheet = planilha.worksheet(aba)
        
        # Ler dados brutos
        todos_valores = worksheet.get_all_values()
        
        if len(todos_valores) == 0:
            return pd.DataFrame()
        
        # Primeira linha = headers
        headers_originais = todos_valores[0]
        
        # Renomear colunas vazias
        headers_limpos = []
        contador_vazio = 1
        for h in headers_originais:
            if h == '' or h.strip() == '':
                headers_limpos.append(f'Coluna_Vazia_{contador_vazio}')
                contador_vazio += 1
            else:
                headers_limpos.append(h.strip())
        
        # Criar DataFrame
        dados = todos_valores[1:]  # Pular header
        df = pd.DataFrame(dados, columns=headers_limpos)
        
        # Remover linhas completamente vazias
        df = df.replace('', pd.NA).dropna(how='all')
        
        return df
    
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Planilha '{nome_ou_url_ou_id}' não encontrada!")
        st.info("💡 Verifique se compartilhou com o email da conta de serviço")
        return None
    
    except gspread.exceptions.APIError as e:
        st.error(f"❌ Erro de API do Google: {str(e)}")
        st.info("💡 Verifique se a planilha foi convertida para Google Sheets")
        return None
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar planilha: {str(e)}")
        return None


def salvar_em_planilha(df, nome_ou_url_ou_id, aba):
    """
    Salva um DataFrame em uma planilha do Google Sheets
    
    Args:
        df: DataFrame para salvar
        nome_ou_url_ou_id: Nome, URL ou ID da planilha
        aba: Nome da aba (será criada se não existir)
    
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    try:
        client = conectar_google_sheets()
        
        if client is None:
            return False
        
        # Abrir planilha
        if 'docs.google.com' in str(nome_ou_url_ou_id):
            planilha = client.open_by_url(nome_ou_url_ou_id)
        elif len(str(nome_ou_url_ou_id)) > 30 and '/' not in str(nome_ou_url_ou_id):
            planilha = client.open_by_key(nome_ou_url_ou_id)
        else:
            planilha = client.open(nome_ou_url_ou_id)
        
        # Tentar abrir aba existente ou criar nova
        try:
            worksheet = planilha.worksheet(aba)
            # Limpar conteúdo existente
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            # Criar nova aba
            worksheet = planilha.add_worksheet(title=aba, rows=1000, cols=50)
        
        # Preparar dados (incluir headers)
        dados_para_salvar = [df.columns.tolist()] + df.values.tolist()
        
        # Atualizar planilha
        worksheet.update('A1', dados_para_salvar)
        
        st.success(f"✅ Dados salvos na aba '{aba}'!")
        return True
    
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {str(e)}")
        return False


def listar_planilhas():
    """
    Lista todas as planilhas acessíveis pela conta de serviço
    
    Returns:
        Lista de dicionários com informações das planilhas
    """
    try:
        client = conectar_google_sheets()
        if client is None:
            return []
        
        planilhas = client.openall()
        resultado = []
        for p in planilhas:
            resultado.append({
                'nome': p.title,
                'id': p.id,
                'url': p.url
            })
        
        return resultado
    
    except Exception as e:
        st.error(f"❌ Erro ao listar planilhas: {str(e)}")
        return []