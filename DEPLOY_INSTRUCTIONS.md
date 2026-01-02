# 🚀 DEPLOY INSTRUCTIONS - Pharmyrus Async

## ⚡ Quick Start (10 minutos)

### 1. Preparar o Código (5 min)

```bash
# Descompactar o arquivo
tar -xzf pharmyrus-async.tar.gz
cd pharmyrus-async

# IMPORTANTE: Copiar seu código de busca da v31.0.3
# Você precisa adicionar seus módulos de busca existentes:
# - search/epo_search.py
# - search/google_search.py  
# - search/inpi_crawler.py
# - utils/...
# - etc...

# Depois atualizar main.py para usar suas funções reais
```

### 2. Deploy na Railway (3 min)

#### Opção A: Via GitHub (Recomendado)

```bash
# Criar repo (se não tiver)
git init
git add .
git commit -m "Add async infrastructure"

# Push para GitHub
git remote add origin https://github.com/seu-user/pharmyrus.git
git push -u origin main

# Na Railway:
# 1. New Project → Deploy from GitHub
# 2. Selecionar repo pharmyrus
# 3. Railway faz deploy automaticamente
```

#### Opção B: Railway CLI

```bash
# Instalar CLI (se não tiver)
npm install -g @railway/cli

# Login
railway login

# Link ao projeto existente
railway link

# Deploy
railway up
```

### 3. Adicionar Redis (2 min)

```bash
# Via Railway Dashboard:
# 1. Abrir seu projeto
# 2. "New" → "Database" → "Add Redis"
# 3. Pronto! REDIS_URL é injetado automaticamente

# OU via CLI:
railway add redis
```

### 4. Verificar Deploy (1 min)

```bash
# Pegar URL do projeto
railway open

# Testar health
curl https://seu-app.railway.app/health

# Deve retornar:
# {
#   "status": "healthy",
#   "redis": "connected",
#   "version": "v31.0.3-ASYNC"
# }
```

---

## 🔧 Configuração Detalhada

### Environment Variables

**Já configuradas no seu Railway:**
- ✅ `INPI_USERNAME=dnm48`
- ✅ `INPI_PASSWORD=***`
- ✅ `GROQ_API_KEY=***`

**Auto-injetadas pela Railway:**
- ✅ `REDIS_URL` (quando adiciona Redis)
- ✅ `PORT` (Railway define automaticamente)

**NÃO precisa configurar nada manualmente!**

### Verificar Variáveis

```bash
# Via CLI
railway variables

# Deve mostrar:
# INPI_USERNAME=dnm48
# INPI_PASSWORD=***
# GROQ_API_KEY=***
# REDIS_URL=redis://...
# PORT=...
```

---

## 🧪 Testar Após Deploy

### 1. Health Check

```bash
curl https://seu-app.railway.app/health
```

**Esperado:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "version": "v31.0.3-ASYNC"
}
```

### 2. Teste Sync (Rápido - Sem WIPO)

```bash
curl -X POST https://seu-app.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "molecule": "aspirin",
    "countries": ["BR"]
  }'
```

### 3. Teste Async (Completo)

```bash
# 1. Iniciar busca
JOB_ID=$(curl -X POST https://seu-app.railway.app/search/async \
  -H "Content-Type: application/json" \
  -d '{
    "molecule": "aspirin",
    "countries": ["BR"],
    "include_wipo": false
  }' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Monitorar progresso (repetir a cada 10s)
watch -n 10 "curl -s https://seu-app.railway.app/search/status/$JOB_ID | jq '.'"

# 3. Quando completo, baixar resultado
curl https://seu-app.railway.app/search/result/$JOB_ID | jq '.' > result.json
```

### 4. Teste com Script Python

```bash
# Usar o script incluído
python test_api.py https://seu-app.railway.app
```

---

## 🐛 Troubleshooting

### Problema: Redis não conecta

**Sintoma:**
```json
{"redis": "error: Connection refused"}
```

**Solução:**
1. Verificar Redis foi adicionado: Railway Dashboard → Services → Redis
2. Verificar REDIS_URL existe: `railway variables`
3. Restart: Railway Dashboard → Service → Restart

### Problema: Worker não processa jobs

**Sintoma:**
- Jobs ficam "queued" para sempre
- Status nunca muda para "running"

**Solução:**
```bash
# Ver logs do worker
railway logs --filter celery

