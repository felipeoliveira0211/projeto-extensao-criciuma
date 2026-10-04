"""Preparação opcional: lê as quatro bases originais e cria um banco pequeno.

Não é preciso executar esta etapa para estudar a estatística: o banco já acompanha
esta pasta. Para reconstruí-lo, execute main.py --reconstruir "pasta dos originais".
"""
from pathlib import Path
import csv
import hashlib
import re
import sqlite3
import pandas as pd


def ler_csv(caminho):
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        return [{k: v.strip() for k, v in linha.items()} for linha in csv.DictReader(arquivo)]


def ler_anexo(pasta, nome):
    # Campo vazio significa ausência de referência; arquivo referido e ausente é erro.
    return ler_csv(pasta / nome) if nome else []


def numero(texto):
    return float(texto) if texto else None


def cadastrar(catalogo, chave):
    if chave not in catalogo:
        catalogo[chave] = len(catalogo) + 1
    return catalogo[chave]


def conciliar(dados, chaves, nome, problemas):
    """Uma linha por chave. Concordâncias são preservadas; conflitos ficam ausentes."""
    grupos = dados.groupby(chaves, sort=False, dropna=False)
    diferentes = grupos.nunique(dropna=True)
    for chave, linha in diferentes.iterrows():
        for campo in linha.index[linha > 1]:
            problemas.append({"tabela": nome, "chave": str(chave), "campo": campo})
    def unico(coluna):
        valores = coluna.dropna().unique()
        return valores[0] if len(valores) == 1 else None
    return grupos.agg(unico).reset_index()


