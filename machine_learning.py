import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

print("A iniciar o Pipeline de Machine Learning (Análise RFM)...")

# 1. Carregar a base unificada
df_mesclado = pd.read_excel('arquivo_final_mesclado.xlsx')

print("\n--- ENGENHARIA DE ATRIBUTOS (FEATURE ENGINEERING) ---")

# 2. FREQUÊNCIA: Quantas sessões o cliente teve?
frequencia = df_mesclado.groupby('Nome')['ID_Sessao'].nunique().reset_index()
frequencia.columns = ['Nome', 'Frequencia_Acesso']

# NOTA: O Ticket Médio foi removido intencionalmente das features.
# Usá-lo seria um vazamento de dados (data leakage), pois ele é derivado
# diretamente das compras — ou seja, entregaria o alvo ao modelo antes
# da predição, inflando a acurácia artificialmente para 100%.

# 3. CATEGORIA DE PREFERÊNCIA
if 'Categoria' in df_mesclado.columns:
    categoria_pref = df_mesclado.groupby('Nome')['Categoria'].agg(
        lambda x: x.mode()[0] if not x.mode().empty else 'Desconhecida'
    ).reset_index()
    categoria_pref.columns = ['Nome', 'Categoria_Preferencia']
else:
    categoria_pref = pd.DataFrame({'Nome': df_mesclado['Nome'].unique(), 'Categoria_Preferencia': 'Desconhecida'})

# 4. RECÊNCIA: Há quantos dias foi a última compra?
df_mesclado['Data_Compra'] = pd.to_datetime(df_mesclado['Data_Compra'], errors='coerce')
data_atual = df_mesclado['Data_Compra'].max()
ultima_compra = df_mesclado.groupby('Nome')['Data_Compra'].max().reset_index()
ultima_compra['Recencia_Dias'] = (data_atual - ultima_compra['Data_Compra']).dt.days

# 5. VARIÁVEL ALVO (TARGET)
# Baseada em Compra_Finalizada: 1 = realizou ao menos uma compra, 0 = apenas navegou.
# Essa abordagem é tecnicamente correta pois usa um campo de comportamento
# independente dos valores monetários, evitando data leakage.
alvo = df_mesclado.groupby('Nome')['Compra_Finalizada'].apply(
    lambda x: 1 if (x == 'Sim').any() else 0
).reset_index()
alvo.columns = ['Nome', 'Alvo_Compra']

# 6. CONSOLIDAR TUDO NO PERFIL DO CLIENTE
df_ia = pd.DataFrame({'Nome': df_mesclado['Nome'].unique()})
df_ia = pd.merge(df_ia, frequencia, on='Nome', how='left')
df_ia = pd.merge(df_ia, categoria_pref, on='Nome', how='left')
df_ia = pd.merge(df_ia, ultima_compra[['Nome', 'Recencia_Dias']], on='Nome', how='left')
df_ia = pd.merge(df_ia, alvo, on='Nome', how='left')

# Clientes sem data de compra recebem 999 dias para sinalizar inatividade à IA
df_ia['Recencia_Dias'] = df_ia['Recencia_Dias'].fillna(999)

print(f"Atributos criados com sucesso! Clientes processados: {len(df_ia)}")

print("\n--- TREINAMENTO DO MODELO ---")

# 7. SELEÇÃO DAS FEATURES
# Features: Frequência de Acesso, Recência e Categoria de Preferência.
# Excluímos dados monetários para garantir que o modelo aprenda padrões
# comportamentais genuínos, não apenas quem já gastou dinheiro.
X = df_ia[['Frequencia_Acesso', 'Recencia_Dias', 'Categoria_Preferencia']]
y = df_ia['Alvo_Compra']

# Converter categorias de texto para números
X = pd.get_dummies(X, drop_first=True)

# Separar 70% para treino e 30% para teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Treinar a Árvore de Decisão
modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
modelo.fit(X_train, y_train)

# Testar o modelo
y_pred = modelo.predict(X_test)

print("\nMatriz de Confusão:")
print(confusion_matrix(y_test, y_pred))

print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))