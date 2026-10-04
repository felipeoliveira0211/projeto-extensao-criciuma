# Conclusão do estudo

A análise mostrou mudanças importantes na distribuição dos recursos de Criciúma entre 2024 e 2025. Nas bases estudadas, Assistência Social passou de R$ 12,37 milhões para R$ 48,53 milhões, um aumento nominal de 292,25%, enquanto Urbanismo apresentou redução de 6,22%. Educação e Saúde cresceram em valores, mas perderam participação no total das 14 áreas comparáveis. Isso mostra por que é importante observar tanto os valores quanto os percentuais.

A importância desse acompanhamento encontra apoio em pesquisas. O Ipea identificou riscos de perda de financiamento na disputa entre saúde e educação [1], enquanto o estudo de Barreto e colaboradores mostrou que melhorias no saneamento podem beneficiar a saúde infantil [2]. Essas evidências reforçam a necessidade de planejar as áreas em conjunto, considerando suas necessidades e os efeitos que produzem umas sobre as outras.

Para Criciúma, os resultados apontam prioridades concretas de investigação: verificar quais programas explicam o crescimento da Assistência Social, quais obras ou serviços estão associados à redução em Urbanismo e se essas mudanças acompanharam a demanda da população. O acompanhamento futuro pode comparar despesas com famílias atendidas, obras concluídas, matrículas e filas de atendimento.

Assim, a contribuição do estudo é identificar mudanças que precisam de explicação e orientar o acompanhamento dos serviços. As 16 correlações encontradas ajudam a descrever a distribuição, mas não comprovam eficiência. Com dois anos de dados e sem indicadores de resultados dos serviços, ainda não é possível afirmar que houve excesso de recursos em uma área ou abandono de outra.

## Comparativos que apoiam a conclusão

| Área | Liquidado em 2024 | Liquidado em 2025 | Variação nominal |
|---|---:|---:|---:|
| Educação | R$ 361,50 milhões | R$ 383,41 milhões | +6,06% |
| Saúde | R$ 279,42 milhões | R$ 293,55 milhões | +5,06% |
| Administração | R$ 217,26 milhões | R$ 228,48 milhões | +5,17% |
| Urbanismo | R$ 163,63 milhões | R$ 153,45 milhões | −6,22% |
| Assistência Social | R$ 12,37 milhões | R$ 48,53 milhões | +292,25% |

Fonte: `base_analitica.csv`, nas bases recebidas para 2024 e 2025. Variação = (valor de 2025 / valor de 2024 − 1) × 100, calculada antes do arredondamento. Valores nominais, sem correção pela inflação; não representam uma conciliação com o balanço oficial.

Educação recebeu mais em reais, mas sua participação no total das 14 áreas comparáveis caiu de **32,75% para 32,09%**. Portanto, perder participação não significa necessariamente sofrer um corte. Assistência Social teve aumento de aproximadamente **R$ 36,16 milhões**, enquanto Urbanismo apresentou redução de **R$ 10,18 milhões**. Os dados não demonstram que o dinheiro de uma área foi transferido para a outra.

## Estudos que fundamentam o objetivo

**[1] Disputa por recursos entre áreas.** Vieira e colaboradores (Ipea, 2020) analisaram 5.480 municípios e identificaram, em um cenário de unificação dos pisos de saúde e educação, 951 municípios com maior risco de redução dos recursos da educação e 97 com maior risco na saúde. O estudo sustenta a preocupação com a concorrência por recursos. São riscos naquele cenário, não cortes observados nem um diagnóstico de Criciúma. Os percentuais de aplicação utilizados no estudo têm bases de cálculo diferentes da participação liquidada deste projeto.

Referência: VIEIRA, Fabiola Sulpino; SERVO, Luciana Mendes Santos; BENEVIDES, Rodrigo Pucci de Sá e; PIOLA, Sérgio Francisco; ORAIR, Rodrigo Octávio. *Gastos em saúde e educação no Brasil: impactos da unificação dos pisos constitucionais*. Ipea, Texto para Discussão 2596, 2020. [Acesso ao estudo](https://repositorio.ipea.gov.br/entities/publication/a587d79e-bb94-4a84-a958-4b68d381d62e).

**[2] Benefícios entre áreas.** Barreto e colaboradores (2007) avaliaram um programa de saneamento em Salvador, acompanhando 841 crianças antes e 1.007 depois da intervenção. Após ajustes estatísticos, estimaram redução de 22% na prevalência de diarreia infantil. O resultado apoia o planejamento conjunto de saneamento e saúde. Esse percentual não pode ser aplicado diretamente a Criciúma, e a pesquisa não demonstra que a distribuição local esteja inadequada.

Referência: BARRETO, Mauricio L. et al. *Effect of city-wide sanitation programme on reduction in rate of childhood diarrhoea in northeast Brazil: assessment by two cohort studies*. The Lancet, v. 370, p. 1622–1628, 2007. [Acesso à pesquisa](https://pubmed.ncbi.nlm.nih.gov/17993362/).

**[3] Planejamento apoiado em resultados.** O relatório da OCDE de 2025, com levantamento de 2023, informa que 28 dos 33 países respondentes (85%) utilizavam alguma forma de orçamento orientado por desempenho. Desses 28, 20 usavam informações de desempenho para orientar a distribuição anual dos recursos. O levantamento trata de governos centrais e mostra adoção da prática, não um percentual de melhoria da eficiência. Ele apoia a proposta de combinar despesas com indicadores dos serviços.

Referência: OECD. *Government at a Glance 2025*, seção 9.2, Performance budgeting. 2025. [Acesso ao relatório](https://www.oecd.org/en/publications/2025/06/government-at-a-glance-2025_70e14c6c/full-report/performance-budgeting_eb0a21ea.html).

As referências fundamentam a importância do acompanhamento, mas não definem uma divisão ideal do orçamento de Criciúma. Uma área receber mais recursos pode ser justificável por sua demanda, pelos custos dos serviços e pelas obrigações de financiamento.

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
