import pandas as pd
from neo4j import GraphDatabase
from pyspark.sql import SparkSession
import os

# Initialize SparkSession with Delta Lake & MinIO configs
def init_spark():
    spark = SparkSession.builder \
        .appName("Generate Gold Layer from Silver + Graph") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.access.key", "admin")
    hadoop_conf.set("fs.s3a.secret.key", "admin123")
    hadoop_conf.set("fs.s3a.endpoint", "http://127.0.0.1:9000")
    hadoop_conf.set("fs.s3a.path.style.access", "true")
    hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    hadoop_conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    return spark

# Connect to Neo4j
def connect_neo4j():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "admin123"
    return GraphDatabase.driver(uri, auth=(user, password))

# Run graph algorithms in Neo4j and write features
def build_similarity_and_community(driver):
    with driver.session() as session:
        session.run("MATCH ()-[r:SIMILAR]-() DELETE r")
        result = session.run("CALL gds.graph.exists('userGraph') YIELD exists")
        record = result.single()
        if record and record["exists"]:
            session.run("CALL gds.graph.drop('userGraph') YIELD graphName")
        session.run("""
        CALL gds.graph.project(
          'userGraph',
          'User',
          {
            PURCHASED: { type: 'PURCHASED', orientation: 'UNDIRECTED' }
          }
        )""")
        session.run("""
        CALL gds.nodeSimilarity.write('userGraph', {
            writeRelationshipType: 'SIMILAR',
            writeProperty: 'score',
            similarityCutoff: 0.1
        })""")
        session.run("""
        CALL gds.louvain.write('userGraph', { writeProperty: 'communityId' })""")
        session.run("""
        CALL gds.pageRank.write('userGraph', { writeProperty: 'pagerank' })""")

# Export Neo4j graph features to CSV
def export_user_features(driver, output_csv_path):
    with driver.session() as session:
        result = session.run("""
        MATCH (u:User)
        RETURN u.id AS user_id, u.communityId AS community_id, u.pagerank AS pagerank
        """)
        rows = [dict(record) for record in result]
        df = pd.DataFrame(rows)
        df.to_csv(output_csv_path, index=False)

# Join existing Silver table with graph features to produce Gold
def merge_gold_layer(spark, silver_path, graph_csv, output_path):
    silver_df = spark.read.format("delta").load(silver_path)
    graph_df = spark.read.csv(graph_csv, header=True, inferSchema=True)
    df = silver_df.join(graph_df, on="user_id", how="left")
    df.write.format("delta") \
        .option("mergeSchema", "true") \
        .mode("overwrite") \
        .save(output_path)
    print(f"✅ Gold layer saved successfully to: {output_path}")

# Generate Gold Layer by combining existing Silver Layer + Graph Features
def main():
    spark = init_spark()
    driver = connect_neo4j()
    build_similarity_and_community(driver)

    os.makedirs("data/tmp", exist_ok=True)
    csv_path = "data/tmp/neo4j_user_features.csv"
    export_user_features(driver, csv_path)

    merge_gold_layer(
        spark,
        silver_path="s3a://data-learning/silver/",
        graph_csv=csv_path,
        output_path="s3a://data-learning/gold/"
    )
    driver.close()

if __name__ == "__main__":
    main()