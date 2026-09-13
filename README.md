# Distribuição das despesas de Criciúma — 2024 e 2025

**Pergunta-problema:** Como os recursos da Prefeitura de Criciúma foram distribuídos entre as áreas em 2024 e 2025, e como a análise estatística pode ajudar a planejar melhor essa distribuição?

## Organização das pastas

```text
extensao_planejamento_criciuma/
├── dados/
│   ├── originais/          seis CSVs principais baixados, sem alterações
│   └── tratados/           base unificada criada pelo programa
├── codigo/
│   ├── preparar_dados.py   leitura, conversão de valores e união das bases
│   ├── estatistica.py      quartis, outliers, resumos e correlações
│   └── gerar_graficos.py  imagens dos resultados
├── graficos/              cinco imagens prontas para apresentação
├── resultados/            tabelas, auditoria e resumo dos achados
├── executar.py            executa as três etapas na ordem correta
└── requirements.txt       bibliotecas necessárias
```

Os seis CSVs em `dados/originais` são os **arquivos principais** das duas bases para 2024, 2025 e 2026. Os pacotes baixados também contêm milhares de arquivos auxiliares vinculados aos registros; eles não são usados nesta etapa. A análise principal usa **2024 e 2025**, pois são exercícios completos. Os dois CSVs de 2026 ficam guardados para análise posterior.

## Como executar

No terminal, dentro desta pasta:

```powershell
python -m pip install -r requirements.txt
python executar.py
```

Ao executar, o programa refaz a base tratada, as tabelas de resultados e os gráficos. Os CSVs originais não são modificados.

## Como explicar o código

1. `preparar_dados.py` abre quatro CSVs, transforma valores monetários em números e liga as tabelas pela entidade, pelo ano e pela ação. Antes da ligação, resume a tabela de ações para não multiplicar as linhas da execução.
2. `estatistica.py` encontra Q1, mediana e Q3; considera atípicos altos os valores acima de Q3 + 1,5 × (Q3 − Q1); resume os dados por função e mês; e calcula Pearson e Spearman para 25 variáveis iniciais e dez adicionais.
3. `gerar_graficos.py` desenha boxplot, evolução mensal, valores por função, outliers por função e correlações selecionadas.
4. `executar.py` chama as etapas e salva os arquivos finais.

O fluxo é: **CSV original → base tratada → cálculos → tabelas e gráficos**.

## Cuidados na interpretação

A unidade de análise é a linha do arquivo de execução. Existem 116 pares com o mesmo número e valor de empenho, mas diferenças em outros campos. Por isso, os totais monetários por linha devem ser tratados como provisórios até a reconciliação. Os valores orçados por ação se repetem após a união e não são somados nos gráficos. Correlação não prova causa, necessidade da despesa ou eficiência. O resumo em `resultados/resumo.md` apresenta os achados e o limite atual da exigência de 15 correlações acima de 0,3.

A interpretação final e as medidas possíveis para o planejamento estão em `resultados/conclusao.md`.

Fonte: [Portal de Dados Abertos de Criciúma](https://transparencia.betha.cloud/#/n4W91vnHptoBkiHKAxioOA==/dados-abertos?esconderCabecalho=S&esconderMenu=S&esconderRodape=S).
