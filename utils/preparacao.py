"""
Módulo de preparação e validação de dados
"""

import pandas as pd
import numpy as np
import streamlit as st


def validar_dados(df, tipo):
    """
    Valida se o DataFrame tem as colunas necessárias
    
    Args:
        df: DataFrame para validar
        tipo: 'candidatos', 'vagas' ou 'matches'
    
    Returns:
        True se válido, False caso contrário
    """
    
    colunas_necessarias = {
        'candidatos': [
            'id',
            'Intervalo_Idade_Código',
            'Nível_Formação_Código',
            'Nível do cargo código',
            'Área_Atuação_Código',
            'Regime código',
            'autoridade',
            'prestigio',
            'preservacao',
            'formalidade'
        ],
        'vagas': [
            'ID_vaga',
            'Intervalo_Idade_Código',
            'Nível_Formação_Código',
            'Nível do cargo código',
            'Área_Atuação_Código',
            'Regime código',
            'autoridade',
            'prestigio',
            'preservacao',
            'formalidade'
        ],
        'matches': [
            'id_vaga',
            'id_candidato',
            'match'
        ]
    }
    
    colunas_esperadas = colunas_necessarias.get(tipo, [])
    colunas_faltando = [col for col in colunas_esperadas if col not in df.columns]
    
    if colunas_faltando:
        st.error(f"❌ Erros em {tipo}: Colunas faltando: {', '.join(colunas_faltando)}")
        
        # Mostrar colunas disponíveis para debug
        with st.expander(f"🔍 Colunas disponíveis em {tipo}"):
            st.write(list(df.columns))
        
        return False
    
    return True


def limpar_dados(df, tipo):
    """
    Limpa e trata valores faltantes
    
    Args:
        df: DataFrame para limpar
        tipo: 'candidatos', 'vagas' ou 'matches'
    
    Returns:
        DataFrame limpo
    """
    df = df.copy()
    
    # Colunas de código (preencher com moda)
    colunas_codigo = [
        'Intervalo_Idade_Código',
        'Nível_Formação_Código',
        'Nível do cargo código',
        'Área_Atuação_Código',
        'Regime código'
    ]
    
    for col in colunas_codigo:
        if col in df.columns:
            # Converter para numérico
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Preencher NaN com a moda (valor mais frequente)
            if df[col].notna().sum() > 0:
                moda = df[col].mode()
                if len(moda) > 0:
                    df[col] = df[col].fillna(moda[0])
                else:
                    df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna(0)
    
    # Colunas de perfil comportamental (preencher com 25.0)
    colunas_perfil = ['autoridade', 'prestigio', 'preservacao', 'formalidade']
    
    for col in colunas_perfil:
        if col in df.columns:
            # Converter para numérico
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Preencher NaN com 25.0 (valor neutro)
            df[col] = df[col].fillna(25.0)
    
    # Match (preencher com 0)
    if 'match' in df.columns:
        df['match'] = pd.to_numeric(df['match'], errors='coerce')
        df['match'] = df['match'].fillna(0).astype(int)
    
    return df


