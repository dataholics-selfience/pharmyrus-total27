# ⚡ DEPLOY RÁPIDO - 5 Comandos

## 1. Git Init & Push

```bash
cd pharmyrus-FINAL

git init
git add .
git commit -m "Pharmyrus v31.0.3-ASYNC ready"
git branch -M main
git remote add origin https://github.com/SEU-USER/pharmyrus.git
git push -u origin main
```

## 2. Railway Deploy

- Acesse: https://railway.app
- **New Project** → **Deploy from GitHub**
- Selecione: `pharmyrus`
- Aguarde build (~3 min)

## 3. Configurar Variáveis

Railway Dashboard → Variables → Add:
```
GROQ_API_KEY=sua_chave_aqui
INPI_PASSWORD=sua_senha_aqui
```

**Nota:** Se você já tem um projeto Railway com essas variáveis, não precisa reconfigurar!

## 4. Adicionar Redis

Railway Dashboard:
- Click **"New"**
- **"Database"**
- **"Add Redis"**
- Pronto!

## 5. Testar

```bash
# Pegar URL
railway open

# Testar health
curl https://seu-app.railway.app/health

# Deve retornar:
{
  "status": "healthy",
  "redis": "connected",
  "version": "v31.0.3-ASYNC"
}
```

## ✅ PRONTO!

Endpoints funcionando:
- `POST /search` - Sync (5-15 min)
- `POST /search/async` - Async (sem timeout)
- `GET /search/status/{job_id}` - Progress
- `GET /search/result/{job_id}` - Resultado

**Custo:** $10/mês  
**Tempo de deploy:** ~10 minutos  

---

## 🧪 Teste Rápido com cURL

```bash
# Teste async
JOB_ID=$(curl -X POST https://seu-app.railway.app/search/async \
  -H "Content-Type: application/json" \
  -d '{"nome_molecula":"aspirin"}' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Monitor progress
watch -n 10 "curl -s https://seu-app.railway.app/search/status/$JOB_ID | jq '.'"

# Get result quando complete
curl https://seu-app.railway.app/search/result/$JOB_ID > result.json
```

**FUNCIONOU? Deploy completo!** 🎉
