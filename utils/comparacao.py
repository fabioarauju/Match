"""
Módulo de comparação e treinamento de modelos ML
"""

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, roc_curve
)
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os


def treinar_modelos(X_train, y_train, X_test, y_test):
    """
    Treina 3 modelos de ML e retorna resultados
    
    Args:
        X_train, y_train: Dados de treino
        X_test, y_test: Dados de teste
    
    Returns:
        Dict com modelos, resultados, previsões e probabilidades
    """
    
    modelos = {}
    previsoes = {}
    probabilidades = {}
    resultados = []
    
    # ═══════════════════════════════════════════════════════════════════
    # MODELO 1: LOGISTIC REGRESSION
    # ═══════════════════════════════════════════════════════════════════
    lr_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('lr', LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'))
    ])
    
    lr_pipeline.fit(X_train, y_train)
    y_pred_lr = lr_pipeline.predict(X_test)
    y_proba_lr = lr_pipeline.predict_proba(X_test)[:, 1]
    
    modelos['LR'] = lr_pipeline
    previsoes['LR'] = y_pred_lr
    probabilidades['LR'] = y_proba_lr
    
    resultados.append({
        'Modelo': 'Logistic Regression',
        'Acurácia': accuracy_score(y_test, y_pred_lr),
        'Precisão': precision_score(y_test, y_pred_lr, zero_division=0),
        'Recall': recall_score(y_test, y_pred_lr, zero_division=0),
        'F1-Score': f1_score(y_test, y_pred_lr, zero_division=0),
        'ROC-AUC': roc_auc_score(y_test, y_proba_lr)
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # MODELO 2: RANDOM FOREST
    # ═══════════════════════════════════════════════════════════════════
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_proba_rf = rf.predict_proba(X_test)[:, 1]
    
    modelos['RF'] = rf
    previsoes['RF'] = y_pred_rf
    probabilidades['RF'] = y_proba_rf
    
    resultados.append({
        'Modelo': 'Random Forest',
        'Acurácia': accuracy_score(y_test, y_pred_rf),
        'Precisão': precision_score(y_test, y_pred_rf, zero_division=0),
        'Recall': recall_score(y_test, y_pred_rf, zero_division=0),
        'F1-Score': f1_score(y_test, y_pred_rf, zero_division=0),
        'ROC-AUC': roc_auc_score(y_test, y_proba_rf)
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # MODELO 3: XGBOOST
    # ═══════════════════════════════════════════════════════════════════
    # Calcular scale_pos_weight
    neg = (y_train == 0).sum()
    pos = (y_train == 1).sum()
    scale_pos_weight = neg / pos if pos > 0 else 1.0
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        scale_pos_weight=scale_pos_weight,
        n_jobs=-1,
        eval_metric='logloss'
    )
    
    xgb_model.fit(X_train, y_train)
    y_pred_xgb = xgb_model.predict(X_test)
    y_proba_xgb = xgb_model.predict_proba(X_test)[:, 1]
    
    modelos['XGB'] = xgb_model
    previsoes['XGB'] = y_pred_xgb
    probabilidades['XGB'] = y_proba_xgb
    
    resultados.append({
        'Modelo': 'XGBoost',
        'Acurácia': accuracy_score(y_test, y_pred_xgb),
        'Precisão': precision_score(y_test, y_pred_xgb, zero_division=0),
        'Recall': recall_score(y_test, y_pred_xgb, zero_division=0),
        'F1-Score': f1_score(y_test, y_pred_xgb, zero_division=0),
        'ROC-AUC': roc_auc_score(y_test, y_proba_xgb)
    })
    
    # Calcular score total
    df_resultados = pd.DataFrame(resultados)
    df_resultados['Score_Total'] = (
        df_resultados['Acurácia'] +
        df_resultados['F1-Score'] +
        df_resultados['ROC-AUC']
    ) / 3
    
    return {
        'modelos': modelos,
        'resultados': df_resultados,
        'previsoes': previsoes,
        'probabilidades': probabilidades
    }


def gerar_recomendacoes(candidatos, vaga, modelos, pesos, fatores_penalizacao):
    """
    Gera recomendações para uma vaga específica
    
    Args:
        candidatos: DataFrame com candidatos
        vaga: dict com especificações da vaga
        modelos: dict com modelos treinados
        pesos: dict com pesos de cada aspecto
        fatores_penalizacao: dict com fatores de penalização
    
    Returns:
        DataFrame com top 10 candidatos ranqueados
    """
    
    candidatos = candidatos.copy()
    
    # ═══════════════════════════════════════════════════════════════════
    # CONVERTER COLUNAS PARA NUMÉRICO
    # ═══════════════════════════════════════════════════════════════════
    colunas_para_converter = [
        'Intervalo_Idade_Código',
        'Nível_Formação_Código',
        'Área_Atuação_Código',
        'Nível do cargo código',
        'Regime código',
        'autoridade',
        'prestigio',
        'preservacao',
        'formalidade'
    ]
    
    for col in colunas_para_converter:
        if col in candidatos.columns:
            candidatos[col] = pd.to_numeric(candidatos[col], errors='coerce')
    
    # Preencher NaN com valores padrão
    candidatos = candidatos.fillna({
        'Intervalo_Idade_Código': 2,
        'Nível_Formação_Código': 4,
        'Área_Atuação_Código': 1,
        'Nível do cargo código': 3,
        'Regime código': 0,
        'autoridade': 25.0,
        'prestigio': 25.0,
        'preservacao': 25.0,
        'formalidade': 25.0
    })
    
    # ═══════════════════════════════════════════════════════════════════
    # CALCULAR FEATURES
    # ═══════════════════════════════════════════════════════════════════
    features_lista = []
    
    for idx, cand in candidatos.iterrows():
        features = {
            'diff_idade': abs(float(cand['Intervalo_Idade_Código']) - float(vaga['codigo_idade'])),
            'diff_formacao': abs(float(cand['Nível_Formação_Código']) - float(vaga['codigo_formacao'])),
            'diff_area': abs(float(cand['Área_Atuação_Código']) - float(vaga['codigo_area'])),
            'diff_cargo': abs(float(cand['Nível do cargo código']) - float(vaga['codigo_cargo'])),
            'diff_regime': abs(float(cand['Regime código']) - float(vaga['codigo_regime'])),
            'diff_autoridade': abs(float(cand['autoridade']) - float(vaga['autoridade'])),
            'diff_prestigio': abs(float(cand['prestigio']) - float(vaga['prestigio'])),
            'diff_preservacao': abs(float(cand['preservacao']) - float(vaga['preservacao'])),
            'diff_formalidade': abs(float(cand['formalidade']) - float(vaga['formalidade']))
        }
        
        features['distancia_perfil'] = np.sqrt(
            features['diff_autoridade']**2 +
            features['diff_prestigio']**2 +
            features['diff_preservacao']**2 +
            features['diff_formalidade']**2
        )
        
        features_lista.append(features)
    
    df_predicao = pd.DataFrame(features_lista)
    
    # Tratar NaN
    for col in df_predicao.columns:
        max_val = df_predicao[col].max()
        if pd.isna(max_val) or max_val == 0:
            max_val = 10
        df_predicao[col] = df_predicao[col].fillna(max_val)
    
    # ═══════════════════════════════════════════════════════════════════
    # FAZER PREVISÕES COM OS 3 MODELOS
    # ═══════════════════════════════════════════════════════════════════
    candidatos['prob_lr'] = modelos['LR'].predict_proba(df_predicao)[:, 1]
    candidatos['prob_rf'] = modelos['RF'].predict_proba(df_predicao)[:, 1]
    candidatos['prob_xgb'] = modelos['XGB'].predict_proba(df_predicao)[:, 1]
    
    # ═══════════════════════════════════════════════════════════════════
    # CALCULAR SCORES 0-100 POR ASPECTO
    # ═══════════════════════════════════════════════════════════════════
    candidatos['score_area'] = 100 - np.minimum(
        df_predicao['diff_area'] * fatores_penalizacao['area'],
        100
    )
    
    candidatos['score_perfil'] = 100 - np.minimum(
        df_predicao['distancia_perfil'] * fatores_penalizacao['perfil'],
        100
    )
    
    candidatos['score_cargo'] = 100 - np.minimum(
        df_predicao['diff_cargo'] * fatores_penalizacao['cargo'],
        100
    )
    
    candidatos['score_formacao'] = 100 - np.minimum(
        df_predicao['diff_formacao'] * fatores_penalizacao['formacao'],
        100
    )
    
    candidatos['score_idade'] = 100 - np.minimum(
        df_predicao['diff_idade'] * fatores_penalizacao['idade'],
        100
    )
    
    candidatos['score_regime'] = 100 - np.minimum(
        df_predicao['diff_regime'] * fatores_penalizacao['regime'],
        100
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # SCORE PONDERADO FINAL
    # ═══════════════════════════════════════════════════════════════════
    candidatos['score_ponderado'] = (
        candidatos['score_area'] * pesos['area'] +
        candidatos['score_perfil'] * pesos['perfil'] +
        candidatos['score_cargo'] * pesos['cargo'] +
        candidatos['score_formacao'] * pesos['formacao'] +
        candidatos['score_idade'] * pesos['idade'] +
        candidatos['score_regime'] * pesos['regime']
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # RANQUEAR E RETORNAR TOP 10
    # ═══════════════════════════════════════════════════════════════════
    top_10 = candidatos.nlargest(10, 'score_ponderado')
    
    return top_10


def gerar_graficos_comparacao(df_resultados, y_test, probabilidades):
    """
    Gera gráficos de comparação dos modelos
    
    Args:
        df_resultados: DataFrame com resultados dos modelos
        y_test: Labels verdadeiros
        probabilidades: Dict com probabilidades de cada modelo
    
    Returns:
        Dict com paths dos gráficos salvos
    """
    
    # Criar diretório temporário compatível com Windows
    temp_dir = tempfile.gettempdir()
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 5)
    
    # ═══════════════════════════════════════════════════════════════════
    # GRÁFICO 1: COMPARAÇÃO DE MÉTRICAS
    # ═══════════════════════════════════════════════════════════════════
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    metricas = ['Acurácia', 'Precisão', 'Recall', 'F1-Score', 'ROC-AUC']
    x = np.arange(len(metricas))
    width = 0.25
    
    for i, modelo in enumerate(df_resultados['Modelo']):
        valores = df_resultados.iloc[i][metricas].values
        ax1.bar(x + i*width, valores, width, label=modelo)
    
    ax1.set_xlabel('Métricas', fontsize=12)
    ax1.set_ylabel('Score', fontsize=12)
    ax1.set_title('Comparação de Desempenho dos Modelos', fontsize=14, fontweight='bold')
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(metricas)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    path_metricas = os.path.join(temp_dir, 'comparacao_metricas.png')
    plt.tight_layout()
    plt.savefig(path_metricas, dpi=150, bbox_inches='tight')
    plt.close()
    
    # ═══════════════════════════════════════════════════════════════════
    # GRÁFICO 2: CURVAS ROC
    # ═══════════════════════════════════════════════════════════════════
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    
    cores = ['#800c0f', '#e1a125', '#292727']
    
    for i, (modelo_nome, prob) in enumerate(probabilidades.items()):
        fpr, tpr, _ = roc_curve(y_test, prob)
        auc = roc_auc_score(y_test, prob)
        
        if modelo_nome == 'LR':
            label = f'Logistic Regression (AUC = {auc:.3f})'
        elif modelo_nome == 'RF':
            label = f'Random Forest (AUC = {auc:.3f})'
        else:
            label = f'XGBoost (AUC = {auc:.3f})'
        
        ax2.plot(fpr, tpr, color=cores[i], linewidth=2, label=label)
    
    ax2.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Taxa de Falsos Positivos', fontsize=12)
    ax2.set_ylabel('Taxa de Verdadeiros Positivos', fontsize=12)
    ax2.set_title('Curvas ROC dos Modelos', fontsize=14, fontweight='bold')
    ax2.legend(loc='lower right')
    ax2.grid(True, alpha=0.3)
    
    path_roc = os.path.join(temp_dir, 'curvas_roc.png')
    plt.tight_layout()
    plt.savefig(path_roc, dpi=150, bbox_inches='tight')
    plt.close()
    
    return {
        'metricas': path_metricas,
        'roc': path_roc
    }