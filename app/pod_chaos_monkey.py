#!/usr/bin/env python

"""
Pod chaos monkey module
"""

import logging
import random
import sys
import os

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException

# Get Environment variables
NAMESPACE = os.getenv("NAMESPACE", "workloads")
LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()

# Setting up the logger
logger = logging.getLogger("pod-chaos-monkey")
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=LOGLEVEL,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Debugging Environment variables
logger.debug("NAMESPACE: %s", NAMESPACE)
logger.debug("LOGLEVEL: %s", LOGLEVEL)


def load_k8s_config():
    """
    Load Kubernetes config
    """
    try:
        config.load_incluster_config()  # To access kube apiserver from within the cluster
    except ConfigException as err:
        logger.error(err)
        sys.exit(1)


def list_pods(api, namespace) -> dict:
    """
    List pods in a single namespace

    :param api: versioned kubernetes api
    :param namespace: namespace
    :return: list of pods
    """
    logger.info("Listing pods in %s namespace", namespace)
    try:
        pod_list = api.list_namespaced_pod(namespace, watch=False).items
        logging.debug(pod_list)
        return pod_list
    except ApiException as err:
        logger.error("Exception occurred when listing Pods : %s", err)
        sys.exit(1)


def delete_random_pod(api, namespace, pod_list):
    """
    Deletes a randomly chosen pod from the input list

    :param api: versioned kubernetes api
    :param namespace: namespace
    :param pod_list: pod list
    :return: None
    """
    if not pod_list:
        logger.info("No pods in %s namespace", namespace)
        return None

    # Select a random pod from the list
    pod = random.choice(pod_list)

    # Deleting the selected pod
    logger.info("Deleting pod %s", pod.metadata.name)
    try:
        api_response = api.delete_namespaced_pod(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace
        )
        logger.debug(api_response)
        logger.info("Pod %s deletion initiated successfully", pod.metadata.name)
        return api_response
    except ApiException as err:
        logger.error("Exception occurred when deleting the Pod : %s", err)
        sys.exit(1)


def main(namespace):
    """
    Delete a random pod from a selected namespace

    :param namespace: Namespace in which delete the Pod
    :return: None
    """
    load_k8s_config()
    v1api = client.CoreV1Api()
    pods = list_pods(v1api, namespace)
    _ = delete_random_pod(v1api, namespace, pods)


if __name__ == '__main__':
    main(NAMESPACE)
