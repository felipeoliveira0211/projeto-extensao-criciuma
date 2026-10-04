# Conclusão do estudo

Pergunta: como os recursos da Prefeitura de Criciúma foram distribuídos entre as áreas em 2024 e 2025, e como a análise estatística pode ajudar a planejar melhor essa distribuição?

## Resultado

Educação, Saúde, Administração e Urbanismo apresentam os maiores valores nas bases recebidas. O gráfico `distribuicao.png` compara as mesmas áreas nos dois anos. A tabela `distribuicao_areas.csv` inclui também Cultura e Habitação, preservando as limitações de seus registros.

A base de correlações tem 14 áreas em dois anos, totalizando 28 observações. A variável principal é a participação de cada área na despesa liquidada das áreas comparáveis no mesmo ano. Das 25 variáveis candidatas, **16 superam 0,3 em módulo em Spearman**. Em Pearson, são 14. Não foram excluídas variáveis para elevar essa contagem.

## Normalidade

Para a variável principal, Shapiro–Wilk resultou em W = 0.692839 e p = 2.26072e-06. Com alfa de 5%: **rejeita normalidade**. O teste das 26 variáveis está em `shapiro_wilk.csv`; a inspeção visual está em `normalidade.png`.

O teste é um diagnóstico exploratório. Contagens são discretas, participações são limitadas e a mesma área aparece em dois anos. As observações não são completamente independentes. Não rejeitar H0 não prova normalidade, e rejeitá-la não torna Pearson automaticamente inválido. Spearman foi priorizado para descrever associações monotônicas entre áreas de escalas diferentes; não apenas por um resultado de Shapiro–Wilk.

## Uso no planejamento

A comparação permite identificar onde o gasto se concentra, acompanhar alterações de prioridade relativa e confrontar a distribuição com a estrutura dos programas e o volume administrativo. O aumento de Assistência Social e a queda de Urbanismo merecem avaliação de ações, reorganização administrativa e demanda antes de orientar novas decisões.

As correlações mais fortes acompanham principalmente a escala das áreas: orçamento, ações, dotações, empenhos e credores. Elas não demonstram eficiência, necessidade ou causalidade. Para recomendar uma distribuição melhor, será necessário acrescentar indicadores de demanda e resultados, como atendimentos, matrículas e metas.

## Limites que acompanham a conclusão

- Cultura tem quatro dotações com valores liquidados conflitantes em 2025. Habitação não consta como função em 2024. Por isso, ambas ficam fora do painel comparável; não se inventou valor zero.
- O denominador da participação é o total das 14 áreas comparáveis, não o total municipal.
- Os valores são nominais, sem correção de inflação. As fontes de orçamento e execução têm retratos diferentes; não somamos seus valores financeiros. A resposta monetária vem somente da base de programas e ações.
- Número de liquidações é contagem de lançamentos, não valor líquido de estornos. Os anexos de pagamentos não são necessários para a resposta escolhida.
- A seleção de áreas considera cobertura e qualidade, não o tamanho da correlação. As associações por ano e retirando uma área estão na mesma tabela de correlações.
- As 25 medidas são relacionadas entre si, não independentes. Com 14 áreas, não cabe afirmar que um modelo com 25 explicadores produziria previsões confiáveis.
- Os totais descrevem os arquivos recebidos, sem conciliação final com o balanço oficial. A análise não determina uma alocação ideal nem comprova irregularidade.
