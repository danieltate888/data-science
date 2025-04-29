import os
import psycopg2
import pyarrow.parquet as pq
import pyarrow as pa
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, upper

# Export joined user + order data from PostgreSQL to local Parquet and upload to MinIO (Bronze Layer)
def export_postgres_to_bronze():
    conn = psycopg2.connect(
        host="localhost",
        port=5435,
        user="admin",
        password="admin123",
        dbname="data-learning"
    )
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT
                       u.id AS user_id,
                       u.age,
                       u.gender_id,
                       u.annual_income,
                       u.occupation_id,
                       u.location_id,
                       u.family_assets,
                       o.product_type_id,
                       o.purchased
                   FROM users u
                            JOIN orders o ON u.id = o.user_id
                   ''')
    rows = cursor.fetchall()

    schema = pa.schema([
        ('user_id', pa.int64()),
        ('age', pa.int32()),
        ('gender_id', pa.int32()),
        ('annual_income', pa.int64()),
        ('occupation_id', pa.int32()),
        ('location_id', pa.int32()),
        ('family_assets', pa.int64()),
        ('product_type_id', pa.int32()),
        ('purchased', pa.int32()),
    ])

    table = pa.Table.from_pylist([
        {
            'user_id': r[0],
            'age': r[1],
            'gender_id': r[2],
            'annual_income': r[3],
            'occupation_id': r[4],
            'location_id': r[5],
            'family_assets': r[6],
            'product_type_id': r[7],
            'purchased': r[8],
        }
        for r in rows
    ], schema=schema)

    os.makedirs('data/bronze', exist_ok=True)
    pq.write_table(table, 'data/bronze/bronze.parquet')
    print("✅ Parquet file created locally.")

    import boto3
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='admin',
        aws_secret_access_key='admin123',
        region_name='us-east-1'
    )

    with open('data/bronze/bronze.parquet', 'rb') as f:
        s3.upload_fileobj(f, 'data-learning', 'bronze/bronze.parquet')

    print("✅ Parquet file uploaded to MinIO bucket 'data-learning' as bronze/bronze.parquet")

    cursor.close()
    conn.close()

# Initialize SparkSession with Delta and S3 support
def init_spark():
    spark = SparkSession.builder \
        .appName("ETL Pipeline") \
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

# Load Bronze Layer from MinIO
def load_bronze(spark):
    return spark.read.parquet("s3a://data-learning/bronze/bronze.parquet")

# Apply cleaning and filtering to build Silver Layer
def build_silver_layer(spark):
    df = load_bronze(spark)
    df = df.dropDuplicates(['user_id'])
    df = df.filter((col("age") >= 0) & (col("age") <= 100))
    return df

# Optional: Add derived columns for Gold Layer (not used now)
def build_gold_layer(silver_df):
    df = silver_df.withColumn("age_bucket", col("age") / 10)
    return df

# Save DataFrame to Delta Lake on MinIO
def save_delta(df, s3_path):
    df.write.format("delta").mode("overwrite").save(s3_path)

# Pipeline entry point
if __name__ == "__main__":
    export_postgres_to_bronze()
    spark = init_spark()
    silver_df = build_silver_layer(spark)
    # gold_df = build_gold_layer(silver_df)
    save_delta(silver_df, "s3a://data-learning/silver")
    # save_delta(gold_df, "s3a://data-learning/gold")
    print("✅ ETL Pipeline Completed (Bronze + Silver)")