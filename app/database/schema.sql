-- app/database/schema.sql

-- Tabela de faturas (AP = payable, AR = receivable)
CREATE TABLE IF NOT EXISTS invoices (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number      TEXT NOT NULL,
    invoice_type        TEXT NOT NULL CHECK(invoice_type IN ('AP','AR')),
                                           -- AP = a pagar (fornecedor), AR = a receber (cliente)
    counterparty_name   TEXT NOT NULL,     -- fornecedor (AP) ou cliente (AR)
    counterparty_email  TEXT,
    counterparty_tax_id TEXT,              -- EIN / SSN do fornecedor ou cliente
    issue_date          DATE NOT NULL,
    due_date            DATE NOT NULL,
    received_date       DATE,              -- data de ingesta pelo APEX
    amount              REAL NOT NULL,     -- valor bruto da fatura
    currency            TEXT DEFAULT 'USD',
    tax_amount          REAL DEFAULT 0.0,
    total_amount        REAL NOT NULL,     -- amount + tax_amount
    description         TEXT,
    po_number           TEXT,              -- Purchase Order de referência
    status              TEXT DEFAULT 'pending',
                        -- pending|matched|partially_matched|disputed|paid|overdue|cancelled
    source              TEXT DEFAULT 'manual',
                        -- manual|email|folder_watch|api_upload
    source_filename     TEXT,              -- nome original do arquivo PDF
    source_path         TEXT,              -- caminho local após armazenamento
    ocr_confidence      REAL DEFAULT 0.0, -- 0.0–1.0 confiança do OCR
    ocr_raw_text        TEXT,              -- texto extraído bruto (para debug)
    fraud_score         REAL DEFAULT 0.0, -- 0.0–1.0 risco de fraude (Isolation Forest)
    is_duplicate        INTEGER DEFAULT 0,-- 0=não, 1=suspeita de duplicata
    duplicate_of_id     INTEGER REFERENCES invoices(id),
    requires_human_review INTEGER DEFAULT 0,
    human_review_notes  TEXT,
    afis_transaction_id INTEGER,           -- referência ao AFIS após reconciliação
    axis_classified     INTEGER DEFAULT 0, -- 1 se o AXIS já classificou o pagamento
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices críticos para performance de busca
CREATE INDEX IF NOT EXISTS idx_invoices_type_status ON invoices(invoice_type, status);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices(due_date);
CREATE INDEX IF NOT EXISTS idx_invoices_counterparty ON invoices(counterparty_name);
CREATE INDEX IF NOT EXISTS idx_invoices_fraud_score ON invoices(fraud_score);

-- Tabela de reconciliações (match invoice ↔ pagamento AFIS)
CREATE TABLE IF NOT EXISTS reconciliations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id          INTEGER NOT NULL REFERENCES invoices(id),
    afis_transaction_id INTEGER NOT NULL,  -- ID da transação no AFIS
    match_type          TEXT NOT NULL,     -- exact|fuzzy|partial|manual
    confidence_score    REAL NOT NULL,     -- 0.0–1.0 confiança do match
    matched_amount      REAL NOT NULL,     -- valor efetivamente reconciliado
    variance_amount     REAL DEFAULT 0.0, -- diferença: invoice.total - matched_amount
    variance_reason     TEXT,             -- ex: "early payment discount", "partial"
    match_date          DATETIME DEFAULT CURRENT_TIMESTAMP,
    matched_by          TEXT DEFAULT 'apex_agent',
                        -- apex_agent|human|axis_agent
    status              TEXT DEFAULT 'pending_review',
                        -- pending_review|approved|rejected
    reviewed_by_human   INTEGER DEFAULT 0,
    human_notes         TEXT,
    approved_at         DATETIME,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reconciliations_invoice ON reconciliations(invoice_id);
CREATE INDEX IF NOT EXISTS idx_reconciliations_status ON reconciliations(status, confidence_score);

-- Tabela de campanhas de dunning (cobranças de AR vencidos)
CREATE TABLE IF NOT EXISTS dunning_campaigns (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id          INTEGER NOT NULL REFERENCES invoices(id),
    campaign_stage      INTEGER NOT NULL DEFAULT 1,
                        -- 1=friendly reminder, 2=formal notice, 3=final demand, 4=collections
    days_overdue        INTEGER NOT NULL DEFAULT 0,
    tone                TEXT NOT NULL,     -- friendly|formal|urgent|legal
    email_subject       TEXT,
    email_body          TEXT,
    email_to            TEXT,
    email_sent          INTEGER DEFAULT 0,
    email_sent_at       DATETIME,
    email_opened        INTEGER DEFAULT 0,
    email_opened_at     DATETIME,
    response_received   INTEGER DEFAULT 0,
    response_notes      TEXT,
    next_action_date    DATE,
    status              TEXT DEFAULT 'draft',
                        -- draft|scheduled|sent|responded|escalated|resolved
    generated_by        TEXT DEFAULT 'apex_agent',
                        -- apex_agent|human
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dunning_invoice ON dunning_campaigns(invoice_id);
CREATE INDEX IF NOT EXISTS idx_dunning_status ON dunning_campaigns(status, next_action_date);

-- Tabela de alertas de fraude
CREATE TABLE IF NOT EXISTS fraud_alerts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id          INTEGER REFERENCES invoices(id),
    alert_type          TEXT NOT NULL,
                        -- duplicate|vendor_anomaly|amount_spike|new_vendor|bank_mismatch
    severity            TEXT NOT NULL,     -- low|medium|high|critical
    fraud_score         REAL NOT NULL,     -- 0.0–1.0
    description         TEXT NOT NULL,    -- explicação legível do alerta
    features_flagged    TEXT,             -- JSON com features que geraram o alerta
    status              TEXT DEFAULT 'open',
                        -- open|investigating|resolved|false_positive
    investigated_by     TEXT,
    resolution_notes    TEXT,
    resolved_at         DATETIME,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fraud_alerts_status ON fraud_alerts(status, severity);

-- Tabela de DSO snapshots (Days Sales Outstanding)
CREATE TABLE IF NOT EXISTS dso_snapshots (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date       DATE NOT NULL,
    dso_days            REAL NOT NULL,     -- DSO calculado no dia
    ar_balance          REAL NOT NULL,     -- total de AR em aberto
    revenue_30d         REAL NOT NULL,     -- receita dos últimos 30 dias
    overdue_amount      REAL DEFAULT 0.0, -- total vencido em aberto
    overdue_count       INTEGER DEFAULT 0,
    collection_rate     REAL DEFAULT 0.0, -- % de AR coletado no período
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_date)
);

-- Tabela de fornecedores/clientes (counterparty registry)
CREATE TABLE IF NOT EXISTS counterparties (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    type                TEXT NOT NULL CHECK(type IN ('vendor','customer','both')),
    email               TEXT,
    phone               TEXT,
    address             TEXT,
    tax_id              TEXT UNIQUE,       -- EIN / SSN
    payment_terms       INTEGER DEFAULT 30,-- net 30 padrão
    credit_limit        REAL DEFAULT 0.0,
    avg_payment_days    REAL DEFAULT 0.0, -- média histórica de dias para pagar
    on_time_rate        REAL DEFAULT 1.0, -- 0.0–1.0 taxa de pontualidade
    total_invoiced      REAL DEFAULT 0.0,
    total_paid          REAL DEFAULT 0.0,
    fraud_flag          INTEGER DEFAULT 0, -- 0=ok, 1=suspeito, 2=bloqueado
    risk_score          REAL DEFAULT 0.0, -- 0.0–1.0 risco agregado
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_counterparties_type ON counterparties(type, fraud_flag);

-- Tabela de configurações do sistema
CREATE TABLE IF NOT EXISTS apex_settings (
    key                 TEXT PRIMARY KEY,
    value               TEXT NOT NULL,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Inserir configurações padrão
INSERT OR IGNORE INTO apex_settings (key, value) VALUES
    ('dunning_stage1_days', '7'),       -- dias após vencimento para friendly reminder
    ('dunning_stage2_days', '15'),      -- dias para formal notice
    ('dunning_stage3_days', '30'),      -- dias para final demand
    ('dunning_stage4_days', '45'),      -- dias para encaminhar a collections
    ('auto_approve_threshold', '0.90'), -- confidence score para auto-aprovação
    ('human_review_threshold', '0.60'), -- abaixo disso → revisão manual obrigatória
    ('fraud_alert_threshold', '0.65'),  -- fraud score acima disso → alerta
    ('dso_target_days', '30'),          -- meta de DSO em dias
    ('default_payment_terms', '30'),    -- net 30 padrão
    ('company_email', ''),              -- e-mail de saída para dunning
    ('company_name', '');               -- nome da empresa nas cobranças
