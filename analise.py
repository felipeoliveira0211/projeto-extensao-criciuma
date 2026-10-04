"""Roteiro estatístico: juntar → descrever → testar normalidade → correlacionar."""
from pathlib import Path
import sqlite3
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ALVO = "participacao_liquidada"
ALFA = 0.05


def salvar(tabela, pasta, nome):
    tabela.to_csv(pasta / nome, index=False, encoding="utf-8-sig")


def analisar(projeto):
    projeto = Path(projeto)
    saida = projeto / "resultados"
    saida.mkdir(exist_ok=True)
    dicionario = pd.read_csv(projeto / "variaveis.csv")
    variaveis = dicionario.variavel.tolist()

    # 1. PERGUNTA E VARIÁVEIS: veja README.md e variaveis.csv.
    # Y é a participação liquidada. As 25 X são candidatas explicativas, não outros alvos.

    # 2. CARREGAR E RELACIONAR AS BASES, sem multiplicar valores pelas liquidações.
    with sqlite3.connect(projeto / "dados" / "banco.sqlite") as banco:
        dotacoes = pd.read_sql_query("SELECT d.*, a.nome AS area FROM dotacoes d JOIN areas a ON d.area_id=a.id", banco)
        empenhos = pd.read_sql_query("SELECT e.*, a.nome AS area FROM empenhos e JOIN areas a ON e.area_id=a.id", banco)
        liquidacoes = pd.read_sql_query("SELECT l.*, e.ano, e.area_id, e.data AS data_empenho FROM liquidacoes l JOIN empenhos e ON l.empenho_id=e.id", banco)
        fontes = pd.read_sql_query("SELECT f.*, d.ano, d.area_id FROM fontes_dotacao f JOIN dotacoes d ON f.dotacao_id=d.id", banco)
        assert not banco.execute("PRAGMA foreign_key_check").fetchall()
    banco.close()
    empenhos["data"] = pd.to_datetime(empenhos.data, errors="coerce")
    liquidacoes["data"] = pd.to_datetime(liquidacoes.data, errors="coerce")
    liquidacoes["data_empenho"] = pd.to_datetime(liquidacoes.data_empenho, errors="coerce")
    liquidacoes["prazo"] = (liquidacoes.data - liquidacoes.data_empenho).dt.days

    # 3. UMA LINHA POR ÁREA E ANO. Somar os valores apenas na tabela de dotações.
    linhas = []
    for (ano, area_id), d in dotacoes.groupby(["ano", "area_id"]):
        e = empenhos[(empenhos.ano == ano) & (empenhos.area_id == area_id)]
        l = liquidacoes[(liquidacoes.ano == ano) & (liquidacoes.area_id == area_id)
                       & (liquidacoes.data.dt.year == ano)]
        f = fontes[(fontes.ano == ano) & (fontes.area_id == area_id)]
        total_inicial = d.inicial.sum()
        peso_acoes = d.groupby(["entidade_id", "acao"]).inicial.sum() / total_inicial
        def proporcao_orcamento(condicao):
            return d.loc[condicao, "inicial"].sum() / total_inicial if total_inicial else float("nan")
        def proporcao_empenhos(condicao):
            return condicao.mean() if len(e) else float("nan")
        linha = {"ano": ano, "area": d.area.iloc[0]}
        # min_count impede que um valor conflitante seja silenciosamente tratado como zero.
        linha["liquidado_area"] = d.liquidado.sum(min_count=len(d))
        linha["liquidado_min"] = d.liquidado_min.sum()
        linha["liquidado_max"] = d.liquidado_max.sum()
        linha["dotacao_inicial"] = total_inicial
        linha["n_dotacoes"] = len(d)
        linha["n_programas"] = len(d[["entidade_id", "programa"]].drop_duplicates())
        linha["n_acoes"] = len(d[["entidade_id", "acao"]].drop_duplicates())
        linha["n_unidades"] = len(d[["entidade_id", "unidade"]].drop_duplicates())
        linha["n_subfuncoes"] = d.subfuncao.nunique()
        linha["n_entidades"] = d.entidade_id.nunique()
        linha["n_naturezas"] = d.natureza.nunique()
        linha["hhi_orcamento_acoes"] = (peso_acoes ** 2).sum() if total_inicial else float("nan")
        linha["perc_orcamento_pessoal"] = proporcao_orcamento(d.natureza.str.startswith("31"))
        linha["perc_orcamento_capital"] = proporcao_orcamento(d.natureza.str.startswith("4"))
        linha["perc_orcamento_transferencias"] = proporcao_orcamento(d.natureza.str[2:4].isin(["20", "30", "40", "50", "60", "70", "71", "72"]))
        linha["n_fontes_orcamentarias"] = f.recurso_id.nunique()
        linha["n_suplementacoes"] = d.n_suplementacoes.sum(min_count=len(d))
        atualizado = d.atualizado.sum(min_count=len(d))
        linha["taxa_alteracao_orcamento"] = (atualizado - total_inicial) / total_inicial if total_inicial else float("nan")
        linha["n_empenhos"] = len(e)
        linha["n_credores"] = e.credor_id.nunique()
        linha["n_recursos_empenhos"] = e.recurso_id.nunique()
        linha["n_liquidacoes"] = len(l)
        linha["mediana_valor_empenho"] = e.inicial.median()
        linha["perc_empenhos_folha"] = proporcao_empenhos(e.categoria == "FOLHA")
        linha["perc_empenhos_processo"] = proporcao_empenhos(e.categoria == "PROCESSO")
        linha["perc_empenhos_ordinarios"] = proporcao_empenhos(e.tipo.str.lower().isin(["ordinário", "ordinario"]))
        linha["prazo_liquidacao_mediano"] = l.loc[l.prazo >= 0, "prazo"].median()
        linha["perc_empenhos_ultimo_trimestre"] = proporcao_empenhos(e.data.dt.month >= 10)
        linhas.append(linha)
    todas = pd.DataFrame(linhas)
    salvar(todas[["ano", "area", "dotacao_inicial", "liquidado_area", "liquidado_min", "liquidado_max"]], saida, "distribuicao_areas.csv")

    # Mesmas áreas nos dois anos e resposta sem conflito: filtro por qualidade, não por r.
    cobertura = todas.groupby("area").agg(anos=("ano", "nunique"), validos=("liquidado_area", "count"))
    areas_validas = cobertura.index[(cobertura.anos == 2) & (cobertura.validos == 2)]
    base = todas[todas.area.isin(areas_validas)].copy()
    base[ALVO] = base.liquidado_area / base.groupby("ano").liquidado_area.transform("sum")
    base = base[["ano", "area", "liquidado_area", ALVO] + variaveis]
    assert len(variaveis) == 25 and not base.duplicated(["ano", "area"]).any()
    assert (base.groupby("ano")[ALVO].sum() - 1).abs().max() < 1e-10
    salvar(base, saida, "base_analitica.csv")

    # 4. ESTATÍSTICA DESCRITIVA: avaliar tamanho, dispersão e assimetria antes do teste.
    descritiva = base[[ALVO] + variaveis].describe().T
    descritiva["assimetria"] = base[[ALVO] + variaveis].skew()
    salvar(descritiva.reset_index(names="variavel"), saida, "descritiva.csv")

    # 5. SHAPIRO–WILK: H0 = distribuição normal; alfa = 0,05.
    normalidade = []
    for coluna in [ALVO] + variaveis:
        valores = base[coluna].dropna()
        if len(valores) < 3 or valores.nunique() < 2:
            w, p, leitura = float("nan"), float("nan"), "Não aplicável: constante ou poucos dados"
        else:
            w, p = stats.shapiro(valores)
            leitura = "Rejeita normalidade" if p < ALFA else "Não rejeita normalidade"
        normalidade.append({"variavel": coluna, "n": len(valores), "W": w, "p_valor": p,
                            "leitura_5pct": leitura, "contagem_discreta": coluna.startswith("n_")})
    normalidade = pd.DataFrame(normalidade)
    salvar(normalidade, saida, "shapiro_wilk.csv")

    # 6. CORRELAÇÃO: Spearman descreve associação monotônica; Pearson é comparação.
    # O SW auxilia o diagnóstico, mas sozinho não escolhe nem proíbe um coeficiente.
    # Mantemos as 25 variáveis, inclusive as que não ultrapassam 0,3.
    resultados = []
    for coluna in variaveis:
        pares = base[[coluna, ALVO]].dropna()
        rho = pares[coluna].corr(pares[ALVO], method="spearman")
        r = pares[coluna].corr(pares[ALVO], method="pearson")
        linha = {"variavel": coluna, "n": len(pares), "spearman": rho,
                 "pearson": r, "supera_03_spearman": abs(rho) > 0.3}
        for ano in (2024, 2025):
            recorte = base[base.ano == ano]
            linha[f"spearman_{ano}"] = recorte[coluna].corr(recorte[ALVO], method="spearman")
        # Sensibilidade simples: retirar uma área com seus dois anos.
        sem_uma_area = []
        for area in base.area.unique():
            recorte = base[base.area != area]
            sem_uma_area.append(recorte[coluna].corr(recorte[ALVO], method="spearman"))
        linha["rho_min_sem_area"] = min(sem_uma_area)
        linha["rho_max_sem_area"] = max(sem_uma_area)
        resultados.append(linha)
    correlacoes = pd.DataFrame(resultados)
    salvar(correlacoes, saida, "correlacoes.csv")

    # 7. VISUALIZAR: histograma e Q-Q da resposta; comparação das mesmas áreas.
    plt.rcParams.update({"font.size": 10})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].hist(base[ALVO] * 100, bins=8, color="#2874a6", edgecolor="white")
    ax[0].set(title="Distribuição da variável principal", xlabel="Participação na despesa liquidada (%)", ylabel="Observações área × ano")
    stats.probplot(base[ALVO] * 100, dist="norm", plot=ax[1])
    ax[1].set(title="Q-Q: comparação com a normal", xlabel="Quantis teóricos da normal", ylabel="Participação observada (%)")
    fig.tight_layout()
    fig.savefig(saida / "normalidade.png", dpi=160)
    plt.close(fig)
    comparacao = base.pivot(index="area", columns="ano", values="liquidado_area") / 1_000_000
    comparacao = comparacao.sort_values(2025)
    fig, ax = plt.subplots(figsize=(10, 7))
    comparacao.plot.barh(ax=ax, color=["#a2b9ce", "#17658a"], width=0.8)
    ax.set(title="Distribuição entre as 14 áreas comparáveis", xlabel="Despesa liquidada (R$ milhões nominais)", ylabel="")
    ax.legend(title="Ano", loc="lower right")
    fig.tight_layout()
    fig.savefig(saida / "distribuicao.png", dpi=160)
    plt.close(fig)

    # 8. CONCLUSÃO: responder à pergunta sem confundir correlação com causa.
    n_spearman = int(correlacoes.supera_03_spearman.sum())
    n_pearson = int((correlacoes.pearson.abs() > 0.3).sum())
    sw = normalidade.iloc[0]
    resumo = f"""# Conclusão do estudo

Pergunta: como os recursos da Prefeitura de Criciúma foram distribuídos entre as áreas em 2024 e 2025, e como a análise estatística pode ajudar a planejar melhor essa distribuição?

## Resultado

Educação, Saúde, Administração e Urbanismo apresentam os maiores valores nas bases recebidas. O gráfico `distribuicao.png` compara as mesmas áreas nos dois anos. A tabela `distribuicao_areas.csv` inclui também Cultura e Habitação, preservando as limitações de seus registros.

A base de correlações tem {base.area.nunique()} áreas em dois anos, totalizando {len(base)} observações. A variável principal é a participação de cada área na despesa liquidada das áreas comparáveis no mesmo ano. Das 25 variáveis candidatas, **{n_spearman} superam 0,3 em módulo em Spearman**. Em Pearson, são {n_pearson}. Não foram excluídas variáveis para elevar essa contagem.

## Normalidade

Para a variável principal, Shapiro–Wilk resultou em W = {sw.W:.6f} e p = {sw.p_valor:.6g}. Com alfa de 5%: **{sw.leitura_5pct.lower()}**. O teste das 26 variáveis está em `shapiro_wilk.csv`; a inspeção visual está em `normalidade.png`.

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
"""
    (saida / "CONCLUSAO.md").write_text(resumo, encoding="utf-8")
    print(f"Base: {len(base)} linhas, {base.area.nunique()} áreas, 25 variáveis.")
    print(f"Shapiro–Wilk de Y: W={sw.W:.6f}, p={sw.p_valor:.6g}.")
    print(f"Além de ±0,3: {n_spearman} em Spearman; {n_pearson} em Pearson.")
    print(f"Resultados: {saida}")


