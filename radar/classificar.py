"""Classificação de cada vaga: nível, tipo de contratação e modalidade."""
import re
import unicodedata


def _norm(texto):
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()


def nivel(titulo):
    t = _norm(titulo)
    if "estag" in t:
        return "estagio"
    if re.search(r"\bjunior\b|\bjr\b|\btrainee\b", t):
        return "junior"
    if re.search(r"\bpleno\b|\bpl\b", t):
        return "pleno"
    if re.search(r"\bsenior\b|\bsr\b|\bespecialista\b|\blead\b|\bstaff\b|\bprincipal\b", t):
        return "senior"
    return "nao_informado"


def tipo(tipo_gupy, titulo):
    t = _norm(tipo_gupy)
    if "intern" in t or "estag" in _norm(titulo):
        return "estagio"
    if "effective" in t:
        return "efetivo"
    if "apprentice" in t:
        return "aprendiz"
    if "temporary" in t:
        return "temporario"
    return "outro"


def modalidade(workplace_type, remoto_flag=False):
    w = _norm(workplace_type)
    if "remote" in w or "remoto" in w:
        return "remoto"
    if "hybrid" in w or "hibrido" in w:
        return "hibrido"
    if "site" in w or "presencial" in w:
        return "presencial"
    return "remoto" if remoto_flag else "nao_informado"
