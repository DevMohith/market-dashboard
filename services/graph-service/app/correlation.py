from redis_client import get_redis_connection
from neo4j_client import driver, create_correlation
from scipy.stats import pearsonr

def run_correlation_job():
    redis = get_redis_connection()
    symbols = redis.keys()

    if len(symbols) < 2:
        print("ℹ️ Not enough companies to compute correlation.")
        return

    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            sym1, sym2 = symbols[i], symbols[j]
            prices1 = list(map(float, redis.lrange(sym1, 0, -1)))
            prices2 = list(map(float, redis.lrange(sym2, 0, -1)))

            if len(prices1) != len(prices2) or len(prices1) < 5:
                continue

            score, _ = pearsonr(prices1, prices2)

            if score >= 0.9:
                with driver.session() as session:
                    session.write_transaction(create_correlation, sym1, sym2, round(score, 4))
                    print(f"🔗 Correlation saved: {sym1} ↔ {sym2} = {score:.4f}")
