"""
Sistema de Match Candidato-Vaga
Aplicação Streamlit com Identidade Visual Personalizada
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import subprocess
import sys

# TEMPORÁRIO: Instalar gspread manualmente
try:
    import gspread
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gspread==5.12.3", "oauth2client==4.1.3"])
    import gspread

# Importar módulos
from utils.dicionarios import (
    areas_atuacao, niveis_formacao, niveis_cargo,
    faixas_etarias, regimes, PESOS_PADRAO
)
from utils.google_sheets import carregar_planilha
from utils.preparacao import preparar_dados_completos
from utils.comparacao import treinar_modelos, gerar_recomendacoes, gerar_graficos_comparacao

# Configuração da página
st.set_page_config(
    page_title="Sistema de Match",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════
# CSS CUSTOMIZADO - IDENTIDADE VISUAL DA EMPRESA
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Cores da empresa */
    :root {
        --vermelho-principal: #800c0f;
        --dourado-principal: #e1a125;
        --cinza-escuro: #292727;
        --cinza-claro: #e4e4e4;
    }
    
    /* Header principal */
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(135deg, #800c0f 0%, #e1a125 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    /* Sidebar - MELHORADA LEGIBILIDADE */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #800c0f 0%, #292727 100%);
    }
    
    /* Textos da sidebar - CONTRASTES MELHORADOS */
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffd700 !important;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    /* Valores dos inputs */
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stNumberInput > div {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Input fields */
    [data-testid="stSidebar"] input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #000000 !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] input:focus {
        border-color: #ffd700 !important;
        box-shadow: 0 0 5px rgba(255, 215, 0, 0.5) !important;
    }
    
    /* Markdown text na sidebar */
    [data-testid="stSidebar"] p {
        color: #FFF !important;
        font-size: 0.95rem;
    }
    
    /* Caption na sidebar */
    [data-testid="stSidebar"] .stCaption {
        color: #e1a125 !important;
        font-style: italic;
    }
    
    /* Success/Warning na sidebar */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stWarning {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Botão principal */
    .stButton > button {
        background: linear-gradient(135deg, #800c0f 0%, #e1a125 100%);
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(128, 12, 15, 0.3);
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(128, 12, 15, 0.4);
    }
    
    /* Botão de download */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #800c0f 0%, #e1a125 100%);
        color: white !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
    }
    
    /* Métricas - MELHOR CONTRASTE */
    [data-testid="stMetricValue"] {
        color: #800c0f;
        font-weight: bold;
        font-size: 1.8rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #292727;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Cards de expansão (candidatos) - MELHOR LEGIBILIDADE */
    .streamlit-expanderHeader {
        background-color: #f8f8f8;
        border-left: 4px solid #800c0f;
        border-radius: 5px;
        font-weight: bold;
        color: #292727 !important;
        font-size: 1.05rem;
        padding: 0.75rem 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e4e4e4;
        border-left-color: #e1a125;
    }
    
    /* Conteúdo dentro dos expanders */
    .streamlit-expanderContent {
        background-color: #fafafa;
        padding: 1rem;
    }
    
    .streamlit-expanderContent p,
    .streamlit-expanderContent div {
        color: #292727 !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Títulos dentro dos cards */
    .streamlit-expanderContent strong {
        color: #800c0f !important;
        font-weight: 700;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #800c0f 0%, #e1a125 100%);
    }
    
    /* Info boxes - MELHOR CONTRASTE */
    .stAlert {
        border-left: 4px solid #e1a125;
        background-color: #e1a125;
        color: #292727 !important;
    }
    
    .stInfo {
        background-color: #e8f4f8;
        border-left: 4px solid #3498db;
        color: #1a1a1a !important;
    }
    
    /* Success boxes */
    .stSuccess {
        background-color: rgba(225, 161, 37, 0.15);
        border-left: 4px solid #e1a125;
        color: #292727 !important;
        font-weight: 500;
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: rgba(128, 12, 15, 0.15);
        border-left: 4px solid #800c0f;
        color: #292727 !important;
        font-weight: 500;
    }
    
    /* Error boxes */
    .stError {
        background-color: rgba(128, 12, 15, 0.2);
        border-left: 4px solid #800c0f;
        color: #292727 !important;
        font-weight: 600;
    }
    
    /* DataFrames - MELHOR LEGIBILIDADE */
    .dataframe {
        border: 2px solid #e4e4e4;
        font-size: 0.95rem;
    }
    
    .dataframe thead tr th {
        background-color: #800c0f !important;
        color: white !important;
        font-weight: bold;
        padding: 0.75rem !important;
        text-align: center;
    }
    
    .dataframe tbody tr td {
        padding: 0.5rem !important;
        color: #292727 !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    .dataframe tbody tr:hover {
        background-color: #fff9e6;
    }
    
    /* Dividers */
    hr {
        border-color: #e1a125;
        border-width: 2px;
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #292727;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 2px solid #e1a125;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e4e4e4;
        border-radius: 5px 5px 0 0;
        color: #292727 !important;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #800c0f;
        color: white !important;
        font-weight: 600;
    }
    
    /* Subheaders - MELHOR CONTRASTE */
    h1, h2, h3 {
        color: #800c0f !important;
        font-weight: 700;
    }
    
    h1 {
        font-size: 2.5rem;
    }
    
    h2 {
        font-size: 2rem;
    }
    
    h3 {
        font-size: 1.5rem;
    }
    
    /* Parágrafos normais */
    p {
        color: #292727;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Badge de score - MELHOR VISIBILIDADE */
    .score-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
    }
    
    .score-excelente {
        background: linear-gradient(135deg, #e1a125 0%, #800c0f 100%);
        color: white !important;
    }
    
    .score-bom {
        background-color: #e1a125;
        color: #292727 !important;
        font-weight: 700;
    }
    
    .score-moderado {
        background-color: #e4e4e4;
        color: #292727 !important;
        font-weight: 600;
        border: 2px solid #c0c0c0;
    }
    
    /* Spinner de loading */
    .stSpinner > div {
        border-top-color: #800c0f !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CARREGAMENTO AUTOMÁTICO DOS DADOS
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def carregar_dados_inicial():
    """Carrega dados do Google Sheets uma única vez"""
    try:
        PLANILHA_ID = "1tM1LSnFLlp_CF8yAWFE0w6r1qTV9Smy_mvDx0Wx1x-U"
        
        candidatos_raw = carregar_planilha(PLANILHA_ID, aba="candidatos")
        vagas_raw = carregar_planilha(PLANILHA_ID, aba="vagas")
        matches_raw = carregar_planilha(PLANILHA_ID, aba="matches")
        
        if candidatos_raw is not None and vagas_raw is not None and matches_raw is not None:
            return {
                'candidatos': candidatos_raw,
                'vagas': vagas_raw,
                'matches': matches_raw,
                'sucesso': True,
                'erro': None
            }
        else:
            return {
                'candidatos': None,
                'vagas': None,
                'matches': None,
                'sucesso': False,
                'erro': 'Erro ao carregar uma ou mais abas'
            }
    except Exception as e:
        return {
            'candidatos': None,
            'vagas': None,
            'matches': None,
            'sucesso': False,
            'erro': str(e)
        }

# Carregar dados automaticamente
with st.spinner("📂 Carregando dados..."):
    dados = carregar_dados_inicial()

# Header
st.markdown('<p class="main-header">Sistema de Match</p>', unsafe_allow_html=True)
st.markdown("---")

# Verificar se dados foram carregados
if not dados['sucesso']:
    st.error(f"❌ Erro ao carregar dados: {dados['erro']}")
    st.info("""
    **💡 Possíveis causas:**
    - Arquivo `credentials.json` não encontrado
    - Planilha não compartilhada com a conta de serviço
    - ID da planilha incorreto no código
    
    **🔧 Solução:**
    1. Verifique se `credentials.json` está na pasta raiz
    2. Compartilhe a planilha com o email da conta de serviço
    3. Atualize o PLANILHA_ID no código
    """)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR - CONFIGURAÇÕES DA VAGA
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📋 Configuração da Vaga")
    st.markdown("---")
    
    # Área
    area_opcoes = [(v, k) for k, v in areas_atuacao.items()]
    area_sel = st.selectbox(
        "🏢 Área de Atuação",
        options=area_opcoes,
        format_func=lambda x: f"{x[0]}",
        index=0
    )
    codigo_area = area_sel[1]
    
    # Cargo
    cargo_opcoes = [(v, k) for k, v in niveis_cargo.items()]
    cargo_sel = st.selectbox(
        "💼 Nível do Cargo",
        options=cargo_opcoes,
        format_func=lambda x: x[0],
        index=3
    )
    codigo_cargo = cargo_sel[1]
    
    # Formação
    formacao_opcoes = [(v, k) for k, v in niveis_formacao.items()]
    formacao_sel = st.selectbox(
        "🎓 Formação Mínima",
        options=formacao_opcoes,
        format_func=lambda x: x[0],
        index=8
    )
    codigo_formacao = formacao_sel[1]
    
    # Idade
    idade_opcoes = [(v, k) for k, v in faixas_etarias.items()]
    idade_sel = st.selectbox(
        "👤 Faixa Etária",
        options=idade_opcoes,
        format_func=lambda x: x[0],
        index=2
    )
    codigo_idade = idade_sel[1]
    
    # Regime
    regime_opcoes = [(v, k) for k, v in regimes.items()]
    regime_sel = st.selectbox(
        "🏠 Regime de Trabalho",
        options=regime_opcoes,
        format_func=lambda x: x[0],
        index=0
    )
    codigo_regime = regime_sel[1]
    
    st.markdown("---")
    st.markdown("### 🎨 Perfil Comportamental")
    st.caption("A soma dos 4 valores deve ser igual a 100")
    
    col1, col2 = st.columns(2)
    
    with col1:
        autoridade = st.number_input(
            "💪 Autoridade",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=0.1,
            help="Nível de autoridade e liderança"
        )
        
        preservacao = st.number_input(
            "🛡️ Preservação",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=0.1,
            help="Nível de estabilidade e segurança"
        )
    
    with col2:
        prestigio = st.number_input(
            "⭐ Prestígio",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=0.1,
            help="Nível de prestígio e status"
        )
        
        formalidade = st.number_input(
            "📋 Formalidade",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=0.1,
            help="Nível de processos e estrutura"
        )
    
    soma_perfil = autoridade + prestigio + preservacao + formalidade
    
    if abs(soma_perfil - 100) > 1:
        st.warning(f"⚠️ Soma: {soma_perfil:.2f} (deve ser 100)")
    else:
        st.success(f"✅ Soma: {soma_perfil:.2f}")
    
    st.markdown("---")
    
    # Pesos do modelo (expandido)
    with st.expander("⚖️ Ajustar Pesos do Modelo"):
        st.info("Ajuste a importância de cada aspecto")
        
        peso_area = st.slider("Área (%)", 0, 100, 35, 1)
        peso_perfil = st.slider("Perfil (%)", 0, 100, 30, 1)
        peso_cargo = st.slider("Cargo (%)", 0, 100, 20, 1)
        peso_formacao = st.slider("Formação (%)", 0, 100, 10, 1)
        peso_idade = st.slider("Idade (%)", 0, 100, 3, 1)
        peso_regime = st.slider("Regime (%)", 0, 100, 2, 1)
        
        soma_pesos = peso_area + peso_perfil + peso_cargo + peso_formacao + peso_idade + peso_regime
        
        if abs(soma_pesos - 100) > 1:
            st.warning(f"⚠️ Total: {soma_pesos}%")
        else:
            st.success(f"✅ Total: {soma_pesos}%")
    
    # Se não ajustou os pesos, usar padrão
    if 'peso_area' not in locals():
        peso_area, peso_perfil = 35, 30
        peso_cargo, peso_formacao = 20, 10
        peso_idade, peso_regime = 3, 2
        soma_pesos = 100
    
    pesos = {
        'area': peso_area / 100,
        'perfil': peso_perfil / 100,
        'cargo': peso_cargo / 100,
        'formacao': peso_formacao / 100,
        'idade': peso_idade / 100,
        'regime': peso_regime / 100
    }
    
    st.markdown("---")
    
    # Botão de processar
    processar = st.button("🚀 Gerar Recomendações", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

# Mostrar resumo dos dados carregados
st.markdown("### 📊 Base de Dados")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 Candidatos", f"{len(dados['candidatos']):,}")

with col2:
    st.metric("📋 Vagas Históricas", f"{len(dados['vagas']):,}")

with col3:
    st.metric("✅ Matches Registrados", f"{len(dados['matches']):,}")

st.markdown("---")

# Processar quando clicar no botão
if processar:
    # Validações
    if abs(soma_perfil - 100) > 1:
        st.error("❌ A soma do perfil comportamental deve ser próxima de 100!")
        st.stop()
    
    if abs(soma_pesos - 100) > 1:
        st.error("❌ A soma dos pesos deve ser 100%!")
        st.stop()
    
    # Criar dicionário da vaga
    vaga = {
        'codigo_area': codigo_area,
        'codigo_cargo': codigo_cargo,
        'codigo_formacao': codigo_formacao,
        'codigo_idade': codigo_idade,
        'codigo_regime': codigo_regime,
        'autoridade': autoridade,
        'prestigio': prestigio,
        'preservacao': preservacao,
        'formalidade': formalidade
    }
    
    # ETAPA 1: PREPARAR DADOS (silencioso - sem mensagens)
    try:
        dados_completos = preparar_dados_completos(
            dados['candidatos'],
            dados['vagas'],
            dados['matches']
        )
        
        if dados_completos is None:
            st.error("❌ Erro na preparação dos dados.")
            st.stop()
        
    except Exception as e:
        st.error(f"❌ Erro na preparação: {str(e)}")
        with st.expander("🔍 Ver detalhes"):
            import traceback
            st.code(traceback.format_exc())
        st.stop()
    
    # ETAPA 2: TREINAR MODELOS (silencioso - sem mensagens)
    try:
        features = [
            'diff_idade', 'diff_formacao', 'diff_area', 'diff_cargo', 'diff_regime',
            'diff_autoridade', 'diff_prestigio', 'diff_preservacao',
            'diff_formalidade', 'distancia_perfil'
        ]
        
        X = dados_completos[features]
        y = dados_completos['match']
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        resultado_treino = treinar_modelos(X_train, y_train, X_test, y_test)
        
        modelos = resultado_treino['modelos']
        df_resultados = resultado_treino['resultados']
        probabilidades = resultado_treino['probabilidades']
        
    except Exception as e:
        st.error(f"❌ Erro no treinamento: {str(e)}")
        with st.expander("🔍 Ver detalhes"):
            import traceback
            st.code(traceback.format_exc())
        st.stop()
    
    # ETAPA 3: GERAR RECOMENDAÇÕES (silencioso - sem mensagens)
    try:
            fatores_penalizacao = {
                'area': 10.0,
                'perfil': 1.5,
                'cargo': 12.5,
                'formacao': 7.0,
                'idade': 10.0,
                'regime': 25.0
            }
            
            # Gerar top 10 para cada modelo
            top_10_negocio = gerar_recomendacoes(
                dados['candidatos'],
                vaga,
                modelos,
                pesos,
                fatores_penalizacao
            )
            
            # Top 10 por modelo ML individual
            candidatos_temp = dados['candidatos'].copy()
            
            # Converter colunas para numérico
            colunas_para_converter = [
                'Intervalo_Idade_Código', 'Nível_Formação_Código',
                'Área_Atuação_Código', 'Nível do cargo código',
                'Regime código', 'autoridade', 'prestigio',
                'preservacao', 'formalidade'
            ]
            
            for col in colunas_para_converter:
                if col in candidatos_temp.columns:
                    candidatos_temp[col] = pd.to_numeric(candidatos_temp[col], errors='coerce')
            
            candidatos_temp = candidatos_temp.fillna({
                'Intervalo_Idade_Código': 2, 'Nível_Formação_Código': 4,
                'Área_Atuação_Código': 1, 'Nível do cargo código': 3,
                'Regime código': 0, 'autoridade': 25.0, 'prestigio': 25.0,
                'preservacao': 25.0, 'formalidade': 25.0
            })
            
            # Calcular features
            features_lista = []
            for idx, cand in candidatos_temp.iterrows():
                feats = {
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
                
                feats['distancia_perfil'] = np.sqrt(
                    feats['diff_autoridade']**2 + feats['diff_prestigio']**2 +
                    feats['diff_preservacao']**2 + feats['diff_formalidade']**2
                )
                
                features_lista.append(feats)
            
            df_pred = pd.DataFrame(features_lista)
            
            # Preencher NaN
            for col in df_pred.columns:
                max_val = df_pred[col].max()
                if pd.isna(max_val) or max_val == 0:
                    max_val = 10
                df_pred[col] = df_pred[col].fillna(max_val)
            
            # Fazer previsões
            candidatos_temp['prob_lr'] = modelos['LR'].predict_proba(df_pred)[:, 1]
            candidatos_temp['prob_rf'] = modelos['RF'].predict_proba(df_pred)[:, 1]
            candidatos_temp['prob_xgb'] = modelos['XGB'].predict_proba(df_pred)[:, 1]
            
            top_10_lr = candidatos_temp.nlargest(10, 'prob_lr')[['Nome Completo', 'prob_lr']]
            top_10_rf = candidatos_temp.nlargest(10, 'prob_rf')[['Nome Completo', 'prob_rf']]
            top_10_xgb = candidatos_temp.nlargest(10, 'prob_xgb')[['Nome Completo', 'prob_xgb']]
            
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        with st.expander("🔍 Ver detalhes"):
            import traceback
            st.code(traceback.format_exc())
        st.stop()
    
    # ═══════════════════════════════════════════════════════════════════
    # EXIBIR RESULTADOS
    # ═══════════════════════════════════════════════════════════════════
    
    st.success("✅ Análise concluída!")
    
    st.markdown("---")
    
    # Configuração da Vaga Analisada
    st.markdown("### 📋 Configuração da Vaga Analisada")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Área", areas_atuacao[codigo_area])
        st.metric("💼 Cargo", niveis_cargo[codigo_cargo])
    
    with col2:
        st.metric("🎓 Formação", niveis_formacao[codigo_formacao])
        st.metric("👤 Faixa Etária", faixas_etarias[codigo_idade])
    
    with col3:
        st.metric("🏠 Regime", regimes[codigo_regime])
        
    with col4:
        st.markdown("**🎨 Perfil Comportamental**")
        st.write(f"💪 Autoridade: {autoridade:.1f}")
        st.write(f"⭐ Prestígio: {prestigio:.1f}")
        st.write(f"🛡️ Preservação: {preservacao:.1f}")
        st.write(f"📋 Formalidade: {formalidade:.1f}")
    
    st.markdown("---")
    
    # Métricas dos Modelos
    st.markdown("### 📈 Desempenho dos Modelos")
    st.dataframe(
        df_resultados.style.format({
            'Acurácia': '{:.1%}',
            'Precisão': '{:.1%}',
            'Recall': '{:.1%}',
            'F1-Score': '{:.1%}',
            'ROC-AUC': '{:.3f}',
            'Score_Total': '{:.1%}'
        }).background_gradient(cmap='RdYlGn', subset=['Acurácia', 'F1-Score', 'ROC-AUC']),
        use_container_width=True
    )
    
    melhor = df_resultados.loc[df_resultados['Score_Total'].idxmax()]
    st.info(f"🏆 **Melhor Modelo:** {melhor['Modelo']} (Score: {melhor['Score_Total']:.1%})")
    
    st.markdown("---")
    
    # Tabela Comparativa Top 10
    st.markdown("### 📊 Top 10 por Modelo")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Modelo de Negócio", "📊 Logistic Regression", "🌲 Random Forest", "⚡ XGBoost"])
    
    with tab1:
        st.dataframe(
            top_10_negocio[['Nome Completo', 'score_ponderado', 'prob_lr', 'prob_rf', 'prob_xgb']].rename(columns={
                'Nome Completo': 'Candidato',
                'score_ponderado': 'Score (%)',
                'prob_lr': 'LR (%)',
                'prob_rf': 'RF (%)',
                'prob_xgb': 'XGB (%)'
            }).style.format({
                'Score (%)': '{:.1f}',
                'LR (%)': '{:.1%}',
                'RF (%)': '{:.1%}',
                'XGB (%)': '{:.1%}'
            }),
            use_container_width=True
        )
    
    with tab2:
        st.dataframe(
            top_10_lr.rename(columns={'Nome Completo': 'Candidato', 'prob_lr': 'Match (%)'}).style.format({
                'Match (%)': '{:.1%}'
            }),
            use_container_width=True
        )
    
    with tab3:
        st.dataframe(
            top_10_rf.rename(columns={'Nome Completo': 'Candidato', 'prob_rf': 'Match (%)'}).style.format({
                'Match (%)': '{:.1%}'
            }),
            use_container_width=True
        )
    
    with tab4:
        st.dataframe(
            top_10_xgb.rename(columns={'Nome Completo': 'Candidato', 'prob_xgb': 'Match (%)'}).style.format({
                'Match (%)': '{:.1%}'
            }),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Top 10 Detalhado
    st.markdown("### 🏆 Top 10 Candidatos Recomendados")
    
    for i, (idx, cand) in enumerate(top_10_negocio.iterrows(), 1):
        score = cand['score_ponderado']
        
        if score >= 90:
            badge_class = "score-excelente"
            status = "EXCELENTE MATCH"
            emoji = "🌟"
        elif score >= 80:
            badge_class = "score-bom"
            status = "MUITO BOM"
            emoji = "✅"
        else:
            badge_class = "score-moderado"
            status = "BOM"
            emoji = "ℹ️"
        
        with st.expander(
            f"{emoji} #{i} - {cand['Nome Completo']} • Score: {score:.1f}/100",
            expanded=(i<=3)
        ):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📋 Informações**")
                st.write(f"**Área:** {cand['Área de Atuação']}")
                st.write(f"**Cargo:** {cand['Nível do cargo atual']}")
                st.write(f"**Formação:** {cand['Nível de Formação']}")
            
            with col2:
                st.markdown("**🎯 Scores**")
                st.write(f"Área: {cand['score_area']:.0f}/100")
                st.write(f"Perfil: {cand['score_perfil']:.0f}/100")
                st.write(f"Cargo: {cand['score_cargo']:.0f}/100")
            
            with col3:
                st.markdown("**🤖 ML**")
                st.write(f"LR: {cand['prob_lr']:.1%}")
                st.write(f"RF: {cand['prob_rf']:.1%}")
                st.write(f"XGB: {cand['prob_xgb']:.1%}")
            
            st.progress(score / 100)
            st.markdown(f'<span class="score-badge {badge_class}">{status}</span>', unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("---")
    st.markdown("### 📊 Análise Comparativa")
    
    graficos = gerar_graficos_comparacao(df_resultados, y_test, probabilidades)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(graficos['metricas'], use_column_width=True)
    
    with col2:
        st.image(graficos['roc'], use_column_width=True)
    
    # Botão de Download PDF
    st.markdown("---")
    
    # Preparar dados para PDF (simplificado - você pode expandir depois)
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    elements.append(Paragraph("Sistema de Match Candidato-Vaga", styles['Title']))
    elements.append(Paragraph("Relatório de Recomendações", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Configuração da Vaga
    elements.append(Paragraph("Configuração da Vaga:", styles['Heading3']))
    config_data = [
        ['Área', areas_atuacao[codigo_area]],
        ['Cargo', niveis_cargo[codigo_cargo]],
        ['Formação', niveis_formacao[codigo_formacao]],
        ['Idade', faixas_etarias[codigo_idade]],
        ['Regime', regimes[codigo_regime]]
    ]
    config_table = Table(config_data, colWidths=[150, 300])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#800c0f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(config_table)
    elements.append(Spacer(1, 20))
    
    # Top 10
    elements.append(Paragraph("Top 10 Candidatos:", styles['Heading3']))
    top_data = [['#', 'Nome', 'Score']]
    for i, (idx, cand) in enumerate(top_10_negocio.iterrows(), 1):
        top_data.append([str(i), cand['Nome Completo'], f"{cand['score_ponderado']:.1f}"])
    
    top_table = Table(top_data, colWidths=[30, 350, 70])
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#800c0f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(top_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📄 Baixar Relatório PDF",
            data=buffer,
            file_name="relatorio_match.pdf",
            mime="application/pdf",
            use_container_width=True
        )

else:
    # Vaga configurada
    st.markdown("### 📋 Vaga Configurada")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏢 Área", areas_atuacao[codigo_area])
        st.metric("💼 Cargo", niveis_cargo[codigo_cargo])
    
    with col2:
        st.metric("🎓 Formação", niveis_formacao[codigo_formacao])
        st.metric("👤 Idade", faixas_etarias[codigo_idade])
    
    with col3:
        st.metric("🏠 Regime", regimes[codigo_regime])
        st.metric("🎨 Perfil", f"A:{autoridade:.0f} P:{prestigio:.0f}")
    
    st.info("👈 Configure a vaga na barra lateral e clique em 'Gerar Recomendações'")

# Footer
st.markdown('<div class="footer">Sistema de Match | By Alavank  </div>', unsafe_allow_html=True)