import os
import pandas as pd
import psycopg2
from pyspark.sql import SparkSession

# Initialize Spark session with Delta Lake and S3 (MinIO) support
def init_spark():
    spark = SparkSession.builder \
        .appName("Build Features") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    hadoop_conf = spark._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.access.key", "admin")
    hadoop_conf.set("fs.s3a.secret.key", "admin123")
    hadoop_conf.set("fs.s3a.endpoint", "http://localhost:9000")
    hadoop_conf.set("fs.s3a.path.style.access", "true")
    hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    hadoop_conf.set("fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    return spark

# Fetch mapping tables from PostgreSQL: convert ID -> name
def fetch_mapping_tables():
    conn = psycopg2.connect(
        host="localhost", port=5435,
        dbname="data-learning", user="admin", password="admin123"
    )
    genders = pd.read_sql("SELECT id, name AS gender FROM genders", conn)
    occupations = pd.read_sql("SELECT id, name AS occupation FROM occupations", conn)
    locations = pd.read_sql("SELECT id, name AS location FROM locations", conn)
    products = pd.read_sql("SELECT id, name AS product_type FROM products", conn)
    conn.close()
    return genders, occupations, locations, products

# Main feature extraction pipeline
def main():
    spark = init_spark()

    # Load Gold Layer from MinIO (Delta format)
    df = spark.read.format("delta").load("s3a://data-learning/gold/")
    pandas_df = df.toPandas()

    # Restore actual names from ID columns
    genders, occupations, locations, products = fetch_mapping_tables()
    pandas_df = pandas_df.merge(genders, left_on="gender_id", right_on="id", how="left")
    pandas_df = pandas_df.merge(occupations, left_on="occupation_id", right_on="id", how="left")
    pandas_df = pandas_df.merge(locations, left_on="location_id", right_on="id", how="left")
    pandas_df = pandas_df.merge(products, left_on="product_type_id", right_on="id", how="left")

    # Drop original ID columns and duplicate merge keys
    pandas_df.drop(columns=["gender_id", "occupation_id", "location_id", "product_type_id", "id_x", "id_y", "id"], errors='ignore', inplace=True)

    # Define final feature columns and label
    feature_cols = [
        "age", "gender", "annual_income", "occupation",
        "location", "family_assets", "product_type",
        "community_id", "pagerank"
    ]
    label_col = "purchased"

    # Export features and labels as separate CSV files
    os.makedirs('data/processed', exist_ok=True)
    pandas_df[feature_cols].to_csv('data/processed/train_features.csv', index=False)
    pandas_df[label_col].to_csv('data/processed/train_labels.csv', index=False)

    print("✅ Feature extraction complete: train_features.csv & train_labels.csv generated")

if __name__ == "__main__":
    main()