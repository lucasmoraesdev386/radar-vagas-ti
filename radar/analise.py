"""Consultas SQL de análise e geração do relatório em Markdown."""
from radar import banco


def _filtro_estado(estado):
    return (" AND estado = ?", [estado]) if estado else ("", [])


def resumo(con, estado=None):
    f, p = _filtro_estado(estado)
    return dict(con.execute(
        f"""SELECT COUNT(*) AS vagas,
                   COALESCE(SUM(tem_descricao), 0) AS com_descricao,
                   COUNT(DISTINCT empresa_id) AS empresas,
                   MIN(primeira_coleta) AS primeira_coleta,
                   MAX(ultima_coleta) AS ultima_coleta
            FROM vagas WHERE 1=1{f}""", p).fetchone())


def contagem_por(con, coluna, estado=None):
    assert coluna in {"nivel", "tipo", "modalidade"}
    f, p = _filtro_estado(estado)
    return [dict(r) for r in con.execute(
        f"""SELECT {coluna} AS grupo, COUNT(*) AS vagas,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM vagas WHERE 1=1{f}), 1) AS pct
            FROM vagas WHERE 1=1{f} GROUP BY {coluna} ORDER BY vagas DESC""", p + p)]


def top_tecnologias(con, niveis=("estagio", "junior"), estado=None, categoria=None, limite=15):
    """Tecnologias mais citadas; o percentual é sobre as vagas do filtro que têm descrição."""
    marcas = ",".join("?" * len(niveis))
    f, p = _filtro_estado(estado)
    cat, pc = (" AND t.categoria = ?", [categoria]) if categoria else ("", [])
    sql = f"""
        WITH base AS (
            SELECT id FROM vagas WHERE nivel IN ({marcas}) AND tem_descricao = 1{f}
        )
        SELECT t.nome AS tecnologia, t.categoria, COUNT(*) AS vagas,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM base), 1) AS pct
        FROM base b
        JOIN vaga_tecnologia vt ON vt.vaga_id = b.id
        JOIN tecnologias t ON t.id = vt.tecnologia_id
        WHERE 1=1{cat}
        GROUP BY t.id ORDER BY vagas DESC, t.nome LIMIT ?"""
    return [dict(r) for r in con.execute(sql, [*niveis, *p, *pc, limite])]


def top_empresas(con, estado=None, limite=10):
    f, p = _filtro_estado(estado)
    return [dict(r) for r in con.execute(
        f"""SELECT e.nome AS empresa, COUNT(*) AS vagas
            FROM vagas v JOIN empresas e ON e.id = v.empresa_id
            WHERE 1=1{f.replace('estado', 'v.estado')}
            GROUP BY e.id ORDER BY vagas DESC, e.nome LIMIT ?""", [*p, limite])]


def novas_por_semana(con, estado=None):
    f, p = _filtro_estado(estado)
    return [dict(r) for r in con.execute(
        f"""SELECT strftime('%Y-W%W', primeira_coleta) AS semana, COUNT(*) AS novas
            FROM vagas WHERE 1=1{f} GROUP BY semana ORDER BY semana""", p)]


def _tabela(linhas, colunas):
    if not linhas:
        return "_Sem dados ainda._\n"
    out = ["| " + " | ".join(colunas) + " |", "|" + "---|" * len(colunas)]
    out += ["| " + " | ".join(str(l[c]) for c in colunas) + " |" for l in linhas]
    return "\n".join(out) + "\n"


def relatorio_markdown(con, estado=None):
    r = resumo(con, estado)
    escopo = estado or "todos os estados"
    partes = [
        f"# Relatório do Radar ({escopo})\n",
        f"Gerado em {banco.agora()}. Coletas de {r['primeira_coleta']} até {r['ultima_coleta']}.\n",
        f"- Vagas coletadas: **{r['vagas']}** de **{r['empresas']}** empresas\n"
        f"- Vagas com descrição (base das análises de tecnologia): **{r['com_descricao']}**\n",
        "## Vagas por nível\n", _tabela(contagem_por(con, "nivel", estado), ["grupo", "vagas", "pct"]),
        "## Vagas por modalidade\n", _tabela(contagem_por(con, "modalidade", estado), ["grupo", "vagas", "pct"]),
        "## Tecnologias mais citadas em vagas de estágio e júnior\n",
        "_Mede menções no anúncio, não requisitos obrigatórios._\n",
        _tabela(top_tecnologias(con, estado=estado), ["tecnologia", "categoria", "vagas", "pct"]),
        "## Empresas que mais anunciam\n", _tabela(top_empresas(con, estado), ["empresa", "vagas"]),
        "## Vagas novas por semana\n", _tabela(novas_por_semana(con, estado), ["semana", "novas"]),
    ]
    return "\n".join(partes)
