# Pod Chaos Monkey
Deletes a randomly chosen pod from a given Kubernetes cluster namespace on given schedule

## Pre-requisites
* A Kubernetes cluster
  * For ex. minikube (https://minikube.sigs.k8s.io/docs/start/)
* An application in **workloads** namespace
  * start a **nginx** deployment with `kubectl apply -f workload`

#### NOTE
Kubernetes Python client is used : https://github.com/kubernetes-client/python 

## Installation
* Build image with `docker build -t <repository>/pod-chaos-monkey:<tag> .`
* docker login to the repository. For ex. for dockerhub `docker login -u <username> docker.io`
* Push it to your registry `docker push <repository>/pod-chaos-monkey:<tag>`
* Update the image repository, tag and SHA256 in Deployment Yaml (for given environment) `./kustomize/overlay/dev/cronjob.yaml`
* `schedule` field in the cronjob.yaml is used to specify the Cron expression. For ex. `schedule: "* * * * *"` runs a job every minute.
* More info : https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#cron-schedule-syntax
* Create namespace `kubectl create ns pod-chaos-monkey`
* Apply Kustomize Yamls (for given environment) `kubectl apply -k ./kustomize/overlay/dev/ `
* Verify the cronjob `kubectl get cronjob -n pod-chaos-monkey`
* Verify the jobs (executed by the cronjob) `kubectl get job -n pod-chaos-monkey`
* Wait for the Pod to become Running `kubectl get po -n pod-chaos-monkey`
* Check Pod logs `kubectl logs <pod-id> -n pod-chaos-monkey`

Below are pod_chaos_monkey application options (injected as environment variables to the K8s cronjob) :

| Key | Type | Default       | Description                      |
|-----|------|---------------|----------------------------------|
| config.loglevel | string | `"info"`      | log verbosity                    |
| config.namespace | string | `"workloads"` | watched namespace                |

## Run tests and linter

### Unit tests
* Install **coverage** with `pip install coverage`
* Run unittests with coverage `python -m coverage run --source=app/ -m unittest discover`
* Generate unit tests coverage report `python -m coverage report --fail-under=90 --rcfile=./.coveragerc` 
* Write coverage to XML report `python -m coverage xml -o ./coverage.xml --rcfile=./.coveragerc`

### Linter
* Install **pylint** with `pip install pylint`
* Run linter with `python -m pylint ./app`

## Future Improvements
Implement CI/CD pipeline (using Jenkins or similar) which includes :
* Python Code scan (with Sonarqube or similar)
* Docker image scan for vulnerabilities (Ex. 'docker scan' to run Snyk tests)
* Unit tests and coverage
* Pylint
* Kustomization deployment
