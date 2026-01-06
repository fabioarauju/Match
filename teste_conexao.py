"""
Teste de conexão com Google Sheets - COM TRATAMENTO DE COLUNAS
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

print("🔄 Testando conexão com Google Sheets...")

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
    print("✅ Credenciais carregadas!")
    
    # Usar ID direto
    spreadsheet_id = '1tM1LSnFLlp_CF8yAWFE0w6r1qTV9Smy_mvDx0Wx1x-U'
    
    print(f"\n📂 Abrindo planilha...")
    planilha = client.open_by_key(spreadsheet_id)
    print(f"✅ Planilha '{planilha.title}' aberta!")
    
    # Listar abas
    print("\n📋 Abas encontradas:")
    for i, worksheet in enumerate(planilha.worksheets()):
        print(f"   {i+1}. {worksheet.title} ({worksheet.row_count} linhas, {worksheet.col_count} colunas)")
    
    # Carregar aba candidatos - COM TRATAMENTO DE ERROS
    print("\n📂 Carregando aba 'candidatos'...")
    ws_candidatos = planilha.worksheet('candidatos')
    
    # SOLUÇÃO: Pegar dados como matriz e limpar manualmente
    print("   🔧 Lendo dados brutos...")
    todos_valores = ws_candidatos.get_all_values()
    
    if len(todos_valores) == 0:
        print("   ❌ Aba vazia!")
    else:
        # Primeira linha = headers
        headers_originais = todos_valores[0]
        print(f"   📊 {len(headers_originais)} colunas detectadas")
        
        # Verificar colunas vazias
        colunas_vazias = [i for i, h in enumerate(headers_originais) if h == '' or h.strip() == '']
        
        if colunas_vazias:
            print(f"   ⚠️ {len(colunas_vazias)} colunas vazias encontradas nas posições: {colunas_vazias[:5]}")
            print("   🔧 Renomeando colunas vazias...")
            
            # Renomear colunas vazias
            headers_limpos = []
            contador_vazio = 1
            for i, h in enumerate(headers_originais):
                if h == '' or h.strip() == '':
                    headers_limpos.append(f'Coluna_Vazia_{contador_vazio}')
                    contador_vazio += 1
                else:
                    headers_limpos.append(h.strip())
        else:
            headers_limpos = [h.strip() for h in headers_originais]
        
        # Criar DataFrame
        dados = todos_valores[1:]  # Pular header
        df = pd.DataFrame(dados, columns=headers_limpos)
        
        # Remover linhas completamente vazias
        df = df.replace('', pd.NA).dropna(how='all')
        
        print(f"   ✅ {len(df)} linhas carregadas!")
        
        # Mostrar colunas importantes
        print(f"\n📊 Colunas encontradas ({len(df.columns)} total):")
        colunas_importantes = [
            'Nome Completo', 'id', 'Área de Atuação', 'Nível do cargo atual',
            'Área_Atuação_Código', 'Nível do cargo código'
        ]
        
        for col in colunas_importantes:
            if col in df.columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ⚠️ {col} (NÃO ENCONTRADA)")
        
        # Mostrar TODAS as colunas (primeiras 20)
        print(f"\n📋 Todas as colunas (primeiras 20):")
        for i, col in enumerate(df.columns[:20], 1):
            valores_unicos = df[col].nunique()
            print(f"   {i}. '{col}' ({valores_unicos} valores únicos)")
        
        if len(df.columns) > 20:
            print(f"   ... e mais {len(df.columns) - 20} colunas")
        
        # Mostrar primeiras linhas
        print(f"\n📋 Primeiras 3 linhas:")
        colunas_mostrar = [c for c in ['Nome Completo', 'Área de Atuação', 'id'] if c in df.columns][:3]
        if colunas_mostrar:
            print(df[colunas_mostrar].head(3).to_string(index=False))
        else:
            print(df.iloc[:3, :5].to_string(index=False))  # Primeiras 5 colunas
    
    print("\n" + "="*70)
    print("✅ CONEXÃO FUNCIONANDO PERFEITAMENTE!")
    print("="*70)
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Rode: streamlit run app.py")
    print("   2. Configure a vaga na sidebar")
    print("   3. Clique em 'Gerar Recomendações'")

except FileNotFoundError:
    print("❌ Arquivo credentials.json não encontrado!")

except gspread.exceptions.SpreadsheetNotFound:
    print("❌ Planilha não encontrada!")
    print("\n📧 Verifique o compartilhamento com:")
    try:
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            print(f"   {creds.get('client_email', 'NÃO ENCONTRADO')}")
    except:
        pass

except Exception as e:
    print(f"❌ Erro: {str(e)}")
    print(f"🔍 Tipo: {type(e).__name__}")
    import traceback
    print("\n📋 Detalhes completos:")
    print(traceback.format_exc())