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

    # 4B. BOXPLOT E OUTLIERS: comparar as áreas dentro de cada ano.
    # IQR = Q3 - Q1. Usamos a regra de Tukey, sem remover pontos da base.
    limites, marcados = [], []
    for ano, grupo in base.groupby("ano"):
        q1, q3 = grupo[ALVO].quantile([0.25, 0.75])
        iqr = q3 - q1
        inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        fora = (grupo[ALVO] < inferior) | (grupo[ALVO] > superior)
        limites.append({"ano": ano, "n": len(grupo), "q1": q1, "q3": q3,
                        "iqr": iqr, "limite_inferior": inferior,
                        "limite_superior": superior, "n_outliers": int(fora.sum())})
        pontos = grupo.loc[fora, ["ano", "area", ALVO, "liquidado_area"]].copy()
        pontos["tipo"] = pontos[ALVO].map(lambda x: "inferior" if x < inferior else "superior")
        marcados.append(pontos)
    limites = pd.DataFrame(limites)
    outliers = pd.concat(marcados, ignore_index=True)
    salvar(limites, saida, "limites_outliers.csv")
    salvar(outliers, saida, "outliers.csv")

    # 5. SHAPIRO e Normalização da variável alvo caso no SW teste tenha valor inferior à 0.05
    participacao_nova = base[ALVO].copy()

    if(stats.shapiro(base[ALVO]).pvalue < 0.05):
        q1, q3 = base[ALVO].quantile([0.25, 0.75])
        iqr = q3 - q1
        inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        base.loc[base[ALVO] < inferior] = inferior # Substituido outliers inferiores pelo valor do limite inferior
        base.loc[base[ALVO] > superior] = superior # Substituido outliers superiores pelo valor do limite superior
        participacao_nova, lambda_boxcox = stats.boxcox(base[ALVO]) # Utilização de boxcox para diminuir o peso dos outliers superiores os aproximando da média
        

    # 6. CORRELAÇÃO: Spearman descreve associação monotônica; Pearson é comparação.
    # Mantemos as 25 variáveis, inclusive as que não ultrapassam 0,3.
    resultados = []
    for coluna in variaveis:
        pares = pd.DataFrame({ coluna: base[coluna], ALVO: participacao_nova }).dropna()
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
    destaque = correlacoes.loc[correlacoes.supera_03_spearman].merge(
        dicionario[["variavel", "descricao"]], on="variavel", validate="one_to_one")
    destaque["estavel_sem_uma_area"] = ((destaque.rho_min_sem_area > 0.3)
                                      | (destaque.rho_max_sem_area < -0.3))
    destaque = destaque.sort_values("spearman", key=lambda x: x.abs(), ascending=False)
    salvar(destaque[["variavel", "descricao", "n", "spearman", "pearson",
                    "estavel_sem_uma_area"]], saida, "correlacoes_destaque.csv")

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

    # Boxplot: caixa = Q1 a Q3; linha = mediana; círculos = pontos além dos limites.
    anos = sorted(base.ano.unique())
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot([base.loc[base.ano == ano, ALVO] * 100 for ano in anos], widths=0.4)
    ax.set_xticks(range(1, len(anos) + 1), [str(ano) for ano in anos])
    for ponto in outliers.itertuples():
        x = anos.index(ponto.ano) + 1
        ax.annotate(ponto.area, (x, getattr(ponto, ALVO) * 100),
                    xytext=(14, 0), textcoords="offset points", va="center", fontsize=9)
    ax.set(title="Boxplot da participação liquidada por ano",
           xlabel="Ano · 14 áreas comparáveis em cada ano",
           ylabel="Participação na despesa liquidada (%)")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(saida / "boxplot.png", dpi=160)
    plt.close(fig)

    # Todas as 25 variáveis no gráfico, para não esconder as correlações pequenas.
    grafico = correlacoes.merge(dicionario[["variavel", "descricao"]], on="variavel")
    grafico = grafico.sort_values("spearman")
    cores = ["#b55b19" if r < -0.3 else "#17658a" if r > 0.3 else "#9aa4ae"
             for r in grafico.spearman]
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.barh(grafico.descricao, grafico.spearman, color=cores)
    ax.axvline(-0.3, color="#555555", linestyle="--", linewidth=1)
    ax.axvline(0.3, color="#555555", linestyle="--", linewidth=1)
    ax.axvline(0, color="#aaaaaa", linewidth=0.6)
    for i, r in enumerate(grafico.spearman):
        ax.text(r + (0.02 if r >= 0 else -0.02), i, f"{r:.3f}", va="center",
                ha="left" if r >= 0 else "right", fontsize=8)
    ax.set(xlim=(-1.1, 1.1), title="25 variáveis e sua associação com a participação liquidada",
           xlabel="Spearman ρ · tracejados: −0,3 e +0,3 · cinza: não atinge o limite")
    fig.tight_layout()
    fig.savefig(saida / "correlacoes.png", dpi=160)
    plt.close(fig)

    # 8. CONCLUSÃO: responder à pergunta sem confundir correlação com causa.
    n_spearman = int(correlacoes.supera_03_spearman.sum())
    n_pearson = int((correlacoes.pearson.abs() > 0.3).sum())
    tabela_destaque = ["| Variável | Spearman ρ | Estável ao retirar uma área |",
                       "|---|---:|:---:|"]
    for item in destaque.itertuples():
        coeficiente = f"{item.spearman:.3f}".replace(".", ",")
        tabela_destaque.append(f"| {item.descricao} | {coeficiente} | {'Sim' if item.estavel_sem_uma_area else 'Não'} |")
    tabela_outliers = ["| Ano | Área | Participação | Tipo |", "|---:|---|---:|---|"]
    for item in outliers.itertuples():
        percentual = f"{getattr(item, ALVO) * 100:.2f}%".replace(".", ",")
        tabela_outliers.append(f"| {item.ano} | {item.area} | {percentual} | {item.tipo} |")
    
    print(f"Base: {len(base)} linhas, {base.area.nunique()} áreas, 25 variáveis.")
    print(f"Shapiro–Wilk: {stats.shapiro(base[ALVO]).pvalue}")
    print(f"Além de ±0,3: {n_spearman} em Spearman; {n_pearson} em Pearson.")
    print(f"Resultados: {saida}")


