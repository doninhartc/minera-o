import pandas as pd

# --- PARTE 1: LIMPEZA E PRÉ-PROCESSAMENTO ---

# Função para arrumar o problema das colunas que vieram todas em uma única string
def colunas(df):
    nova_coluna = df.columns[0]
    coluna_separada = [col.strip() for col in nova_coluna.split(',')]
    df_corrigida = df[nova_coluna].str.split(',', expand=True)
    df_corrigida.columns = coluna_separada
    
    for col in df_corrigida.columns:
        df_corrigida[col] = df_corrigida[col].str.strip()

    return df_corrigida

# Lendo as planilhas brutas
df_clientes_bruto = pd.read_excel('Base de Dados 1- Cadastro de Clientes.xlsx')
df_compras_bruto = pd.read_excel('Base de Dados 2- Acessos e Compras no Site.xlsx')
df_detalhes_bruto = pd.read_excel('Base de Dados 3- Detalhes dos Pedidos.xlsx')

# Limpando as 3 tabelas
df_clientes = colunas(df_clientes_bruto)
df_compras = colunas(df_compras_bruto)
df_detalhes = colunas(df_detalhes_bruto)


# --- PARTE 2: INTEGRAÇÃO E TRANSFORMAÇÃO ---

# Cruzamento 1 e 2 (Left Join para manter integridade)
df_mesclado = pd.merge(df_compras, df_detalhes, on='ID_Sessao', how='left')
df_mesclado_parte = pd.merge(df_clientes, df_mesclado, left_on='Nome', right_on='Nome_Cliente', how='left')

# Convertendo textos para números
if 'Preco_Unitario' in df_mesclado_parte.columns:
    df_mesclado_parte['Preco_Unitario'] = pd.to_numeric(df_mesclado_parte['Preco_Unitario'], errors='coerce').fillna(0)
if 'Quantidade' in df_mesclado_parte.columns:
    df_mesclado_parte['Quantidade'] = pd.to_numeric(df_mesclado_parte['Quantidade'], errors='coerce').fillna(0)

# Tentando achar a Idade ou calculando pela Data_Nascimento se existir
if 'Idade' in df_mesclado_parte.columns:
    df_mesclado_parte['Idade'] = pd.to_numeric(df_mesclado_parte['Idade'], errors='coerce')
elif 'idade' in df_mesclado_parte.columns:
    df_mesclado_parte['idade'] = pd.to_numeric(df_mesclado_parte['idade'], errors='coerce')
    df_mesclado_parte.rename(columns={'idade': 'Idade'}, inplace=True) 
elif 'Data_Nascimento' in df_mesclado_parte.columns:
    # Cria a coluna Idade baseada no ano de nascimento
    df_mesclado_parte['Data_Nascimento'] = pd.to_datetime(df_mesclado_parte['Data_Nascimento'], errors='coerce')
    df_mesclado_parte['Idade'] = 2026 - df_mesclado_parte['Data_Nascimento'].dt.year

# 1. Feature Engineering: Criando o Total_Gasto
if 'Preco_Unitario' in df_mesclado_parte.columns and 'Quantidade' in df_mesclado_parte.columns:
    df_mesclado_parte['Total_Gasto'] = df_mesclado_parte['Preco_Unitario'] * df_mesclado_parte['Quantidade']
else:
    df_mesclado_parte['Total_Gasto'] = 0

# 2. Tratamento de duplicidades sistêmicas 
print("\n" + "=" * 40)
print("AUDITORIA DE DADOS")
print("=" * 40)
tamanho_antes = len(df_mesclado_parte)
df_mesclado_parte = df_mesclado_parte.drop_duplicates()
tamanho_depois = len(df_mesclado_parte)
print(f"Auditoria: Foram removidas {tamanho_antes - tamanho_depois} linhas duplicadas/redundantes no cruzamento.\n")

# 3. Redução de dimensionalidade 
df_mesclado_parte = df_mesclado_parte.drop(columns=['Nome_Cliente'], errors='ignore')

# 4. Feature Engineering: Criando a coluna de Conversao solicitada na rubrica
df_mesclado_parte['Conversao'] = df_mesclado_parte['Total_Gasto'].apply(lambda x: 1 if x > 0 else 0)

