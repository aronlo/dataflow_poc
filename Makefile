SHELL=/bin/sh

.PHONY: local

gcp-build-push-docker:

	docker build \
	-f local/DockerfileGCP \
	-t "gcr.io/$(PROJECT_ID)/$(GCE_INSTANCE)-image:$(GITHUB_SHA)" \
	.


	docker push "gcr.io/$(PROJECT_ID)/$(GCE_INSTANCE)-image:$(GITHUB_SHA)"
	
gcp-test-locally-image:

	python main.py \
		--runner=PortableRunner \
		--job_endpoint=embed \
		--environment_type=DOCKER \
		--environment_config= gcr.io/alicorp-sandbox/dataflow-poc:latest

gcp:

	GOOGLE_APPLICATION_CREDENTIALS="./local/credenciales/alicorp-sandbox-dataflow-poc.json"

	python main.py \
		--project=alicorp-sandbox \
		--region=us-east1 \
		--runner=DataflowRunner \
		--staging_location=gs://alo_dataflow_test/stg \
		--temp_location=gs://alo_dataflow_test/tmp \
		-experiment=use_runner_v2 \
		--worker_harness_container_image=gcr.io/alicorp-sandbox/dataflow-poc:latest


create-template:

	python main.py \
		--project=alicorp-sandbox \
		--region=us-east1 \
		--runner=DataflowRunner \
		--staging_location=gs://alo_dataflow_test/stg \
		--temp_location=gs://alo_dataflow_test/tmp \
		--template_location=gs://alo_dataflow_test/template/temp1 \
		
		#--experiment=use_runner_v2 \
		#--worker_harness_container_image=gcr.io/py-ali-as-pe-pricing-afrecho/afrecho-dataflow:latest 

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