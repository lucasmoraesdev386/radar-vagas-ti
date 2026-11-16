# Radar do mercado de TI

Pipeline de dados que acompanha, todos os dias, as vagas de **estágio e desenvolvedor júnior** anunciadas no portal da Gupy, extrai as tecnologias citadas em cada anúncio, guarda tudo num banco SQL e responde perguntas como:

- Quais tecnologias mais aparecem em vagas de estágio e júnior?
- Quanto pesa Python em comparação com Java? E SQL, Power BI, Git, inglês?
- Quantas vagas são estágio, efetivo, remoto, híbrido?
- Quais empresas mais contratam? Como o volume de vagas novas muda semana a semana?

Projeto pessoal, feito para estudar engenharia e análise de dados com dados reais e para orientar o que estudar para a minha própria busca de estágio.

## Como funciona

```
Gupy (busca pública)  ->  coleta.py  ->  classificar.py + tecnologias.py  ->  SQLite  ->  analise.py  ->  relatório / dashboard
                          (requests)     (nível, tipo, modalidade,            (3FN)       (SQL)         (Markdown / Streamlit)
                                          tecnologias por regex)
```

1. **Coleta** (`radar/coleta.py`): busca vários termos, com pausa entre requisições, e normaliza cada vaga.
2. **Classificação** (`radar/classificar.py`): nível (estágio, júnior, pleno, sênior), tipo de contratação e modalidade.
3. **Extração** (`radar/tecnologias.py`): um catálogo de ~50 tecnologias, com expressões regulares cuidadosas (por exemplo, "Java" não casa com "JavaScript").
4. **Armazenamento** (`radar/schema.sql`): empresas, vagas, tecnologias, relação vaga-tecnologia e histórico de coletas. Rodar de novo não duplica nada.
5. **Análise** (`radar/analise.py`): consultas SQL com CTEs e agregações; o relatório em Markdown sai de lá.
6. **Automação**: o GitHub Actions roda a coleta todo dia e salva o banco e o relatório no repositório, então os dados crescem ao longo do tempo.

## Modelo de dados

| Tabela | Conteúdo |
|---|---|
| `empresas` | nome da empresa (única) |
| `vagas` | id, título, empresa, cidade, estado, modalidade, tipo, nível, url, datas da primeira e da última coleta |
| `tecnologias` | nome e categoria (linguagem, banco de dados, cloud, etc.) |
| `vaga_tecnologia` | quais tecnologias cada vaga cita (N:N) |
| `coletas` | histórico: termo, quantas vagas vieram e quantas eram novas |

## Como rodar

```bash
pip install -r requirements.txt

python -m radar coletar                          # coleta com os termos padrão
python -m radar coletar --termos "python junior" "estagio dados" --paginas 3
python -m radar relatorio --estado "São Paulo"   # imprime no terminal
python -m radar relatorio --saida docs/relatorio.md

pytest                                           # testes
```

Dashboard (opcional):

```bash
pip install -r requirements-dashboard.txt
streamlit run dashboard/app.py
```

## Resultados

O relatório mais recente fica em [`docs/relatorio.md`](docs/relatorio.md), atualizado pela automação diária. _(Os principais achados serão resumidos aqui depois de algumas semanas de coleta.)_

## Decisões e limitações

- **Menções, não requisitos.** O anúncio pode citar uma tecnologia sem exigi-la. Os percentuais medem menções.
- **Só vagas com descrição entram nas análises de tecnologia.** O relatório informa quantas são.
- **Dados públicos e mínimos.** São guardados apenas campos públicos do anúncio. O texto completo da vaga só é salvo com `--salvar-descricao`; por padrão o banco guarda apenas o que foi extraído dele.
- **Fonte não oficial.** A busca da Gupy usa um endereço interno do portal, não uma API documentada, e pode mudar sem aviso. O coletor falha de forma isolada por termo e avisa no terminal.
- **Viés de amostra.** Só a Gupy, só termos de busca da lista padrão. Não representa o mercado inteiro.
- Use com moderação: o coletor já espera entre as requisições, mantenha isso.

## Próximos passos

- Segunda fonte de vagas para reduzir o viés de amostra
- Faixa de salário e benefícios, quando o anúncio informar
- Detecção de requisito obrigatório vs. desejável
- Comparação mês a mês das tecnologias em alta

## Licença

MIT
