# 🚀 Pharmyrus v31.0.3-ASYNC

Pharmaceutical Patent Intelligence System with Async Processing

**Based on:** v31.0.3-ADVANCED-SEARCH  
**New Features:** Redis queue + Celery workers for long-running searches

---

## 🎯 What's New

### Synchronous Endpoint (Original)
```
POST /search
- Fast searches WITHOUT WIPO
- Returns immediately (5-15 min)
- Same as v31.0.3
```

### Asynchronous Endpoints (NEW!)
```
POST /search/async
- Long searches WITH WIPO
- Returns job_id instantly
- Process up to 60 minutes
- Track progress in real-time

GET /search/status/{job_id}
- Check progress (0-100%)
- See current step
- Elapsed time

GET /search/result/{job_id}
- Download final results
- Available for 24h
```

---

## 📦 Quick Deploy to Railway

### Step 1: Add Redis to Your Project

1. Open your Railway project
2. Click **"New"** → **"Database"** → **"Add Redis"**
3. Done! Railway auto-injects `REDIS_URL`

### Step 2: Deploy This Code

**Option A: From GitHub**
```bash
# Push to your repo
git add .
git commit -m "Add async processing"
git push

# Railway auto-deploys
```

**Option B: Railway CLI**
```bash
railway up
```

### Step 3: Verify

```bash
# Check health
curl https://your-app.railway.app/health

# Should return:
{
  "status": "healthy",
  "redis": "connected",
  "version": "v31.0.3-ASYNC"
}
```

---

## 🧪 Testing

### Test Sync Endpoint (No WIPO - Fast)

```bash
curl -X POST https://your-app.railway.app/search \
  -H "Content-Type: application/json" \
  -d '{
    "molecule": "aspirin",
    "countries": ["BR"],
    "include_wipo": false
  }'
```

### Test Async Endpoint (With WIPO - Slow but no timeout)

```bash
# 1. Start search
JOB_ID=$(curl -X POST https://your-app.railway.app/search/async \
  -H "Content-Type: application/json" \
  -d '{
    "molecule": "darolutamide",
    "countries": ["BR"],
    "include_wipo": true
  }' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Check status (repeat every 10s)
curl https://your-app.railway.app/search/status/$JOB_ID | jq '.'

# 3. Get result when complete
curl https://your-app.railway.app/search/result/$JOB_ID | jq '.' > result.json
```

---

## 🔧 Environment Variables

**Already set in your Railway:**
- `INPI_USERNAME` ✓
- `INPI_PASSWORD` ✓
- `GROQ_API_KEY` ✓

**Auto-injected by Railway:**
- `REDIS_URL` (when you add Redis database)
- `PORT` (Railway assigns automatically)

**No changes needed!** Your existing credentials work.

---

## 📁 File Structure

```
pharmyrus-async/
├── main.py              # FastAPI app with sync & async endpoints
├── celery_app.py        # Celery configuration
├── tasks.py             # Background tasks
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container config
├── railway.toml         # Railway deploy config
├── .env.example         # Environment template
└── README.md            # This file

# YOU NEED TO ADD:
├── search/              # Copy from v31.0.3
│   ├── epo_search.py
│   ├── google_search.py
│   ├── inpi_crawler.py
│   └── ...
```

---

## ⚠️ IMPORTANT: Copy Your Search Code

**This package has PLACEHOLDER search code!**

You need to copy your actual search modules from **v31.0.3-ADVANCED-SEARCH**:

1. **Copy search modules:**
   ```bash
   # Copy your search code
   cp -r ../v31.0.3/search/ ./
   cp -r ../v31.0.3/utils/ ./
   # etc...
   ```

2. **Update imports in `main.py`:**
   ```python
   # Replace placeholder with actual imports
   from search.epo_search import search_epo
   from search.google_search import search_google
   from search.inpi_crawler import search_inpi
   # etc...
   ```

3. **Update `execute_search()` function:**
   - Replace placeholder with your actual search logic
   - Add `progress_callback()` calls at key steps
   - Example:
     ```python
     def execute_search(molecule, countries, include_wipo, progress_callback=None):
         if progress_callback:
             progress_callback(10, "Searching EPO...")
         epo_results = search_epo(molecule)
         
         if progress_callback:
             progress_callback(30, "Searching Google...")
         google_results = search_google(molecule)
         
         # ... rest of your code
     ```

---

## 🎮 Using with Postman

### Collection Structure:

```
Pharmyrus Async
├── Health Check (GET /health)
├── Sync Search (POST /search)
└── Async Search
    ├── Start Search (POST /search/async)
    ├── Check Status (GET /search/status/:job_id)
    ├── Get Result (GET /search/result/:job_id)
    └── Cancel Job (DELETE /search/cancel/:job_id)
```

### Example Flow:

1. **Start:** POST to `/search/async` → Get `job_id`
2. **Monitor:** GET `/search/status/{job_id}` every 10s
3. **Result:** When `status: complete`, GET `/search/result/{job_id}`

---

## 💰 Cost

**Minimum Configuration:**
```
Railway Hobby: $10/month
- Single container (API + Worker)
- Redis included
- 2GB RAM
```

**When you need to scale:**
```
Add dedicated worker: +$10/month
Add 2nd worker: +$10/month
Total: $10-30/month
```

---

## 🐛 Troubleshooting

### Redis Connection Failed

**Symptom:**
```json
{"redis": "error: Connection refused"}
```

**Fix:**
1. Check Redis is added in Railway dashboard
2. Verify `REDIS_URL` environment variable exists
3. Restart the service

### Worker Not Processing Jobs

**Check logs:**
```bash
railway logs --filter worker
```

**Common issues:**
- Redis URL incorrect
- Celery not starting (check Procfile/railway.toml)
- Task import errors

### Jobs Stuck in "Queued"

**Possible causes:**
1. Worker crashed (check logs)
2. Redis disconnected
3. Task serialization error

**Solution:**
```bash
# Restart service in Railway dashboard
# Or via CLI:
railway restart
```

---

## 📊 Monitoring

### Check Job Queue:

```python
# Python script to monitor queue
from celery_app import app

# Get active tasks
active = app.control.inspect().active()
print(f"Active tasks: {active}")

# Get queued tasks
reserved = app.control.inspect().reserved()
print(f"Queued tasks: {reserved}")
```

### Railway Logs:

```bash
# Stream all logs
railway logs --tail

# Filter by service
railway logs --filter web
railway logs --filter worker
```

---

## 🚀 Next Steps

1. ✅ Deploy this version
2. ✅ Test with simple molecule (aspirin)
3. ✅ Validate async flow works
4. 🔄 Copy your actual search code from v31.0.3
5. 🔄 Test with complex molecule (darolutamide)
6. 🔄 Tomorrow: Add WIPO integration

---

## 📝 Notes

- **Sync endpoint:** Use for demos, quick tests (no WIPO)
- **Async endpoint:** Use for production, batch processing (with WIPO)
- **Timeout:** Async can process 60 min, sync limited to 5 min
- **Results:** Stored 24h in Redis, then auto-deleted
- **Scaling:** Add workers horizontally as needed

---

## 🆘 Support

Issues? Check:
1. Railway logs: `railway logs --tail`
2. Health endpoint: `/health`
3. Redis connection: Check Railway dashboard

---

**Ready to deploy? Push to Railway and test!** 🚀
