SHELL=/bin/sh

.PHONY: local

gcp-build-push-docker:

	docker build \
	-f local/DockerfileGCP \
	-t "gcr.io/alicorp-sandbox/dataflow-poc:latest" \
	--no-cache=false \
	.

	# Se configura esto para que docker haga push a Google Registry
	# gcloud auth configure-docker

	docker push "gcr.io/alicorp-sandbox/dataflow-poc:latest"
	
gcp-run-docker-locally:

	python3 main.py \
		--runner=PortableRunner \
		--job_endpoint=embed \
		--staging_location=gs://alo_dataflow_test/stg \
		--temp_location=gs://alo_dataflow_test/tmp \
		--environment_type=DOCKER \
		--environment_config=gcr.io/alicorp-sandbox/dataflow-poc:latest


gcp-run-docker-dataflow:

	python3 main.py \
		--project=alicorp-sandbox \
		--region=us-east1 \
		--runner=DataflowRunner \
		--staging_location=gs://alo_dataflow_test/stg \
		--temp_location=gs://alo_dataflow_test/tmp \
		--experiment=use_runner_v2 \
		--worker_harness_container_image=gcr.io/alicorp-sandbox/dataflow-poc:latest

gcp-create-dataflow-template:

	python3 main.py \
		--project=alicorp-sandbox \
		--region=us-east1 \
		--runner=DataflowRunner \
		--staging_location=gs://alo_dataflow_test/stg \
		--temp_location=gs://alo_dataflow_test/tmp \
		--experiment=use_runner_v2 \
		--worker_harness_container_image=gcr.io/alicorp-sandbox/dataflow-poc:latest \
		--template_location=gs://alo_dataflow_test/template/dataflow-template

local:
	
	docker build \
		-f local/DockerfileLocal \
		-t dataflow/local \
		--no-cache=false \
		.

	docker run \
		-it --rm \
		--cpus 1 --cpu-shares 1024 --memory 2g --memory-swap 4g \
		-v "$(PWD)":/app:rw \
		dataflow/local