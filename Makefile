image=rnacentral/rnacentral-import-pipeline
tag=latest
sif=$(tag).sif
docker=$(image):$(tag)

env: requirements.txt requirements-dev.txt

requirements.txt: requirements.in
	pip-compile -o requirements.txt requirements.in

requirements-dev.txt: requirements-dev.in
	pip-compile -o requirements-dev.txt requirements-dev.in

rust:
	cargo build --release
	cp target/release/json2fasta bin
	cp target/release/ena-split bin

docker: Dockerfile requirements.txt .dockerignore
	docker build --build-arg CACHE_DATE="$(date)" -t "$(docker)" .

shell:
	docker run -v `pwd`:/rna/import-pipeline -i -t "$(docker)" bash

publish: docker
	docker push "$(docker)"

.PHONY: docker publish clean env rust
