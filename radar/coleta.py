"""Coleta de vagas na busca pública do portal da Gupy e gravação no banco.

Atenção: o endereço abaixo é interno do portal, não uma API documentada, e pode mudar.
Usamos pausa entre requisições e apenas campos públicos dos anúncios.
"""
import html
import json
import re
import time

import requests

from radar import banco, classificar
from radar.tecnologias import extrair, registrar_catalogo

GUPY_URL = "https://portal.gupy.io/api/job-search/jobs"
CABECALHOS = {"User-Agent": "radar-vagas-ti/0.1 (projeto de estudo; dados publicos)"}
TERMOS_PADRAO = [
    "desenvolvedor junior", "estagio desenvolvimento", "estagio tecnologia",
    "analista de dados junior", "estagio dados", "python junior",
    "analista de sistemas junior", "engenheiro de dados junior", "suporte tecnico junior",
]


def _limpar(texto):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", texto or ""))).strip()


def buscar(termo, paginas=2, por_pagina=50, pausa=1.0):
    """Gera os registros brutos da busca, página a página."""
    for pag in range(paginas):
        r = requests.get(GUPY_URL, headers=CABECALHOS, timeout=30,
                         params={"jobName": termo, "limit": por_pagina, "offset": pag * por_pagina})
        r.raise_for_status()
        dados = r.json().get("data") or []
        if not dados:
            return
        yield from dados
        time.sleep(pausa)


def normalizar(bruto):
    """Converte o registro da Gupy no formato do banco. Retorna None para banco de talentos."""
    tipo_gupy = str(bruto.get("type", ""))
    if "talent" in tipo_gupy.lower():
        return None
    titulo = " ".join((bruto.get("name") or "").split())
    descricao = _limpar(bruto.get("description"))
    return {
        "id": f"gupy-{bruto.get('id')}",
        "titulo": titulo,
        "empresa": (bruto.get("careerPageName") or "").strip(),
        "cidade": bruto.get("city"),
        "estado": bruto.get("state"),
        "modalidade": classificar.modalidade(bruto.get("workplaceType"), bool(bruto.get("isRemoteWork"))),
        "tipo": classificar.tipo(tipo_gupy, titulo),
        "nivel": classificar.nivel(titulo),
        "url": bruto.get("jobUrl"),
        "descricao": descricao,
        "publicada_em": bruto.get("publishedDate"),
        "bruto": bruto,
    }


def persistir(con, vagas, termo, salvar_descricao=False, agora=None):
    """Grava as vagas (idempotente) e registra a coleta. Retorna (encontradas, novas)."""
    agora = agora or banco.agora()
    registrar_catalogo(con)
    novas = 0
    for v in vagas:
        nome_empresa = v["empresa"] or "Não informada"
        con.execute("INSERT OR IGNORE INTO empresas(nome) VALUES (?)", (nome_empresa,))
        empresa_id = con.execute("SELECT id FROM empresas WHERE nome = ?", (nome_empresa,)).fetchone()[0]
        if con.execute("SELECT 1 FROM vagas WHERE id = ?", (v["id"],)).fetchone():
            con.execute("UPDATE vagas SET ultima_coleta = ? WHERE id = ?", (agora, v["id"]))
            continue
        novas += 1
        con.execute(
            """INSERT INTO vagas(id, titulo, empresa_id, cidade, estado, modalidade, tipo, nivel, url,
                                 tem_descricao, descricao, publicada_em, primeira_coleta, ultima_coleta, bruto)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (v["id"], v["titulo"], empresa_id, v["cidade"], v["estado"], v["modalidade"], v["tipo"], v["nivel"],
             v["url"], int(bool(v["descricao"])), v["descricao"] if salvar_descricao else None,
             v["publicada_em"], agora, agora,
             json.dumps(v["bruto"], ensure_ascii=False) if salvar_descricao else None))
        for nome, _ in extrair(f"{v['titulo']} {v['descricao']}"):
            con.execute(
                "INSERT OR IGNORE INTO vaga_tecnologia(vaga_id, tecnologia_id) "
                "SELECT ?, id FROM tecnologias WHERE nome = ?", (v["id"], nome))
    con.execute("INSERT INTO coletas(iniciada_em, termo, encontradas, novas) VALUES (?,?,?,?)",
                (agora, termo, len(vagas), novas))
    con.commit()
    return len(vagas), novas
