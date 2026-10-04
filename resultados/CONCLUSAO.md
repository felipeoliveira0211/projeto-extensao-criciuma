# Conclusão do estudo

A análise dos dados de 2024 e 2025 mostrou que os maiores valores ficaram em Educação, Saúde, Administração e Urbanismo. Também apareceram mudanças importantes, como o aumento em Assistência Social e a redução em Urbanismo. Isso mostra que a distribuição mudou entre os anos, mas os números sozinhos não explicam se essas mudanças acompanharam as necessidades da população.

Entre as 25 variáveis estudadas, 16 atingiram o limite de correlação definido em Spearman. As relações mais fortes envolveram orçamento, ações, empenhos e credores, mostrando que áreas com maior participação nos recursos também costumam ter uma estrutura de execução maior. O boxplot destacou Educação nos dois anos pelo valor elevado em relação às demais áreas. Esse destaque não significa erro ou gasto excessivo.

Para o planejamento futuro, a Prefeitura pode usar esses resultados para acompanhar mudanças na distribuição, comparar o orçamento com a execução e investigar aumentos ou reduções mais expressivos. O próximo passo é cruzar os gastos com informações como atendimentos, matrículas, filas e metas. Assim, a análise ajuda a decidir com mais informação, sem concluir que uma área precisa de mais ou menos recursos apenas pelo valor que recebeu.

Essas conclusões se limitam às bases disponíveis. A comparação estatística utilizou 14 áreas presentes nos dois anos, com valores nominais e algumas limitações de cadastro documentadas no estudo.

## Evidências da análise

Pergunta: como os recursos da Prefeitura de Criciúma foram distribuídos entre as áreas em 2024 e 2025, e como a análise estatística pode ajudar a planejar melhor essa distribuição?

## Resultado

Educação, Saúde, Administração e Urbanismo apresentam os maiores valores nas bases recebidas. O gráfico `distribuicao.png` compara as mesmas áreas nos dois anos. A tabela `distribuicao_areas.csv` inclui também Cultura e Habitação, preservando as limitações de seus registros.

A base de correlações tem 14 áreas em dois anos, totalizando 28 observações. A variável principal é a participação de cada área na despesa liquidada das áreas comparáveis no mesmo ano. Das 25 variáveis candidatas, **16 superam 0,3 em módulo em Spearman**. Em Pearson, são 14. Não foram excluídas variáveis para elevar essa contagem.

## Quais variáveis atingiram o limite?

Foram **16**, e não apenas 15. Todas estão abaixo. A estabilidade significa que a relação permanece além de ±0,3 ao retirar uma área inteira, com seus dois anos. Isso não é teste de causalidade nem de significância.

| Variável | Spearman ρ | Estável ao retirar uma área |
|---|---:|:---:|
| Número de empenhos | 0,955 | Sim |
| Número de credores | 0,933 | Sim |
| Dotação inicial | 0,930 | Sim |
| Número de ações | 0,921 | Sim |
| Número de liquidações | 0,916 | Sim |
| Número de fontes orçamentárias | 0,902 | Sim |
| Diversidade de recursos dos empenhos | 0,897 | Sim |
| Número de suplementações | 0,895 | Sim |
| Número de dotações | 0,895 | Sim |
| Número de subfunções | 0,877 | Sim |
| Número de unidades | 0,824 | Sim |
| Concentração do orçamento entre ações | -0,804 | Sim |
| Número de programas | 0,779 | Sim |
| Diversidade de naturezas | 0,594 | Sim |
| Proporção de empenhos ordinários | -0,444 | Sim |
| Proporção inicial de pessoal | 0,314 | Não |

A proporção inicial de pessoal atinge o limite no painel completo, mas não em todas as remoções de área. As outras 15 relações são estáveis nesse diagnóstico. A lista inclui todas as 16; nenhuma foi escondida para ajustar o resultado à meta.

![As 25 correlações e os limites solicitados](correlacoes.png)

## Boxplot e outliers

Aplicamos Tukey à variável principal **separadamente em cada ano**, comparando as 14 áreas. Q1 e Q3 usam o cálculo padrão de quantis do pandas, com interpolação linear. Um valor é marcado quando fica abaixo de Q1 − 1,5 × IQR ou acima de Q3 + 1,5 × IQR. Foram identificadas **2 observações área × ano**:

| Ano | Área | Participação | Tipo |
|---:|---|---:|---|
| 2024 | Educação | 32,75% | superior |
| 2025 | Educação | 32,09% | superior |

![Boxplot da participação liquidada em cada ano](boxplot.png)

Os quartis e limites exatos estão em `limites_outliers.csv`, e os registros em `outliers.csv`. As participações são armazenadas entre 0 e 1 nos CSVs e mostradas em porcentagem nos gráficos. Os bigodes terminam nas observações extremas ainda dentro dos limites, não necessariamente sobre as cercas teóricas de Tukey.

**Nenhuma observação foi retirada.** Valores altos podem refletir a escala de políticas como Educação e Saúde. Não são, por si, erro, desperdício ou irregularidade. A classificação compara áreas diferentes; não estabelece quanto cada uma deveria receber. Este diagnóstico trata de áreas e anos, não de contratos ou empenhos individuais. No mesmo ano, valor liquidado e participação diferem por um denominador comum, portanto produziriam os mesmos pontos de Tukey, não duas evidências independentes.

## Normalidade

![Histograma e Q-Q da variável principal](normalidade.png)

Para a variável principal, Shapiro–Wilk resultou em W = 0.692839 e p = 2.26072e-06. Com alfa de 5%: **rejeita normalidade**. O teste das 26 variáveis está em `shapiro_wilk.csv`; a inspeção visual está em `normalidade.png`.

O teste é um diagnóstico exploratório. Contagens são discretas, participações são limitadas e a mesma área aparece em dois anos. As observações não são completamente independentes. Não rejeitar H0 não prova normalidade, e rejeitá-la não torna Pearson automaticamente inválido. Spearman foi priorizado para descrever associações monotônicas entre áreas de escalas diferentes; não apenas por um resultado de Shapiro–Wilk.

## Uso no planejamento

![Distribuição dos valores entre as áreas](distribuicao.png)

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
