
pre-commit:
	pre-commit run --all-files

deploy:
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACC_NO}.dkr.ecr.${AWS_REGION}.amazonaws.com
	docker buildx build --platform linux/amd64 -t ${AWS_ACC_NO}.dkr.ecr.${AWS_REGION}.amazonaws.com/timelines:latest -f Dockerfile --push .
	docker pull ${AWS_ACC_NO}.dkr.ecr.${AWS_REGION}.amazonaws.com/timelines:latest
	cd terraform && terraform apply -auto-approve
