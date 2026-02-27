from prometheus_client import Counter, Histogram, Gauge, start_http_server
import asyncio

# Метрики
analysis_requests = Counter('analysis_requests_total', 'Total analysis requests')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')
active_users = Gauge('active_users', 'Active users in last 24h')
subscription_tiers = Gauge('subscription_tiers', 'Users by tier', ['tier'])
ml_predictions = Counter('ml_predictions_total', 'ML predictions made')
cache_hits = Counter('cache_hits_total', 'Cache hits')
cache_misses = Counter('cache_misses_total', 'Cache misses')

async def start_metrics_server(port=8000):
    """Запускает HTTP сервер для Prometheus в фоне"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, start_http_server, port)
    print(f"Prometheus metrics server started on port {port}")
    
analysis_requests.inc()
with analysis_duration.time():
    result = await perform_analysis()
cache_hits.inc()
