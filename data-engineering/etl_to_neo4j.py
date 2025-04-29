import pandas as pd
from neo4j import GraphDatabase
from pyspark.sql import SparkSession
import psycopg2
from pyspark.sql.functions import col

def init_spark():
    spark = SparkSession.builder \
        .appName("Load Silver Users to Neo4j") \
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
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

def fetch_mapping_tables():
    conn = psycopg2.connect(
        host="localhost", port=5435,
        dbname="data-learning", user="admin", password="admin123"
    )
    genders = pd.read_sql("SELECT id, name as gender FROM genders", conn)
    occupations = pd.read_sql("SELECT id, name as occupation FROM occupations", conn)
    locations = pd.read_sql("SELECT id, name as location FROM locations", conn)
    products = pd.read_sql("SELECT id, name as product_type FROM products", conn)
    conn.close()
    return genders, occupations, locations, products

def create_user_and_product_nodes(tx, batch):
    query = """
    UNWIND $batch AS row
    MERGE (u:User {id: row.user_id})
      ON CREATE SET u.age = row.age,
                    u.gender = row.gender,
                    u.annual_income = row.annual_income,
                    u.family_assets = row.family_assets,
                    u.location = row.location,
                    u.occupation = row.occupation
    MERGE (p:Product {name: row.product_type})
    """
    tx.run(query, batch=batch)

def create_purchase_relationships(tx, batch):
    query = """
    UNWIND $batch AS row
    MATCH (u:User {id: row.user_id})
    MATCH (p:Product {name: row.product_type})
    MERGE (u)-[r:PURCHASED]->(p)
      ON CREATE SET r.label = row.label
    """
    tx.run(query, batch=batch)

def insert_data_to_neo4j(driver, records, batch_size=100):
    with driver.session() as session:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            session.execute_write(create_user_and_product_nodes, batch)
            session.execute_write(create_purchase_relationships, batch)

def main():
    spark = init_spark()
    driver = connect_neo4j()

    genders, occupations, locations, products = fetch_mapping_tables()

    df = spark.read.format("delta").load("s3a://data-learning/silver/")

    genders_df = spark.createDataFrame(genders).withColumnRenamed("id", "gender_id")
    occupations_df = spark.createDataFrame(occupations).withColumnRenamed("id", "occupation_id")
    locations_df = spark.createDataFrame(locations).withColumnRenamed("id", "location_id")
    products_df = spark.createDataFrame(products).withColumnRenamed("id", "product_type_id")

    df = df.join(genders_df, on="gender_id", how="left") \
           .join(occupations_df, on="occupation_id", how="left") \
           .join(locations_df, on="location_id", how="left") \
           .join(products_df, on="product_type_id", how="left")

    df = df.fillna({
        "user_id": 0,
        "age": 0,
        "gender": "UNKNOWN",
        "annual_income": 0,
        "family_assets": 0,
        "occupation": "UNKNOWN",
        "location": "UNKNOWN",
        "product_type": "UNKNOWN",
        "purchased": 0
    })

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    records = df.select(
        "user_id", "age", "gender", "annual_income",
        "family_assets", "occupation", "location",
        "product_type", "purchased"
    ).collect()

    data = [
        {
            "user_id": int(r["user_id"]),
            "age": int(r["age"]),
            "gender": r["gender"],
            "annual_income": float(r["annual_income"]),
            "family_assets": float(r["family_assets"]),
            "occupation": r["occupation"],
            "location": r["location"],
            "product_type": r["product_type"],
            "label": int(r["purchased"])
        } for r in records
    ]

    insert_data_to_neo4j(driver, data)
    driver.close()

    print("\n✅ Neo4j 导入完成，节点和关系已成功建立！")

if __name__ == "__main__":
    main()
