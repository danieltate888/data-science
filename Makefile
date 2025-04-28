# Makefile

build_features:
	python3 feature_engineering/build_features.py

train_model:
	python3 models/train_model.py

start_server:
	uvicorn api.app:app --host 0.0.0.0 --port 6000 --reload

evaluate_model:
	python3 models/evaluate_model.py

generate_dataset:
	python3 scripts/generate_dataset.py

find_best_threshold:
	python3 scripts/find_best_threshold.py