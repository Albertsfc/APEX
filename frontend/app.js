document.addEventListener('DOMContentLoaded', () => {
    // Navigational Logic
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetView = item.getAttribute('data-view');
            
            navItems.forEach(n => n.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));
            
            item.classList.add('active');
            document.getElementById(`view-${targetView}`).classList.add('active');

            // Load data when view is opened
            if(targetView === 'reconciliation') loadReconciliations();
            if(targetView === 'dunning') loadDunning();
            if(targetView === 'fraud') loadFraud();
        });
    });

    // Upload Form
    const uploadForm = document.getElementById('upload-form');
    if(uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('invoice-file');
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const resultDiv = document.getElementById('upload-result');
            resultDiv.innerHTML = '<p style="color:var(--color-primary);margin-top:10px;">Fazendo upload e iniciando LangGraph...</p>';

            try {
                const res = await fetch('/api/v1/invoices/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                resultDiv.innerHTML = `<p style="color:var(--color-success);margin-top:10px;">${data.message}</p>`;
                fileInput.value = '';
            } catch (error) {
                resultDiv.innerHTML = `<p style="color:var(--color-error);margin-top:10px;">Erro de upload: ${error.message}</p>`;
            }
        });
    }

    // API calls to load data
    async function loadReconciliations() {
        const container = document.getElementById('reconciliation-list');
        try {
            const res = await fetch('/api/v1/reconciliation/pending');
            const data = await res.json();
            
            if(data.length === 0) {
                container.innerHTML = '<p>Nenhuma reconciliação pendente.</p>';
                return;
            }

            let html = `<table><tr><th>ID Fatura</th><th>ID AFIS</th><th>Confiança</th><th>Valor</th><th>Ação</th></tr>`;
            data.forEach(item => {
                html += `<tr>
                    <td>${item.invoice_id}</td>
                    <td>${item.afis_transaction_id}</td>
                    <td>${(item.confidence_score * 100).toFixed(1)}%</td>
                    <td>$${item.matched_amount.toFixed(2)}</td>
                    <td><button class="btn btn-primary" onclick="approveRecon(${item.id})">Aprovar</button></td>
                </tr>`;
            });
            html += `</table>`;
            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = 'Erro ao carregar dados.';
        }
    }

    async function loadFraud() {
        const container = document.getElementById('fraud-list');
        try {
            const res = await fetch('/api/v1/fraud/alerts?status=open');
            const data = await res.json();
            
            if(data.length === 0) {
                container.innerHTML = '<p>Nenhum alerta de fraude aberto.</p>';
                return;
            }

            let html = `<table><tr><th>ID Fatura</th><th>Severidade</th><th>Score</th><th>Descrição</th><th>Ação</th></tr>`;
            data.forEach(item => {
                html += `<tr>
                    <td>${item.invoice_id}</td>
                    <td><span style="color:var(--color-error);font-weight:bold;">${item.severity.toUpperCase()}</span></td>
                    <td>${(item.fraud_score * 100).toFixed(1)}%</td>
                    <td>${item.description}</td>
                    <td><button class="btn btn-primary" onclick="resolveFraud(${item.id})">Resolver Falso Positivo</button></td>
                </tr>`;
            });
            html += `</table>`;
            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = 'Erro ao carregar dados.';
        }
    }

    async function loadDunning() {
        const container = document.getElementById('dunning-list');
        try {
            const res = await fetch('/api/v1/dunning/campaigns');
            const data = await res.json();
            
            if(data.length === 0) {
                container.innerHTML = '<p>Nenhuma campanha ativa.</p>';
                return;
            }

            let html = `<table><tr><th>Fatura</th><th>Estágio</th><th>Dias Atraso</th><th>Status</th></tr>`;
            data.forEach(item => {
                html += `<tr>
                    <td>${item.invoice_id}</td>
                    <td>${item.campaign_stage}</td>
                    <td>${item.days_overdue}</td>
                    <td>${item.status}</td>
                </tr>`;
            });
            html += `</table>`;
            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = 'Erro ao carregar dados.';
        }
    }

    // Exported globals for inline onclick
    window.approveRecon = async (id) => {
        try {
            await fetch(`/api/v1/reconciliation/${id}/approve`, {method: 'POST'});
            loadReconciliations();
        } catch(e) {
            alert("Erro ao aprovar.");
        }
    };

    window.resolveFraud = async (id) => {
        try {
            await fetch(`/api/v1/fraud/${id}/resolve?resolution=false_positive`, {method: 'POST'});
            loadFraud();
        } catch(e) {
            alert("Erro ao resolver fraude.");
        }
    };
});