def preparar_dados_completos(candidatos, vagas, matches):
    """
    Prepara dataset completo com merge e cálculo de features
    
    Args:
        candidatos: DataFrame com candidatos
        vagas: DataFrame com vagas
        matches: DataFrame com matches
    
    Returns:
        DataFrame completo com features calculadas
    """
    
    try:
        # Validar estrutura (sem mensagens de progresso)
        if not validar_dados(candidatos, 'candidatos'):
            return None
        
        if not validar_dados(vagas, 'vagas'):
            return None
        
        if not validar_dados(matches, 'matches'):
            return None
        
        # Limpar dados (sem mensagens)
        candidatos = limpar_dados(candidatos, 'candidatos')
        vagas = limpar_dados(vagas, 'vagas')
        matches = limpar_dados(matches, 'matches')
        
        # Fazer merge (sem mensagens)
        dados = matches.merge(
            candidatos,
            left_on='id_candidato',
            right_on='id',
            how='inner',
            suffixes=('', '_candidato')
        )
        
        dados = dados.merge(
            vagas,
            left_on='id_vaga',
            right_on='ID_vaga',
            how='inner',
            suffixes=('_candidato', '_vaga')
        )
        
        # Calcular features (sem mensagens)
        dados['diff_idade'] = abs(
            dados['Intervalo_Idade_Código_candidato'] - 
            dados['Intervalo_Idade_Código_vaga']
        )
        
        dados['diff_formacao'] = abs(
            dados['Nível_Formação_Código_candidato'] - 
            dados['Nível_Formação_Código_vaga']
        )
        
        dados['diff_area'] = abs(
            dados['Área_Atuação_Código_candidato'] - 
            dados['Área_Atuação_Código_vaga']
        )
        
        dados['diff_cargo'] = abs(
            dados['Nível do cargo código_candidato'] - 
            dados['Nível do cargo código_vaga']
        )
        
        dados['diff_regime'] = abs(
            dados['Regime código_candidato'] - 
            dados['Regime código_vaga']
        )
        
        dados['diff_autoridade'] = abs(
            dados['autoridade_candidato'] - 
            dados['autoridade_vaga']
        )
        
        dados['diff_prestigio'] = abs(
            dados['prestigio_candidato'] - 
            dados['prestigio_vaga']
        )
        
        dados['diff_preservacao'] = abs(
            dados['preservacao_candidato'] - 
            dados['preservacao_vaga']
        )
        
        dados['diff_formalidade'] = abs(
            dados['formalidade_candidato'] - 
            dados['formalidade_vaga']
        )
        
        # Distância euclidiana do perfil
        dados['distancia_perfil'] = np.sqrt(
            dados['diff_autoridade']**2 +
            dados['diff_prestigio']**2 +
            dados['diff_preservacao']**2 +
            dados['diff_formalidade']**2
        )
        
        # Verificar NaN
        total_nan = dados[['diff_idade', 'diff_formacao', 'diff_area', 'diff_cargo', 
                           'diff_regime', 'diff_autoridade', 'diff_prestigio',
                           'diff_preservacao', 'diff_formalidade', 'distancia_perfil']].isnull().sum().sum()
        
        if total_nan > 0:
            dados = dados.fillna(0)
        
        # Estatísticas (opcional - pode comentar se não quiser ver)
        with st.expander("📊 Estatísticas do Dataset"):
            st.write(f"**Total de registros:** {len(dados)}")
            st.write(f"**Matches bons (1):** {sum(dados['match'] == 1)} ({sum(dados['match'] == 1)/len(dados)*100:.1f}%)")
            st.write(f"**Matches ruins (0):** {sum(dados['match'] == 0)} ({sum(dados['match'] == 0)/len(dados)*100:.1f}%)")
            
            # st.write("\n**Correlações com Match:**")
            # correlacoes = dados[['diff_idade', 'diff_formacao', 'diff_area', 'diff_cargo', 
            #                      'diff_regime', 'distancia_perfil', 'match']].corr()['match'].sort_values()
            # st.dataframe(correlacoes.drop('match').to_frame('Correlação'))
        return dados
        
    except Exception as e:
        st.error(f"❌ Erro na preparação: {str(e)}")
        with st.expander("🔍 Debug - Ver erro completo"):
            import traceback
            st.code(traceback.format_exc())
        return None


def calcular_features_vaga(candidatos, vaga_dict):
    """
    Calcula features para uma vaga nova (matching em tempo real)
    
    Args:
        candidatos: DataFrame com candidatos
        vaga_dict: Dicionário com especificações da vaga
    
    Returns:
        DataFrame com features calculadas
    """
    
    candidatos = candidatos.copy()
    
    # Garantir que colunas são numéricas
    colunas_numericas = [
        'Intervalo_Idade_Código',
        'Nível_Formação_Código',
        'Nível do cargo código',
        'Área_Atuação_Código',
        'Regime código',
        'autoridade',
        'prestigio',
        'preservacao',
        'formalidade'
    ]
    
    for col in colunas_numericas:
        if col in candidatos.columns:
            candidatos[col] = pd.to_numeric(candidatos[col], errors='coerce')
    
    # Preencher NaN
    candidatos = candidatos.fillna({
        'Intervalo_Idade_Código': 2,
        'Nível_Formação_Código': 4,
        'Nível do cargo código': 3,
        'Área_Atuação_Código': 1,
        'Regime código': 0,
        'autoridade': 25.0,
        'prestigio': 25.0,
        'preservacao': 25.0,
        'formalidade': 25.0
    })
    
    # Calcular diferenças
    features = pd.DataFrame({
        'diff_idade': abs(candidatos['Intervalo_Idade_Código'] - vaga_dict['codigo_idade']),
        'diff_formacao': abs(candidatos['Nível_Formação_Código'] - vaga_dict['codigo_formacao']),
        'diff_area': abs(candidatos['Área_Atuação_Código'] - vaga_dict['codigo_area']),
        'diff_cargo': abs(candidatos['Nível do cargo código'] - vaga_dict['codigo_cargo']),
        'diff_regime': abs(candidatos['Regime código'] - vaga_dict['codigo_regime']),
        'diff_autoridade': abs(candidatos['autoridade'] - vaga_dict['autoridade']),
        'diff_prestigio': abs(candidatos['prestigio'] - vaga_dict['prestigio']),
        'diff_preservacao': abs(candidatos['preservacao'] - vaga_dict['preservacao']),
        'diff_formalidade': abs(candidatos['formalidade'] - vaga_dict['formalidade'])
    })
    
    # Distância euclidiana do perfil
    features['distancia_perfil'] = np.sqrt(
        features['diff_autoridade']**2 +
        features['diff_prestigio']**2 +
        features['diff_preservacao']**2 +
        features['diff_formalidade']**2
    )
    
    return features