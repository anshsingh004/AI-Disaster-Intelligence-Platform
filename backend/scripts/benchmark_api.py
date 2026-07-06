import time
import os
import sys
from datetime import datetime, timezone

# Ensure root path is configured for module mapping
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal
from app.models.disaster import Disaster

client = TestClient(app)

def run_benchmarks():
    print("==========================================================")
    print("         TERRA-AURA API LATENCY BENCHMARKS               ")
    print("==========================================================")
    
    # 1. Assert database has operational records for valid query benchmarking
    db = SessionLocal()
    count = db.query(Disaster).count()
    if count == 0:
        d = Disaster(
            disaster_type="fire",
            severity_score=0.94,
            risk_level="CRITICAL",
            population_at_risk=150000,
            confidence=0.90,
            latitude=28.6139,
            longitude=77.209,
            created_at=datetime.utcnow()
        )
        db.add(d)
        db.commit()
        print("[Setup] Seeded 1 operational disaster record for test benchmarking.")
    db.close()
    
    # 2. Reset cache states
    from app.core.cache import _memory_cache, get_redis_client
    _memory_cache.clear()
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.flushall()
            print("[Setup] Flushed Redis distributed database keys.")
        except Exception:
            pass
    else:
        print("[Setup] Operating in local in-memory fallback cache mode.")

    # 3. Benchmark First Request (Un-cached / Database queries)
    start_time = time.time()
    res1 = client.get("/api/v1/disasters?page=1&limit=10")
    uncached_latency = (time.time() - start_time) * 1000
    assert res1.status_code == 200
    print(f"Un-cached request latency (Database query): {uncached_latency:.2f} ms")

    # 4. Benchmark Subsequent Requests (Cached / Redis-Memory loads)
    cached_latencies = []
    for _ in range(50):
        start_time = time.time()
        res = client.get("/api/v1/disasters?page=1&limit=10")
        latency = (time.time() - start_time) * 1000
        cached_latencies.append(latency)
        assert res.status_code == 200
        
    avg_cached_latency = sum(cached_latencies) / len(cached_latencies)
    print(f"Cached requests latency (Cache hits - average of 50 runs): {avg_cached_latency:.2f} ms")

    # 5. Speedup ratios computation
    improvement_ratio = uncached_latency / avg_cached_latency if avg_cached_latency > 0 else 0
    print(f"Operational Cache Speedup: {improvement_ratio:.2f}x faster")
    print("==========================================================")
    
    # Write Markdown results layout
    print("\n### Benchmark Results Table")
    print("| Metric | Un-cached (Database) | Cached (Redis/Memory) | Speedup Ratio |")
    print("| --- | --- | --- | --- |")
    print(f"| Latency (ms) | {uncached_latency:.2f} ms | {avg_cached_latency:.2f} ms | **{improvement_ratio:.2f}x** |")

if __name__ == "__main__":
    run_benchmarks()
