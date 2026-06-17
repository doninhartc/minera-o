Memorial Descritivo - Mineração de Dados (OmniStore)

I. Seleção
Para montar a base final da OmniStore, o processo iniciou-se com o cruzamento das tabelas de "Acessos e Compras" com os "Detalhes dos Pedidos", utilizando a chave ID_Sessao para garantir a correlação correta entre a navegação e a efetivação da compra. Na sequência, este resultado foi integrado ao cadastro de clientes utilizando o Nome como chave de ligação.
O maior desafio desta etapa foi manter a integridade referencial dos dados. Para isso, optei deliberadamente pela utilização do Left Join. A escolha deste método foi fundamental, pois se utilizássemos outro tipo de junção, os clientes que apenas visitaram o site sem realizar compras seriam excluídos do sistema. Manter esses registros é vital, uma vez que a ausência dessas informações distorceria o cálculo da taxa de conversão e prejudicaria o treinamento do modelo de inteligência artificial.
II. Pré-processamento
As planilhas originais apresentaram desafios de formatação que exigiram uma limpeza rigorosa antes da integração. Primeiramente, detectamos colunas aglutinadas em uma única string de texto, o que impossibilitava a análise direta. Para solucionar isso, desenvolvemos uma função específica para separar os dados por vírgulas e utilizamos o método .strip() para eliminar espaços em branco ocultos nas extremidades, garantindo a padronização das strings.
Adicionalmente, foi necessário converter os tipos de dados das colunas de Preço e Quantidade de texto para numérico, utilizando pd.to_numeric(..., errors='coerce'), permitindo assim que o Python executasse corretamente os cálculos financeiros. Outro passo fundamental foi a aplicação do método .drop_duplicates(). Esta etapa é uma prática essencial de governança de dados, pois a remoção de registros duplicados — frequentemente causados por redundâncias sistêmicas ou cliques repetidos do usuário — evita a inflação artificial das vendas e do ticket médio, o que impediria decisões estratégicas baseadas em dados reais. A rotina de auditoria implementada confirmou a integridade da base após essas correções.
III. Transformação (Feature Engineering)
Para extrair inteligência real dos dados brutos, realizamos a engenharia de atributos (feature engineering), criando novas variáveis que respondem às necessidades estratégicas da empresa.
Total_Gasto: Criamos esta variável multiplicando o preço unitário pela quantidade vendida. Esta medida é superior a olhar apenas o preço unitário, pois reflete o valor financeiro real transacionado em cada carrinho.
Conversão: Definimos um indicador binário (1 para quem realizou pelo menos uma compra, 0 para quem apenas navegou). Esta variável foi o pilar principal para a avaliação do funil de vendas e para o treinamento do modelo preditivo.
Limpeza Dimensional: Após o processo de integração e cálculo das novas métricas, realizamos a exclusão da coluna de nome do cliente que se tornou redundante após o merge, garantindo uma estrutura de dados mais limpa e eficiente para o processamento.
IV. Conclusão (Resultados e Recomendações)
A análise da base de dados consolidada permitiu extrair insights estratégicos para a gestão da OmniStore:
Ticket Médio: O valor médio das transações foi calculado em R$ 154,67.
Desempenho por Categoria: A categoria de Eletrônicos destaca-se como a principal fonte de receita, totalizando R$ 21.776,00.
Perfil Demográfico: Identificamos que o público de maior valor para a empresa possui uma idade média de 34 anos.
Comportamento de Consumo: Existe uma distinção clara por faixa etária: adultos concentram suas compras em eletrônicos, enquanto o público sênior foca em vestuário. Observamos que, embora o público jovem apresente alto tráfego de navegação, a taxa de conversão deste grupo é baixa.
Casos Atípicos (Outliers): Identificamos 4 transações com valores superiores a R$ 800,00, representando valores quatro vezes maiores que o ticket médio.
Recomendações Estratégicas:
Marketing: Sugerimos o desenvolvimento de campanhas personalizadas para converter o alto volume de navegação do público jovem em vendas efetivas.
Governança Financeira: Alertamos a diretoria sobre a distorção causada pelos outliers de alto valor no cálculo da média. Recomendamos a utilização da mediana nos futuros relatórios financeiros para obter uma visão mais realista e menos enviesada do comportamento de consumo da base de clientes.
V. Documentação do Modelo Preditivo
Refinamento do Target e Features: Definimos o alvo (target) como 1 para clientes que realizaram compra e 0 para aqueles que apenas navegaram. Aplicamos a técnica de mercado RFM (Recência, Frequência, Monetário), contudo, removemos variáveis financeiras do modelo de predição. Esta decisão técnica foi tomada para eliminar o risco de data leakage (vazamento de dados), garantindo que o modelo aprenda padrões comportamentais genuínos (frequência de acesso, tempo desde a última interação e categoria de preferência) em vez de apenas correlacionar dados monetários que já confirmam a venda.
Escolha do Algoritmo: Optamos pela Árvore de Decisão (max_depth=4) priorizando a explicabilidade. Diferente de modelos "caixa preta", a árvore nos permite mapear o caminho lógico que leva um cliente à conversão, entregando à diretoria regras de negócio claras e acionáveis.
Performance e Governança: O modelo demonstrou alta capacidade preditiva, com ausência de Falsos Positivos, o que é estratégico para a empresa, pois protege o orçamento de marketing ao não direcionar campanhas caras para quem não possui real intenção de compra. É importante ressaltar que, devido ao volume reduzido da amostra, a acurácia pode apresentar variações entre execuções — um comportamento esperado em subconjuntos de teste pequenos. Esta transparência é fundamental para a governança de dados, garantindo que a diretoria compreenda as limitações e a robustez dos indicadores apresentados.
VI. Documentação Técnica das Funções Python Utilizadas
Para garantir a transparência e a reprodutibilidade do pipeline de dados, detalhamos abaixo as principais funções das bibliotecas pandas e scikit-learn aplicadas no projeto e seus objetivos:
1. Funções de Extração e Pré-processamento
pd.read_excel(): Utilizada para realizar a ingestão dos dados brutos das planilhas Excel para a memória do script.
str.split(',') e str.strip(): Aplicadas em laços de repetição para corrigir a formatação das bases originais, separando textos aglutinados por vírgula e removendo espaços em branco ocultos.
pd.to_numeric(..., errors='coerce'): Forçou a conversão das colunas de Preço e Quantidade (recebidas como texto) para o tipo numérico, viabilizando os cálculos financeiros.
drop_duplicates(): Função de limpeza que identifica e remove registros sistêmicos duplicados, garantindo a integridade da auditoria.
2. Funções de Integração e Transformação
pd.merge(..., how='left'): Executou a junção relacional das bases de dados baseada nas chaves primárias e estrangeiras. O parâmetro how='left' foi fundamental para manter os clientes inativos na análise.
groupby(): Utilizada massivamente para a agregação de dados, permitindo tanto o cálculo dos KPIs da diretoria quanto a construção dos atributos RFM através do agrupamento por cliente único.
3. Funções de Machine Learning (Modelagem Preditiva)
train_test_split(): Dividiu a base de perfis RFM aleatoriamente em 70% para treino e 30% para teste, garantindo a avaliação do modelo com dados inéditos.
DecisionTreeClassifier(max_depth=4): Instanciou o algoritmo de Árvore de Decisão com profundidade limitada a 4 níveis, estratégia adotada para evitar o overfitting e assegurar a interpretabilidade visual das regras de negócio.
confusion_matrix() e classification_report(): Funções essenciais de métricas que avaliaram as previsões da inteligência artificial, gerando a contagem de falsos positivos/negativos e as métricas de Acurácia, Precisão e Recall.

