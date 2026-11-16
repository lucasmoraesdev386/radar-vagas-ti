import pytest

from radar import analise, banco, classificar, cli, coleta
from radar.tecnologias import extrair


def bruto(id_, nome, descricao="", cidade="São Paulo", estado="São Paulo", tipo="vacancy_type_effective",
          workplace="hybrid", empresa="Acme"):
    return {"id": id_, "name": nome, "description": descricao, "city": cidade, "state": estado, "type": tipo,
            "workplaceType": workplace, "careerPageName": empresa, "jobUrl": f"https://x.gupy.io/job/{id_}"}


@pytest.fixture
def con():
    c = banco.conectar(":memory:")
    yield c
    c.close()


def carregar(con, brutos, termo="t", **kw):
    vagas = [v for v in map(coleta.normalizar, brutos) if v]
    return coleta.persistir(con, vagas, termo, **kw)


# ---------- classificação ----------
@pytest.mark.parametrize("titulo,esperado", [
    ("Estágio em Dados", "estagio"),
    ("Pessoa Estagiária - TI", "estagio"),
    ("Desenvolvedor Júnior", "junior"),
    ("Analista Jr.", "junior"),
    ("Desenvolvedor Pleno", "pleno"),
    ("Engenheira de Dados Sênior", "senior"),
    ("Analista de Sistemas", "nao_informado"),
])
def test_nivel(titulo, esperado):
    assert classificar.nivel(titulo) == esperado


def test_modalidade_e_tipo():
    assert classificar.modalidade("remote") == "remoto"
    assert classificar.modalidade("hybrid") == "hibrido"
    assert classificar.modalidade("on-site") == "presencial"
    assert classificar.modalidade(None, True) == "remoto"
    assert classificar.modalidade(None) == "nao_informado"
    assert classificar.tipo("vacancy_type_internship", "Dev") == "estagio"
    assert classificar.tipo("vacancy_type_effective", "Dev") == "efetivo"


# ---------- extração de tecnologias ----------
def nomes(texto):
    return {n for n, _ in extrair(texto)}


def test_java_nao_confunde_com_javascript():
    assert nomes("Conhecimento em JavaScript") == {"JavaScript"}
    assert "Java" in nomes("Experiência com Java e Spring")


def test_extracao_variada():
    t = nomes("Power BI, SQL Server, C#, .NET, Python/Pandas, Git e inglês")
    assert {"Power BI", "SQL Server", "C#", ".NET", "Python", "Pandas", "Git", "Inglês"} <= t
    assert "Excel" not in nomes("pessoa excelente e comunicativa")


# ---------- coleta e banco ----------
def test_normalizar_ignora_banco_de_talentos():
    assert coleta.normalizar(bruto(1, "Banco de Talentos", tipo="vacancy_type_talent_pool")) is None


def test_persistir_e_idempotente(con):
    b = [bruto(1, "Dev Python Júnior", "Python e SQL"), bruto(2, "Estágio em Dados", "Power BI")]
    assert carregar(con, b) == (2, 2)
    assert carregar(con, b) == (2, 0)  # segunda rodada não duplica
    assert con.execute("SELECT COUNT(*) FROM vagas").fetchone()[0] == 2
    assert con.execute("SELECT COUNT(*) FROM coletas").fetchone()[0] == 2


def test_descricao_so_e_guardada_quando_pedido(con):
    carregar(con, [bruto(1, "Dev Júnior", "Python")])
    linha = con.execute("SELECT descricao, bruto, tem_descricao FROM vagas").fetchone()
    assert linha["descricao"] is None and linha["bruto"] is None and linha["tem_descricao"] == 1


# ---------- análise ----------
@pytest.fixture
def populado(con):
    carregar(con, [
        bruto(1, "Dev Júnior", "Python, SQL e Git", empresa="A"),
        bruto(2, "Dev Júnior", "Python e Docker", empresa="A"),
        bruto(3, "Estágio em Dados", "Power BI e SQL", empresa="B"),
        bruto(4, "Dev Sênior", "Java", empresa="B"),
        bruto(5, "Dev Júnior", "", empresa="C"),                       # sem descrição: fora da base de tecnologias
        bruto(6, "Dev Júnior", "Python", estado="Rio de Janeiro", empresa="C"),
    ])
    return con


def test_top_tecnologias_percentual(populado):
    r = {x["tecnologia"]: x for x in analise.top_tecnologias(populado, estado="São Paulo")}
    # base SP júnior/estágio com descrição = vagas 1, 2 e 3
    assert r["Python"]["vagas"] == 2 and r["Python"]["pct"] == 66.7
    assert r["SQL"]["vagas"] == 2
    assert "Java" not in r  # vaga sênior fica de fora


def test_resumo_e_contagens(populado):
    r = analise.resumo(populado)
    assert r["vagas"] == 6 and r["com_descricao"] == 5 and r["empresas"] == 3
    niveis = {x["grupo"]: x["vagas"] for x in analise.contagem_por(populado, "nivel")}
    assert niveis == {"junior": 4, "estagio": 1, "senior": 1}
    assert analise.resumo(populado, "Rio de Janeiro")["vagas"] == 1


def test_top_empresas_filtra_estado(populado):
    assert analise.top_empresas(populado, "Rio de Janeiro") == [{"empresa": "C", "vagas": 1}]


def test_relatorio_markdown(populado):
    md = analise.relatorio_markdown(populado)
    assert "# Relatório do Radar" in md and "| Python |" in md


def test_relatorio_com_banco_vazio(con):
    assert "Sem dados ainda" in analise.relatorio_markdown(con)


def test_cli_coletar_com_busca_simulada(monkeypatch, tmp_path):
    monkeypatch.setattr(coleta, "buscar", lambda termo, paginas=2: iter([bruto(10, "Dev Júnior", "Python")]))
    db = tmp_path / "t.db"
    cli.main(["--db", str(db), "coletar", "--termos", "python"])
    cli.main(["--db", str(db), "relatorio", "--saida", str(tmp_path / "r.md")])
    assert "Dev" in (tmp_path / "r.md").read_text(encoding="utf-8") or "Python" in (tmp_path / "r.md").read_text(encoding="utf-8")
