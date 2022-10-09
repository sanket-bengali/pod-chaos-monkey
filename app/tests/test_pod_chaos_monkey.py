"""
Unit tests for pod_chaos_monkey module
"""
import unittest
from unittest.mock import MagicMock, patch

from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException
from ..pod_chaos_monkey import load_k8s_config, list_pods, delete_random_pod, main


class TestPodChaosMonkey(unittest.TestCase):
    """
    Test class for Pod Chaos Monkey module
    """

    def setUp(self) -> None:
        """
        Set global params used by multiple test-cases
        """
        global NAMESPACE, POD1, POD2, POD3, ITEMS

        NAMESPACE = "my_dummy_ns"

        POD1 = MagicMock()
        POD1.metadata.name = "pod-1"
        POD1.metadata.namespace = NAMESPACE

        POD2 = MagicMock()
        POD2.metadata.name = "pod-2"
        POD2.metadata.namespace = NAMESPACE

        POD3 = MagicMock()
        POD3.metadata.name = "pod-3"
        POD3.metadata.namespace = NAMESPACE

        ITEMS = [POD1, POD2, POD3]


    @patch('kubernetes.config.load_incluster_config')
    def test_load_k8s_config_throws_exception(self, mock_config):
        """
        Unit test for load_k8s_config function to verify exception

        :param mock_config: mocked kube config
        """
        mock_config.side_effect = ConfigException("Config exception")

        with self.assertRaises(SystemExit) as system_exit:
            load_k8s_config()
        self.assertEqual(system_exit.exception.code, 1)


    @patch("kubernetes.client.api.core_v1_api.CoreV1Api")
    def test_list_pods(self, mock_api):
        """
        Unit test for list_pods function

        :param api: mocked API version client
        """
        mock_api.list_namespaced_pod(NAMESPACE, watch=False).items = ITEMS

        pods_list = list_pods(mock_api, NAMESPACE)

        assert pods_list == ITEMS


    @patch("kubernetes.client.api.core_v1_api.CoreV1Api")
    def test_list_pods_throws_exception(self, mock_api):
        """
        Unit test for list_pods function to verify exception

        :param api: mocked API version client
        """
        mock_api.list_namespaced_pod.side_effect = ApiException("Api exception")

        with self.assertRaises(SystemExit) as system_exit:
            list_pods(mock_api, NAMESPACE)
        self.assertEqual(system_exit.exception.code, 1)


    @patch("random.choice")
    @patch("kubernetes.client.api.core_v1_api.CoreV1Api")
    def test_delete_random_pod(self, mock_api, mock_choice_mock):
        """
        Unit test for delete_random_pod function

        :param api: mocked API version client
        :param choice_mock: mocked choice to simulate random.choice
        """
        mock_choice_mock.return_value = POD2

        _ = delete_random_pod(mock_api, NAMESPACE, ITEMS)

        assert mock_api.delete_namespaced_pod.call_count == 1
        mock_api.delete_namespaced_pod.assert_called_with(
            name=POD2.metadata.name,
            namespace=POD2.metadata.namespace
        )


    @patch("kubernetes.client.api.core_v1_api.CoreV1Api")
    def test_delete_random_pod_with_empty_list(self, mock_api):
        """
        Unit test for delete_random_pod function with empty list

        :param api: mocked API version client
        """
        _ = delete_random_pod(mock_api, NAMESPACE, [])

        assert mock_api.delete_namespaced_pod.call_count == 0
        assert _ is None


    @patch("kubernetes.client.api.core_v1_api.CoreV1Api")
    def test_delete_random_pod_throws_exception(self, mock_api):
        """
        Unit test for delete_random_pod function to verify exception

        :param api: mocked API version client
        """
        mock_api.delete_namespaced_pod.side_effect = ApiException("Api exception")

        with self.assertRaises(SystemExit) as system_exit:
            delete_random_pod(mock_api, NAMESPACE, ITEMS)
        self.assertEqual(system_exit.exception.code, 1)


    @patch('kubernetes.client.CoreV1Api')
    @patch('app.pod_chaos_monkey.load_k8s_config')
    def test_main(self, mock_config, mock_api):
        """
        Unit test for main function

        :param mock_config: mocked kube config
        :param mock_v1api: mocked API version client
        """
        mock_config.return_value = MagicMock()
        mock_api.return_value = MagicMock()

        main(NAMESPACE)
        assert mock_config.call_count == 1
        assert mock_api.call_count == 1


if __name__ == '__main__':
    main("my_dummy_ns")
