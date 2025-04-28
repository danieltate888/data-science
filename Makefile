# Makefile

build_features:
	python3 feature_engineering/build_features.py

train_model:
	python3 models/train_model.py

start_server:
	python3 api/app.py