SHELL=/bin/sh

.PHONY: local

gcp-build-push-docker:

	docker build \
	-f local/DockerfileGCP \
	-t "gcr.io/alicorp-sandbox/dataflow-poc:latest" \
	--no-cache=false \
	.

	# Se configura esto para que docker haga push a Google Registry
	gcloud auth configure-docker \
		--quiet \
		--verbosity=none

	docker push "gcr.io/alicorp-sandbox/dataflow-poc:latest"
	
gcp-run-docker-locally:

	python3 main.py \
		--runner PortableRunner \
		--job_endpoint embed \
		--staging_location gs://alo_dataflow_test/stg \
		--temp_location gs://alo_dataflow_test/tmp \
		--environment_type DOCKER \
		--environment_config gcr.io/alicorp-sandbox/dataflow-poc:latest


gcp-run-docker-dataflow:

	python3 main.py \
		--project alicorp-sandbox \
		--region us-east1 \
		--runner DataflowRunner \
		--staging_location gs://alo_dataflow_test/stg \
		--temp_location gs://alo_dataflow_test/tmp \
		--experiment use_runner_v2 \
		--worker_harness_container_image gcr.io/alicorp-sandbox/dataflow-poc:latest

gcp-create-dataflow-template:

	#python3 main.py \
		--project alicorp-sandbox \
		--region us-east1 \
		--runner DataflowRunner \
		--staging_location gs://alo_dataflow_test/stg \
		--temp_location gs://alo_dataflow_test/tmp \
		--experiment use_runner_v2 \
		--worker_harness_container_image gcr.io/alicorp-sandbox/dataflow-poc:latest \
		--template_location gs://alo_dataflow_test/template/dataflow-template

	docker build \
		-f local/DockerfileGCPTemplate \
		-t create_dataflow_template/local \
		--no-cache=false \
		.

	docker run \
		-it --rm \
		--cpus 1 --cpu-shares 1024 --memory 2g --memory-swap 4g \
		-v "$(PWD)":/app:rw \
		create_dataflow_template/local

gcp-run-dataflow-from-template:

	gcloud dataflow jobs run alo-dataflow-test \
		--region us-east1 \
        --gcs-location gs://alo_dataflow_test/template/dataflow-template



gcscheduler:

	gcloud scheduler jobs delete alicorp-sandbox-dash-gcscheduler \
		--project alicorp-sandbox \
		--quiet || true

	gcloud scheduler jobs create http alicorp-sandbox-dash-gcscheduler \
		--project alicorp-sandbox \
		--time-zone "America/Lima" \
		--schedule "0 2 * * *" \
		--http-method post \
		--uri https://dataflow.googleapis.com/v1b3/projects/alicorp-sandbox/locations/us-east1/templates \
		--oauth-service-account-email alicorp-sandbox@appspot.gserviceaccount.com \
		--message-body-from-file message-body.json 
		
		
	#--max-backoff=7d \
	--max-retry-attempts=5 \
	--max-retry-duration=3h \
	--min-backoff=1h 

		
gcscheduler-run:

	gcloud scheduler jobs run alicorp-sandbox-dash-gcscheduler \
		--project alicorp-sandbox

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