# Projeto de Mineração de Dados: OmniStore

Este repositório contém a documentação e o código-fonte desenvolvidos para a análise de dados e implementação de um modelo preditivo para a **OmniStore**. O projeto foca em transformar dados brutos de navegação e vendas em inteligência estratégica para o negócio.

## 📋 Memorial Descritivo

### I. Seleção
A base de dados foi construída integrando tabelas de "Acessos e Compras" com "Detalhes dos Pedidos" via `ID_Sessao`, e posteriormente enriquecida com o cadastro de clientes. Utilizamos `Left Join` para preservar os dados de clientes que visitaram o site, mas não converteram, mantendo a integridade para análises de conversão.

### II. Pré-processamento
Realizamos a normalização de dados com `str.split(',')` e `str.strip()` para corrigir formatações inconsistentes. A conversão de tipos com `pd.to_numeric` e a remoção de duplicatas via `drop_duplicates()` garantiram a qualidade necessária para uma auditoria de dados confiável.

### III. Transformação (Feature Engineering)
Criamos indicadores estratégicos:
- **Total_Gasto**: Valor financeiro real (Preço x Quantidade).
- **Conversao**: Variável binária que identifica o sucesso da venda, base para o modelo preditivo.

### IV. Conclusões de Negócio
- **Ticket Médio**: R$ 154,67.
- **Destaque**: Categoria de *Eletrônicos* é a maior geradora de receita (R$ 21.776,00).
- **Insight**: O público jovem possui alto tráfego, mas baixa conversão.
- **Recomendação**: Adotar a mediana para relatórios financeiros (mitigando *outliers*) e focar o marketing em converter o público jovem.

### V. Documentação do Modelo Preditivo
- **Alvo**: Identificação de compradores (1) vs. visitantes (0).
- **Abordagem**: RFM (Recência, Frequência, Monetário), com remoção estratégica do valor monetário para evitar *data leakage*.
- **Algoritmo**: *Árvore de Decisão* (`max_depth=4`), escolhida pela **explicabilidade** das regras de negócio.
- **Performance**: Modelo conservador focado em minimizar *Falsos Positivos*, protegendo o orçamento de marketing.

### VI. Tecnologias Utilizadas
- **Linguagem**: Python.
- **Bibliotecas**: `pandas` (extração, limpeza e agregação) e `scikit-learn` (modelagem e métricas).

---

## 🚀 Como executar
1. Clone este repositório.
2. Certifique-se de ter as dependências instaladas: `pip install pandas scikit-learn openpyxl`.
3. Execute os scripts na ordem:
   - `python merge.py` (para gerar a base tratada)
   - `python machine_learning.py` (para rodar o modelo preditivo)

---
*Projeto desenvolvido como parte da atividade de Mineração de Dados.*