# Pod Chaos Monkey
A simple application that deletes a randomly chosen pod from a given Kubernetes namespace on given schedule

## Pre-requisites
* Install [Docker desktop](https://docs.docker.com/get-docker/)
* A Kubernetes cluster ex. [minikube](https://minikube.sigs.k8s.io/docs/start/)
* Install [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)
* An application running in **workloads** namespace
  * For ex. start an **nginx** deployment with `kubectl apply -f workload`

#### NOTE
[Kubernetes Python client](https://github.com/kubernetes-client/python) is used to access Kube API

## Installation
* Build image with `docker build -t <repository>/pod-chaos-monkey:<tag> .`
* docker login to the repository. For ex. for dockerhub `docker login -u <username> docker.io`
* Push it to your registry `docker push <repository>/pod-chaos-monkey:<tag>`
* Create secret for Docker registry `kubectl create secret generic regcred --from-file=.dockerconfigjson=<path/to/.docker/config.json> --type=kubernetes.io/dockerconfigjson`
  * More info : [Create a secret based on existing credentials](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#registry-secret-existing-credentials)
* Update the image repository, tag and SHA256 in Deployment Yaml (for given environment) `./kustomize/overlay/dev/cronjob.yaml`
* `schedule` field in the cronjob.yaml is used to specify the Cron expression. For ex. `schedule: "* * * * *"` runs a job every minute.
* More info on Cronjobs : 
  * [Running Automated tasks with Cronjobs](https://kubernetes.io/docs/tasks/job/automated-tasks-with-cron-jobs/)
  * [Cron schedule syntax](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#cron-schedule-syntax)
  * [Cronjob example with spec details](https://stackoverflow.com/questions/55510489/avoid-multiple-cron-jobs-running-for-one-cron-execution-point-in-kubernetes/62892617#62892617?newreg=ece92c4da5ca40df957f4337a0ce603a)
* Create namespace `kubectl create ns pod-chaos-monkey`
* Apply Kustomize Yamls (for given environment) `kubectl apply -k ./kustomize/overlay/dev/ `
* Verify the cronjob `kubectl get cronjob -n pod-chaos-monkey`
* Verify the jobs (executed by the cronjob) `kubectl get job -n pod-chaos-monkey`
* Wait for the Pod to become Completed `kubectl get po -n pod-chaos-monkey`
* Check Pod logs `kubectl logs <pod-id> -n pod-chaos-monkey`
* Verify random Pod is getting deleted (based on AGE) in the given namespace `kubectl get po -n workloads` 

Below are pod_chaos_monkey application options (injected as environment variables to the K8s cronjob) :

| Key | Type | Default       | Description                      |
|-----|------|---------------|----------------------------------|
| LOGLEVEL | string | `INFO`      | log verbosity                    |
| NAMESPACE | string | `workloads` | watched namespace                |

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

## License
The MIT License (MIT). Please see [License File](LICENSE) for more information.