# Salva a base bonitinha e consolidada com TODAS as exigências do professor
df_mesclado_parte.to_excel('arquivo_final_mesclado.xlsx', index=False)
print("Base consolidada gerada e salva com sucesso!\n")


# --- PARTE 3: KPIs DE NEGÓCIO COMPLETOS ---
print("=" * 40)
print("RESULTADOS DOS KPIs")
print("=" * 40)

# KPI 1: Ticket Médio
ticket_medio = df_mesclado_parte[df_mesclado_parte['Total_Gasto'] > 0]['Total_Gasto'].mean()
print(f"1. Ticket Médio: R$ {ticket_medio:.2f}")

# KPI 2: Taxa de Conversão por Categoria
if 'Categoria' in df_mesclado_parte.columns and 'Conversao' in df_mesclado_parte.columns:
    conversao_categoria = df_mesclado_parte.groupby('Categoria')['Conversao'].mean() * 100
    print("\n2. Taxa de Conversão por Categoria (%):")
    print(conversao_categoria.sort_values(ascending=False).round(2))

# KPI 3: Categoria de Maior Receita
if 'Categoria' in df_mesclado_parte.columns:
    receita_categoria = df_mesclado_parte.groupby('Categoria')['Total_Gasto'].sum().sort_values(ascending=False)
    print(f"\n3. Categoria de maior receita: {receita_categoria.index[0]} (R$ {receita_categoria.iloc[0]:.2f})")

# KPI 4: Perfil Demográfico Top Compradores
compradores = df_mesclado_parte[df_mesclado_parte['Total_Gasto'] > 0].copy()
print("\n4. Perfil Demográfico Top Compradores:")
if 'Idade' in compradores.columns:
    print(f"   Idade Média: {compradores['Idade'].mean():.0f} anos")
if 'Regiao' in compradores.columns:
    print(f"   Região que mais gasta: {compradores.groupby('Regiao')['Total_Gasto'].sum().idxmax()}")
else:
    print("   (Coluna de Região não encontrada na base de dados, KPI adaptado).")

# KPI 5: Melhores Clientes e o que têm em comum
if 'Nome' in compradores.columns:
    print("\n5. Nossos Melhores Clientes (Top 3):")
    melhores_clientes = compradores.groupby('Nome')['Total_Gasto'].sum().sort_values(ascending=False).head(3)
    print(melhores_clientes)
    nomes_top = melhores_clientes.index
    perfil_top = compradores[compradores['Nome'].isin(nomes_top)]
    if 'Idade' in perfil_top.columns and 'Categoria' in perfil_top.columns:
        print(f"   Em comum: Idade média de {perfil_top['Idade'].mean():.0f} anos e preferência por {perfil_top['Categoria'].mode()[0]}.")

# KPI 6: Relacionamento Perfil x Produto
if 'Regiao' in compradores.columns and 'Categoria' in compradores.columns:
    print("\n6. Relacionamento Região vs Categoria mais comprada:")
    perfil_produto = compradores.groupby('Regiao')['Categoria'].agg(lambda x: x.mode()[0] if not x.empty else 'N/A')
    print(perfil_produto)
elif 'Idade' in compradores.columns and 'Categoria' in compradores.columns:
    # Se não tem região, agrupa por faixa etária
    print("\n6. Relacionamento Faixa Etária vs Categoria mais comprada:")
    compradores['Faixa_Etaria'] = pd.cut(compradores['Idade'], bins=[0, 25, 40, 100], labels=['Jovem', 'Adulto', 'Senior'])
    perfil_produto = compradores.groupby('Faixa_Etaria', observed=False)['Categoria'].agg(lambda x: x.mode()[0] if not x.empty else 'N/A')
    print(perfil_produto)

# KPI 7: Casos Atípicos (Outliers)
maximo_gasto = df_mesclado_parte['Total_Gasto'].max()
outliers = df_mesclado_parte[df_mesclado_parte['Total_Gasto'] > (ticket_medio * 4)]
print(f"\n7. Casos Atípicos (Outliers):")
print(f"   Maior compra registrada: R$ {maximo_gasto:.2f}")
print(f"   Temos {len(outliers)} compras com valor mais de 4 vezes maior que o Ticket Médio (estas compras inflem a receita média distorcendo os relatórios diretores).")