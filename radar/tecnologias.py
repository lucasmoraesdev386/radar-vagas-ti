"""Catálogo de tecnologias e extração por expressões regulares.

É uma aproximação: o texto de uma vaga pode citar uma tecnologia sem exigi-la.
Os resultados medem *menções*, não requisitos.
"""
import re

CATALOGO = [
    ("Python", "linguagem", r"\bpython\b"),
    ("Java", "linguagem", r"\bjava\b(?!\s?script)"),
    ("JavaScript", "linguagem", r"\bjavascript\b"),
    ("TypeScript", "linguagem", r"\btypescript\b"),
    ("C#", "linguagem", r"(?<!\w)c#"),
    ("C++", "linguagem", r"(?<!\w)c\+\+"),
    ("PHP", "linguagem", r"\bphp\b"),
    ("Go", "linguagem", r"\bgolang\b"),
    ("Kotlin", "linguagem", r"\bkotlin\b"),
    ("Swift", "linguagem", r"\bswift\b"),
    ("SQL", "banco de dados", r"\bsql\b"),
    ("PostgreSQL", "banco de dados", r"\bpostgres(ql)?\b"),
    ("MySQL", "banco de dados", r"\bmysql\b"),
    ("SQL Server", "banco de dados", r"\bsql\s?server\b"),
    ("Oracle", "banco de dados", r"\boracle\b"),
    ("MongoDB", "banco de dados", r"\bmongo(db)?\b"),
    ("Power BI", "dados", r"\bpower\s?bi\b"),
    ("Excel", "dados", r"\bexcel\b"),
    ("Tableau", "dados", r"\btableau\b"),
    ("Pandas", "dados", r"\bpandas\b"),
    ("Spark", "dados", r"\b(py)?spark\b"),
    ("Airflow", "dados", r"\bairflow\b"),
    ("ETL", "dados", r"\betl\b"),
    ("Machine Learning", "dados", r"machine learning|aprendizado de m[aá]quina"),
    ("AWS", "cloud", r"\baws\b|amazon web services"),
    ("Azure", "cloud", r"\bazure\b"),
    ("GCP", "cloud", r"\bgcp\b|google cloud"),
    ("Docker", "devops", r"\bdocker\b"),
    ("Kubernetes", "devops", r"\bkubernetes\b|\bk8s\b"),
    ("CI/CD", "devops", r"\bci/cd\b|\bjenkins\b"),
    ("Git", "ferramentas", r"\bgit\b|\bgithub\b|\bgitlab\b"),
    ("Linux", "ferramentas", r"\blinux\b"),
    ("React", "framework", r"\breact(\.?js)?\b"),
    ("Angular", "framework", r"\bangular\b"),
    ("Vue", "framework", r"\bvue(\.?js)?\b"),
    ("Node.js", "framework", r"\bnode(\.?js)?\b"),
    (".NET", "framework", r"\.net\b|\bdotnet\b"),
    ("Django", "framework", r"\bdjango\b"),
    ("Flask", "framework", r"\bflask\b"),
    ("FastAPI", "framework", r"\bfastapi\b"),
    ("Spring", "framework", r"\bspring\b"),
    ("Flutter", "framework", r"\bflutter\b"),
    ("HTML/CSS", "web", r"\bhtml5?\b|\bcss3?\b"),
    ("APIs REST", "arquitetura", r"\brest(ful)?\b"),
    ("Scrum/Agile", "metodologia", r"\bscrum\b|\bkanban\b|\bagile\b|\bágil\b"),
    ("Testes/QA", "qualidade", r"\bselenium\b|\bcypress\b|\bqa\b|testes automatizados"),
    ("Salesforce", "plataforma", r"\bsalesforce\b"),
    ("SAP", "plataforma", r"\bsap\b"),
    ("RPA", "plataforma", r"\brpa\b|power automate"),
    ("Inglês", "idioma", r"\bingl[eê]s\b|\benglish\b"),
]

_COMPILADO = [(n, c, re.compile(rx, re.IGNORECASE)) for n, c, rx in CATALOGO]


def extrair(texto):
    """Retorna a lista de (nome, categoria) das tecnologias citadas no texto, sem repetição."""
    return [(n, c) for n, c, rx in _COMPILADO if rx.search(texto or "")]


def registrar_catalogo(con):
    con.executemany("INSERT OR IGNORE INTO tecnologias(nome, categoria) VALUES (?, ?)",
                    [(n, c) for n, c, _ in CATALOGO])
