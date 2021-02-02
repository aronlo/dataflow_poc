SHELL=/bin/sh

.PHONY: local

gcp:

	docker build \
	-f local/DockerfileGCP \
	-t gcr.io/alicorp-sandbox/dataflow-poc:latest \
	--no-cache=false \
	.

	docker push gcr.io/alicorp-sandbox/dataflow-poc:latest
		
	docker run \
		-it --rm \
		--cpus 1 --cpu-shares 1024 --memory 2g --memory-swap 4g \
		-v "$(PWD)":/app:rw \
		gcr.io/alicorp-sandbox/dataflow-poc:latest

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
	
		
	#docker run \
		-it --rm \
		--cpus 1 --cpu-shares 1024 --memory 2g --memory-swap 4g \
		-v "$(PWD)":/app:rw \
		dataflow/local

#docker run \
		-it --rm \
		--cpus 1 --cpu-shares 1024 --memory 2g --memory-swap 4g \
		-v "$(PWD)":/app:rw \
		test/local