# Verificar se Celery iniciou
# Deve mostrar: "celery@hostname ready"

# Se não aparece, verificar railway.toml
# startCommand deve ter: celery -A celery_app worker
```

### Problema: Deploy falha

**Sintoma:**
```
Build failed
or
Container crashed
```

**Solução:**
```bash
# Ver logs completos
railway logs --tail

# Verificar requirements.txt
# Verificar Dockerfile
# Verificar railway.toml

# Rebuild
railway up --detach
```

### Problema: 500 Internal Server Error

**Sintoma:**
```bash
curl /search/async
# Returns: 500 Internal Server Error
```

**Solução:**
```bash
# Ver logs de erro
railway logs --tail

# Comum: Faltando módulos de busca
# Solução: Copiar código da v31.0.3

# Comum: Import errors
# Verificar imports em main.py e tasks.py
```

---

## 📊 Monitoramento

### Logs em Tempo Real

```bash
# Stream all logs
railway logs --tail

# Filter by text
railway logs --tail | grep "ERROR"
railway logs --tail | grep "search"
```

### Métricas

```bash
# Ver uso de recursos
railway status

# Ver uptime
railway info
```

### Celery Monitoring

```python
# Python script para ver fila
from celery_app import app

# Inspect workers
inspect = app.control.inspect()

# Active tasks
print("Active:", inspect.active())

# Queued tasks  
print("Reserved:", inspect.reserved())

# Stats
print("Stats:", inspect.stats())
```

---

## 🔄 Atualizar Código

### Deploy Nova Versão

```bash
# Fazer mudanças no código
# ...

# Commit
git add .
git commit -m "Update search logic"

# Push (Railway auto-deploys)
git push

# OU se usando CLI:
railway up
```

### Rollback

```bash
# Via Dashboard:
# Deployments → Select previous → Redeploy

# Via CLI:
railway rollback
```

---

## 📈 Scaling

### Adicionar Worker Dedicado

Quando ficcar lento, separar API e Worker:

```bash
# 1. Railway Dashboard → New Service
# 2. Nome: "pharmyrus-worker"
# 3. Deploy do mesmo código
# 4. Environment Variables → Copy from main service
# 5. Start Command: 
#    celery -A celery_app worker --loglevel=info --concurrency=1
```

**Custo:** +$10/mês por worker

### Adicionar Mais Workers

Para processar múltiplos jobs em paralelo:

```bash
# Worker 2, Worker 3, etc...
# Cada um processa 1 job simultâneo
# 3 workers = 3 jobs paralelos
```

**Custo:** $10/mês por worker adicional

---

## ✅ Checklist Pós-Deploy

- [ ] Health check retorna `healthy`
- [ ] Redis conectado (`redis: connected`)
- [ ] Endpoint sync funciona
- [ ] Endpoint async retorna job_id
- [ ] Status endpoint mostra progresso
- [ ] Result endpoint retorna dados
- [ ] Logs mostram worker ativo
- [ ] Testado com molécula real (aspirin)
- [ ] Testado com molécula complexa (darolutamide)

---

## 📝 Próximos Passos

### Hoje:
1. ✅ Deploy desta versão
2. ✅ Validar que async funciona
3. ✅ Testar com moléculas simples

### Amanhã:
4. 🔄 Adicionar WIPO layer
5. 🔄 Testar com timeout 60min
6. 🔄 Validar dados WIPO

### Futuro:
7. 📊 Frontend com progress bar
8. 📧 Email notifications
9. 📁 Batch CSV upload
10. 🎨 Dashboard de jobs

---

## 🆘 Suporte

**Logs não ajudam?**

1. Check Railway Status: https://status.railway.app
2. Check service logs: `railway logs --tail`
3. Check Redis connection in Railway dashboard
4. Restart service: Railway Dashboard → Restart

**Ainda com problemas?**

- Verifique se copiou TODO o código da v31.0.3
- Verifique imports em main.py
- Verifique REDIS_URL está setado
- Verifique worker está rodando nos logs

---

**Pronto! Sistema async funcionando!** 🎉
