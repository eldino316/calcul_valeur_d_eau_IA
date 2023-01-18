setup:  
	docker build -t waterjug . ; docker run -p 5847:5847 waterjug:latest

test:
	./jugtests
clean:
	IMAGES="$(shell docker image ls -aq)"; docker rmi -f $$IMAGES; find . -name '__pycache__' -exec rm -fr {} +

