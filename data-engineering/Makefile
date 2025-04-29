# Makefile

pipeline:
	@spark-submit \
		--packages io.delta:delta-spark_2.12:3.1.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
		--conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
		--conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
		etl_pipeline.py

to_neo4j:
	python3 etl_to_neo4j.py

generate_gold:
	python3 etl_generate_gold.py