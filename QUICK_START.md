# ⚡ QUICK START - Deploy em 10 Minutos

## 📦 O QUE ESTÁ NO PACOTE

```
pharmyrus-v31.0.3-ASYNC.tar.gz
├── main.py              ✅ FastAPI com endpoints sync & async
├── celery_app.py        ✅ Configuração Celery
├── tasks.py             ✅ Background tasks com progress
├── requirements.txt     ✅ Dependências Python
├── Dockerfile           ✅ Container config
├── railway.toml         ✅ Railway deploy config
├── test_api.py          ✅ Script de teste automatizado
├── README.md            📖 Documentação completa
├── DEPLOY_INSTRUCTIONS. 📖 Guia passo a passo
└── .env.example         📋 Template de variáveis
```

---

## 🚀 DEPLOY AGORA (3 Comandos)

```bash
# 1. Descompactar
tar -xzf pharmyrus-v31.0.3-ASYNC.tar.gz
cd pharmyrus-async

# 2. Git push (Railway auto-deploy)
git init
git add .
git commit -m "Add async infrastructure"
git push

# 3. Adicionar Redis no Railway Dashboard
# Dashboard → New → Database → Add Redis
# Pronto!
```

---

## ⚠️ IMPORTANTE: Copiar Seu Código

**Este pacote tem PLACEHOLDER code!**

Você precisa copiar seus módulos de busca da **v31.0.3-ADVANCED-SEARCH**:

```bash
# Copiar módulos de busca
cp -r ../v31.0.3-ADVANCED-SEARCH/search/ ./
cp -r ../v31.0.3-ADVANCED-SEARCH/utils/ ./
# ... outros módulos necessários

# Atualizar imports em main.py
# Ver: README.md seção "Copy Your Search Code"
```

---

## 🧪 TESTAR (1 Comando)

```bash
# Rodar script de teste
python test_api.py https://seu-app.railway.app
```

**Resultado esperado:**
```
✅ Health check passed
✅ Sync search completed
✅ Async search completed
✅ Results saved to aspirin_result.json
```

---

## 📋 CHECKLIST

### Antes do Deploy:
- [ ] Descompactou o arquivo
- [ ] Copiou código de busca da v31.0.3
- [ ] Atualizou imports em main.py
- [ ] Testou localmente (opcional)

### Deploy:
- [ ] Push para GitHub/Railway
- [ ] Adicionou Redis no Railway
- [ ] Verificou health endpoint
- [ ] Variáveis de ambiente OK (INPI, Groq já existem)

### Validação:
- [ ] `/health` retorna "healthy"
- [ ] Redis mostra "connected"
- [ ] Teste sync funciona
- [ ] Teste async retorna job_id
- [ ] Worker aparece nos logs

---

## 💰 CUSTO

**Configuração Mínima:**
- $10/mês (Railway Hobby)
- 1 container (API + Worker juntos)
- Redis incluído
- 2GB RAM

**Depois, se precisar:**
- Worker dedicado: +$10/mês
- 2º worker: +$10/mês
- Total: $10-30/mês

---

## 🔧 CONFIGURAÇÃO

### Variáveis que Você JÁ TEM:
✅ `INPI_USERNAME=dnm48`
✅ `INPI_PASSWORD`
✅ `GROQ_API_KEY`

### Variáveis Auto-Injetadas:
✅ `REDIS_URL` (Railway adiciona automaticamente)
✅ `PORT` (Railway define)

**NÃO precisa configurar NADA manualmente!**

---

## 🎯 ENDPOINTS

### Synchronous (Sem WIPO - Rápido)
```
POST /search
- Retorna em 5-15 minutos
- Sem timeout
- Mesmo comportamento da v31.0.3
```

### Asynchronous (Com WIPO - Sem limite)
```
POST /search/async        → Retorna job_id (< 1s)
GET /search/status/{id}   → Progresso 0-100%
GET /search/result/{id}   → Resultado final
DELETE /search/cancel/{id} → Cancelar job
```

---

## 🐛 PROBLEMAS?

### Redis não conecta:
```bash
# Verificar
railway variables  # REDIS_URL deve existir

# Solução
# Dashboard → Add Redis
# Restart service
```

### Worker não processa:
```bash
# Ver logs
railway logs --tail | grep celery

# Deve mostrar: "celery@hostname ready"

# Se não: verificar railway.toml
```

### Deploy falha:
```bash
# Ver erro
railway logs --tail

# Comum: Faltando código de busca da v31.0.3
# Solução: Copiar módulos search/
```

---

## 📖 DOCUMENTAÇÃO COMPLETA

- **README.md** - Visão geral e features
- **DEPLOY_INSTRUCTIONS.md** - Passo a passo detalhado
- **test_api.py** - Script de teste automatizado

---

## ⏭️ PRÓXIMOS PASSOS

### HOJE:
1. Deploy esta versão
2. Validar async funciona
3. Testar com aspirin

### AMANHÃ:
4. Adicionar WIPO layer
5. Testar timeout 60min
6. Validar dados

---

## ✅ TUDO PRONTO!

**O que você tem:**
- ✅ Infraestrutura assíncrona completa
- ✅ Redis + Celery configurados
- ✅ Endpoints sync & async
- ✅ Progress tracking
- ✅ Deploy em 1 comando
- ✅ $10/mês custo mínimo

**O que falta:**
- 🔄 Copiar seu código de busca
- 🔄 Testar em produção
- 🔄 Adicionar WIPO (amanhã)

**DEPLOY AGORA E TESTE!** 🚀
