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

	docker build \
	-f local/DockerfileGCP \
	-t gcp_dataflow/local \
	--no-cache=false \
	.

	python main.py \
		--runner=PortableRunner \
		--job_endpoint=embed \
		--environment_type=DOCKER \
		--environment_config= gcp_dataflow/local


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