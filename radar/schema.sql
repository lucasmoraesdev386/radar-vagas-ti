-- Modelo de dados do Radar. SQLite, normalizado até a 3FN.

CREATE TABLE IF NOT EXISTS empresas (
    id   INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vagas (
    id              TEXT PRIMARY KEY,                -- ex.: gupy-12345678
    fonte           TEXT NOT NULL DEFAULT 'gupy',
    titulo          TEXT NOT NULL,
    empresa_id      INTEGER REFERENCES empresas(id),
    cidade          TEXT,
    estado          TEXT,
    modalidade      TEXT NOT NULL CHECK (modalidade IN ('remoto', 'hibrido', 'presencial', 'nao_informado')),
    tipo            TEXT NOT NULL CHECK (tipo IN ('estagio', 'efetivo', 'aprendiz', 'temporario', 'outro')),
    nivel           TEXT NOT NULL CHECK (nivel IN ('estagio', 'junior', 'pleno', 'senior', 'nao_informado')),
    url             TEXT,
    tem_descricao   INTEGER NOT NULL DEFAULT 0,      -- 1 se a busca trouxe a descrição da vaga
    descricao       TEXT,                            -- só preenchida com --salvar-descricao
    publicada_em    TEXT,
    primeira_coleta TEXT NOT NULL,
    ultima_coleta   TEXT NOT NULL,
    bruto           TEXT                             -- JSON original, só com --salvar-descricao
);

CREATE TABLE IF NOT EXISTS tecnologias (
    id        INTEGER PRIMARY KEY,
    nome      TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vaga_tecnologia (
    vaga_id       TEXT    NOT NULL REFERENCES vagas(id) ON DELETE CASCADE,
    tecnologia_id INTEGER NOT NULL REFERENCES tecnologias(id),
    PRIMARY KEY (vaga_id, tecnologia_id)
);

CREATE TABLE IF NOT EXISTS coletas (
    id          INTEGER PRIMARY KEY,
    iniciada_em TEXT    NOT NULL,
    termo       TEXT    NOT NULL,
    encontradas INTEGER NOT NULL,
    novas       INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vagas_nivel    ON vagas(nivel);
CREATE INDEX IF NOT EXISTS idx_vagas_estado   ON vagas(estado);
CREATE INDEX IF NOT EXISTS idx_vagas_primeira ON vagas(primeira_coleta);
CREATE INDEX IF NOT EXISTS idx_vt_tecnologia  ON vaga_tecnologia(tecnologia_id);
