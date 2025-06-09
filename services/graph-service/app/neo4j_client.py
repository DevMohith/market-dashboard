from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "test"))

def create_correlation(tx, company1, company2, score):
    tx.run("""
        MERGE (a:Company {symbol: $company1})
        MERGE (b:Company {symbol: $company2})
        MERGE (a)-[r:CORRELATED_WITH]->(b)
        SET r.score = $score
    """, company1=company1, company2=company2, score=score)

def create_price_jump(tx, company, change, timestamp):
    tx.run("""
        MERGE (c:Company {symbol: $company})
        CREATE (e:PriceJump {change: $change, timestamp: $timestamp})
        MERGE (e)-[:AFFECTED]->(c)
    """, company=company, change=change, timestamp=timestamp)
