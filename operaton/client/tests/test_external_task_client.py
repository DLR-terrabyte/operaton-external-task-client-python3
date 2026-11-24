from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch, MagicMock

from operaton.client.engine_client import ENGINE_LOCAL_BASE_URL
from operaton.client.external_task_client import ExternalTaskClient


class ExternalTaskClientTest(TestCase):

    def test_creation_with_no_debug_config(self):
        client = ExternalTaskClient(1, ENGINE_LOCAL_BASE_URL, {})
        self.assertFalse(client.is_debug)
        self.assertFalse(client.config.get("isDebug"))

    def test_creation_with_debug_config(self):
        client = ExternalTaskClient(1, ENGINE_LOCAL_BASE_URL, {"isDebug": True})
        self.assertTrue(client.is_debug)
        self.assertTrue(client.config.get("isDebug"))

    @patch("operaton.client.external_task_client.requests.post")
    def test_failure_includes_formatted_variables_when_global_variables_set(self, mock_post):
        mock_post.return_value = MagicMock(status_code=HTTPStatus.NO_CONTENT)
        client = ExternalTaskClient(1, ENGINE_LOCAL_BASE_URL, {})

        client.failure(
            task_id="task1",
            error_message="failed",
            error_details="details",
            retries=2,
            retry_timeout=1000,
            global_variables={"var1": 1},
        )

        sent_body = mock_post.call_args.kwargs["json"]
        self.assertIn("variables", sent_body)
        self.assertEqual({"value": 1}, sent_body["variables"]["var1"])

    @patch("operaton.client.external_task_client.requests.post")
    def test_failure_omits_variables_key_when_global_variables_falsy(self, mock_post):
        mock_post.return_value = MagicMock(status_code=HTTPStatus.NO_CONTENT)
        client = ExternalTaskClient(1, ENGINE_LOCAL_BASE_URL, {})

        client.failure(
            task_id="task1",
            error_message="failed",
            error_details="details",
            retries=2,
            retry_timeout=1000,
            global_variables=None,
        )

        sent_body = mock_post.call_args.kwargs["json"]
        self.assertNotIn("variables", sent_body)