def preparar(origem, destino):
    origem = Path(origem).resolve()
    destino = Path(destino)
    destino.mkdir(exist_ok=True)
    areas, entidades, recursos, credores = {}, {}, {}, {}
    ids_dotacoes, ids_empenhos = {}, {}
    dotacoes, empenhos, liquidacoes, fontes_dotacao, fontes = [], [], [], [], []

    for ano in (2024, 2025):
        pasta = origem / f"Despesas por Programas e Ações-{ano}"
        arquivo = next(pasta.glob("27_despesas*.csv"))
        linhas = ler_csv(arquivo)
        fontes.append({"arquivo": str(arquivo.relative_to(origem)), "linhas": len(linhas),
                       "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest()})
        for linha in linhas:
            entidade = cadastrar(entidades, linha["nomeEntidade"])
            area = cadastrar(areas, linha["descricaoFuncao"])
            chave = (entidade, ano, linha["idDespesa"])
            dotacao = cadastrar(ids_dotacoes, chave)
            dotacoes.append({
                "id": dotacao, "entidade_id": entidade, "area_id": area, "ano": ano,
                "numero": linha["idDespesa"], "subfuncao": linha["descricaoSubfuncao"],
                "unidade": linha["descricaoOrgao"] + "|" + linha["descricaoUnidade"],
                "programa": linha["descricaoPrograma"], "acao": linha["idAcao"],
                "natureza": linha["numeroElemento"], "inicial": numero(linha["valorOrcado"]),
                "atualizado": numero(linha["valorOrcadoAtualizado"]),
                "liquidado": numero(linha["valorLiquidadoAtualizado"]),
                "n_suplementacoes": len(ler_anexo(pasta, linha["suplementacoes"]))})
            for item in ler_anexo(pasta, linha["fontesRecursos"]):
                chave_recurso = (item["descricaoRecurso"], item["tipoRecurso"], item["finalidade"])
                recurso = cadastrar(recursos, chave_recurso)
                fontes_dotacao.append({"dotacao_id": dotacao, "recurso_id": recurso})

        pasta = origem / f"Execução Detalhada de Despesas-{ano}"
        arquivo = next(pasta.glob("27_execucao*.csv"))
        linhas = ler_csv(arquivo)
        fontes.append({"arquivo": str(arquivo.relative_to(origem)), "linhas": len(linhas),
                       "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest()})
        for linha in linhas:
            entidade = cadastrar(entidades, linha["nomeEntidade"])
            area = cadastrar(areas, linha["descricaoFuncao"])
            empenho = cadastrar(ids_empenhos, (entidade, ano, linha["numeroEmpenho"]))
            anexos = ler_anexo(pasta, linha["dotacaoOrcamentaria"])
            candidatos = {ids_dotacoes.get((entidade, ano, a["numeroDespesa"])) for a in anexos}
            candidatos.discard(None)
            dotacao = next(iter(candidatos)) if len(candidatos) == 1 else None
            pessoas = ler_anexo(pasta, linha["credor"])
            credor = None
            if len(pessoas) == 1:
                documento = pessoas[0]["cnpjCpfCredor"]
                digitos = re.sub(r"\D", "", documento)
                completo = "*" not in documento and len(digitos) in (11, 14)
                chave_credor = digitos if completo else documento + "|" + pessoas[0]["nomeCredor"]
                # Identificador estável para contar credores, sem copiar nomes ou documentos.
                credor = cadastrar(credores, hashlib.sha256(chave_credor.encode()).hexdigest())
            recurso = cadastrar(recursos, (linha["descricaoRecurso"], linha["tipoRecurso"], linha["finalidade"]))
            empenhos.append({
                "id": empenho, "entidade_id": entidade, "area_id": area, "ano": ano,
                "numero": linha["numeroEmpenho"], "dotacao_id": dotacao,
                "data": linha["dataEmpenho"], "categoria": linha["categoriaEmpenho"],
                "tipo": linha["tipoEmpenho"], "inicial": numero(linha["valorEmpenho"]),
                "credor_id": credor, "recurso_id": recurso})
            for item in ler_anexo(pasta, linha["liquidacoes"]):
                liquidacoes.append({"empenho_id": empenho, "numero": item["idLiquidacao"],
                                    "data": item["data"]})
        print(f"Bases e anexos de {ano} lidos.", flush=True)

    problemas = []
    bruto = pd.DataFrame(dotacoes)
    faixas = bruto.groupby("id").liquidado.agg(liquidado_min="min", liquidado_max="max")
    dotacoes = conciliar(bruto, ["id"], "dotacoes", problemas).join(faixas, on="id")
    empenhos = conciliar(pd.DataFrame(empenhos), ["id"], "empenhos", problemas)
    liquidacoes = conciliar(pd.DataFrame(liquidacoes), ["empenho_id", "numero"], "liquidacoes", problemas)
    liquidacoes.insert(0, "id", range(1, len(liquidacoes) + 1))
    fontes_dotacao = pd.DataFrame(fontes_dotacao).drop_duplicates()
    problemas.extend({"tabela": "empenhos", "chave": str(i), "campo": "dotacao_sem_vinculo"}
                     for i in empenhos.loc[empenhos.dotacao_id.isna(), "id"])

    # SQLite pertence à biblioteca padrão do Python. As chaves verificam as relações.
    temporario = destino / "banco.tmp.sqlite"
    if temporario.exists():
        temporario.unlink()  # Apenas o temporário deste script, na pasta de saída definida.
    with sqlite3.connect(temporario) as banco:
        banco.execute("PRAGMA foreign_keys=ON")
        banco.executescript('''
        CREATE TABLE areas(id INTEGER PRIMARY KEY, nome TEXT UNIQUE NOT NULL);
        CREATE TABLE entidades(id INTEGER PRIMARY KEY, nome TEXT UNIQUE NOT NULL);
        CREATE TABLE recursos(id INTEGER PRIMARY KEY, descricao TEXT, tipo TEXT, finalidade TEXT);
        CREATE TABLE credores(id INTEGER PRIMARY KEY, chave TEXT UNIQUE NOT NULL);
        CREATE TABLE dotacoes(id INTEGER PRIMARY KEY, entidade_id INTEGER REFERENCES entidades(id),
          area_id INTEGER REFERENCES areas(id), ano INTEGER, numero TEXT, subfuncao TEXT,
          unidade TEXT, programa TEXT, acao TEXT, natureza TEXT, inicial REAL, atualizado REAL,
          liquidado REAL, n_suplementacoes INTEGER, liquidado_min REAL, liquidado_max REAL,
          UNIQUE(entidade_id,ano,numero));
        CREATE TABLE empenhos(id INTEGER PRIMARY KEY, entidade_id INTEGER REFERENCES entidades(id),
          area_id INTEGER REFERENCES areas(id), ano INTEGER, numero TEXT,
          dotacao_id INTEGER REFERENCES dotacoes(id), data TEXT, categoria TEXT, tipo TEXT,
          inicial REAL, credor_id INTEGER REFERENCES credores(id), recurso_id INTEGER REFERENCES recursos(id),
          UNIQUE(entidade_id,ano,numero));
        CREATE TABLE liquidacoes(id INTEGER PRIMARY KEY, empenho_id INTEGER REFERENCES empenhos(id),
          numero TEXT, data TEXT, UNIQUE(empenho_id,numero));
        CREATE TABLE fontes_dotacao(dotacao_id INTEGER REFERENCES dotacoes(id),
          recurso_id INTEGER REFERENCES recursos(id), PRIMARY KEY(dotacao_id,recurso_id));
        ''')
        pd.DataFrame([{"id": i, "nome": n} for n, i in areas.items()]).to_sql("areas", banco, if_exists="append", index=False)
        pd.DataFrame([{"id": i, "nome": n} for n, i in entidades.items()]).to_sql("entidades", banco, if_exists="append", index=False)
        pd.DataFrame([{"id": i, "descricao": r[0], "tipo": r[1], "finalidade": r[2]} for r, i in recursos.items()]).to_sql("recursos", banco, if_exists="append", index=False)
        pd.DataFrame([{"id": i, "chave": c} for c, i in credores.items()]).to_sql("credores", banco, if_exists="append", index=False)
        for nome, dados in [("dotacoes", dotacoes), ("empenhos", empenhos),
                            ("liquidacoes", liquidacoes), ("fontes_dotacao", fontes_dotacao)]:
            dados.to_sql(nome, banco, if_exists="append", index=False)
        assert not banco.execute("PRAGMA foreign_key_check").fetchall()
        assert banco.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    banco.close()
    temporario.replace(destino / "banco.sqlite")
    pd.DataFrame(fontes).to_csv(destino / "fontes.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(problemas).to_csv(destino / "qualidade.csv", index=False, encoding="utf-8-sig")
    print("Banco compacto criado e relações verificadas.", flush=True)

