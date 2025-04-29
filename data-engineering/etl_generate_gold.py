import pandas as pd
from neo4j import GraphDatabase
from pyspark.sql import SparkSession
import os
from pyspark.sql.types import *

def init_spark():
    spark = SparkSession.builder \
        .appName("Neo4j Graph Features to Gold Layer") \
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

def connect_neo4j():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "admin123"
    return GraphDatabase.driver(uri, auth=(user, password))

def build_similarity_and_community(driver):
    with driver.session() as session:
        # 删除旧关系
        session.run("MATCH ()-[r:SIMILAR]-() DELETE r")

        # 构建 SIMILAR 关系（基于 Jaccard）
        session.run("""
        CALL gds.nodeSimilarity.write(
          'User',
          {
            PURCHASED: {
              type: 'PURCHASED',
              orientation: 'UNDIRECTED'
            }
          },
          {
            similarityCutoff: 0.1,
            writeRelationshipType: 'SIMILAR',
            writeProperty: 'score'
          }
        )
        YIELD nodesCompared, relationshipsWritten, similarityDistribution
        """)

        # 运行 Louvain 社区算法
        session.run("""
        CALL gds.louvain.write(
          'User',
          {
            SIMILAR: {
              type: 'SIMILAR',
              orientation: 'UNDIRECTED',
              properties: 'score'
            }
          },
          {
            writeProperty: 'communityId'
          }
        )
        YIELD communityCount, modularity, modularities
        """)

        # 运行 PageRank
        session.run("""
        CALL gds.pageRank.write(
          'User',
          {
            SIMILAR: {
              type: 'SIMILAR',
              orientation: 'UNDIRECTED'
            }
          },
          {
            writeProperty: 'pagerank'
          }
        )
        YIELD nodePropertiesWritten, ranIterations, dampingFactor
        """)

def export_user_features(driver, output_csv_path):
    with driver.session() as session:
        result = session.run("""
        MATCH (u:User)
        RETURN 
            u.id AS user_id, 
            u.communityId AS community_id, 
            u.pagerank AS pagerank
        """)
        rows = [dict(record) for record in result]
        df = pd.DataFrame(rows)
        df.to_csv(output_csv_path, index=False)
        print(f"\n✅ Graph features exported to {output_csv_path}")

def merge_gold_layer(spark, silver_path, graph_csv, output_path):
    silver_df = spark.read.format("delta").load(silver_path)
    graph_df = spark.read.csv(graph_csv, header=True, inferSchema=True)

    df = silver_df.join(graph_df, on="user_id", how="left")
    df.write.format("delta").mode("overwrite").save(output_path)
    print(f"✅ Gold layer saved to {output_path}")

def main():
    spark = init_spark()
    driver = connect_neo4j()

    build_similarity_and_community(driver)

    csv_path = "data/tmp/neo4j_user_features.csv"
    os.makedirs("data/tmp", exist_ok=True)
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