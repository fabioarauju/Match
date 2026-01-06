"""
Dicionários de códigos do sistema de match
Versão 2.0 - Estrutura otimizada
"""

# ═══════════════════════════════════════════════════════════════════════════
# ÁREAS DE ATUAÇÃO (v2.0)
# ═══════════════════════════════════════════════════════════════════════════
areas_atuacao = {
    # CLUSTER NEGÓCIOS (1-9)
    1: 'Administração e Negócios',
    2: 'Gestão de Projetos',
    3: 'Finanças',
    4: 'Recursos Humanos',
    5: 'Operações e Processos',
    6: 'Jurídico',
    7: 'Comércio e Varejo',
    8: 'Vendas',
    9: 'Atendimento ao Cliente',

    # CLUSTER CRIATIVO (13-21)
    13: 'Marketing',
    14: 'Design',
    15: 'Comunicação',
    16: 'Criação de conteúdo',
    17: 'Criação e Conteúdo',
    20: 'Cultura e Entretenimento',
    21: 'Educação',

    # CLUSTER TECNOLOGIA (26-28)
    26: 'Tecnologia',
    27: 'Pesquisa e Inovação',
    28: 'Infraestrutura e Telecomunicações',

    # CLUSTER ENGENHARIA (32-34)
    32: 'Construção e Imobiliário',
    33: 'Engenharia',
    34: 'Indústria',

    # CLUSTER INFRAESTRUTURA (37-39)
    37: 'Energia',
    38: 'Logística',
    39: 'Transporte e Mobilidade',

    # CLUSTER AGRONEGÓCIO (45-48)
    45: 'Meio Ambiente',
    48: 'Agronegócio',

    # CLUSTER SAÚDE (60-63)
    60: 'Saúde',
    63: 'Esportes e Bem-estar',

    # CLUSTER SEGURANÇA (70+)
    70: 'Segurança e Defesa'
}

# ═══════════════════════════════════════════════════════════════════════════
# NÍVEIS DE FORMAÇÃO
# ═══════════════════════════════════════════════════════════════════════════
niveis_formacao = {
    0: 'Sem formação acadêmica',
    1: 'Ensino Fundamental Incompleto',
    2: 'Ensino Fundamental Completo',
    3: 'Ensino Médio Incompleto',
    4: 'Ensino Médio Completo',
    5: 'Ensino Técnico Incompleto',
    6: 'Ensino Técnico Completo',
    7: 'Ensino Superior Incompleto',
    8: 'Ensino Superior Completo',
    9: 'Pós-Graduação Incompleta',
    10: 'Pós-Graduação Completa',
    11: 'Mestrado Incompleto',
    12: 'Mestrado Completo',
    13: 'Doutorado Incompleto',
    14: 'Doutorado Completo'
}

# ═══════════════════════════════════════════════════════════════════════════
# NÍVEIS DE CARGO
# ═══════════════════════════════════════════════════════════════════════════
niveis_cargo = {
    0: 'Primeiro emprego',
    1: 'Estagiário',
    2: 'Assistente',
    3: 'Analista',
    4: 'Supervisor',
    5: 'Coordenador',
    6: 'Gerente',
    7: 'Diretor',
    8: 'Autônomo'
}

# ═══════════════════════════════════════════════════════════════════════════
# FAIXAS ETÁRIAS
# ═══════════════════════════════════════════════════════════════════════════
faixas_etarias = {
    0: '18-19 anos',
    1: '20-24 anos',
    2: '25-29 anos',
    3: '30-34 anos',
    4: '35-39 anos',
    5: '40-44 anos',
    6: '45-49 anos',
    7: '50-54 anos',
    8: '55-59 anos',
    9: '60-64 anos',
    10: '65+ anos'
}

# ═══════════════════════════════════════════════════════════════════════════
# REGIMES DE TRABALHO
# ═══════════════════════════════════════════════════════════════════════════
regimes = {
    0: 'Híbrido',
    1: 'Presencial',
    2: 'Remoto',
    3: 'Indiferente'
}

# ═══════════════════════════════════════════════════════════════════════════
# CLUSTERS DE ÁREAS
# ═══════════════════════════════════════════════════════════════════════════
clusters_areas = {
    'Negócios': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'Criativo': [13, 14, 15, 16, 17, 20, 21],
    'Tecnologia': [26, 27, 28],
    'Engenharia': [32, 33, 34],
    'Infraestrutura': [37, 38, 39],
    'Agronegócio': [45, 48],
    'Saúde': [60, 63],
    'Segurança': [70]
}

# ═══════════════════════════════════════════════════════════════════════════
# PESOS PADRÃO
# ═══════════════════════════════════════════════════════════════════════════
PESOS_PADRAO = {
    'area': 0.35,
    'perfil': 0.30,
    'cargo': 0.20,
    'formacao': 0.10,
    'idade': 0.03,
    'regime': 0.02
}