"""Linha de comando: python -m radar coletar | relatorio"""
import argparse
from pathlib import Path

from radar import analise, banco, coleta


def cmd_coletar(args):
    con = banco.conectar(args.db)
    for termo in args.termos or coleta.TERMOS_PADRAO:
        try:
            vagas = [v for v in map(coleta.normalizar, coleta.buscar(termo, args.paginas)) if v]
        except Exception as e:  # uma busca que falha não derruba as outras
            print(f"[erro] '{termo}': {e}")
            continue
        encontradas, novas = coleta.persistir(con, vagas, termo, args.salvar_descricao)
        print(f"'{termo}': {encontradas} encontradas, {novas} novas")


def cmd_relatorio(args):
    con = banco.conectar(args.db)
    md = analise.relatorio_markdown(con, args.estado)
    if args.saida:
        Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(args.saida).write_text(md, encoding="utf-8")
        print(f"Relatório salvo em {args.saida}")
    else:
        print(md)


def main(argv=None):
    p = argparse.ArgumentParser(prog="radar", description="Radar do mercado de TI (estágio e júnior)")
    p.add_argument("--db", default=banco.CAMINHO_PADRAO, help="caminho do banco SQLite")
    sub = p.add_subparsers(dest="comando", required=True)

    c = sub.add_parser("coletar", help="busca vagas e grava no banco")
    c.add_argument("--termos", nargs="+", help="termos de busca (padrão: lista do projeto)")
    c.add_argument("--paginas", type=int, default=2, help="páginas por termo (50 vagas por página)")
    c.add_argument("--salvar-descricao", action="store_true", help="guarda o texto completo das vagas no banco")
    c.set_defaults(func=cmd_coletar)

    r = sub.add_parser("relatorio", help="gera o relatório em Markdown")
    r.add_argument("--estado", help="filtra por estado, ex.: 'São Paulo'")
    r.add_argument("--saida", help="arquivo de saída (padrão: imprime no terminal)")
    r.set_defaults(func=cmd_relatorio)

    args = p.parse_args(argv)
    args.func(args)
