from typing_extensions import override

from zerver.lib.test_classes import WebhookTestCase


class DBTHookTests(WebhookTestCase):
    CHANNEL_NAME = "DBT"
    URL_TEMPLATE = "/api/v1/external/dbt?&api_key={api_key}&stream={stream}"
    WEBHOOK_DIR_NAME = "dbt"

    def test_dbt_webhook_when_job_started(self) -> None:
        expected_message = """:yellow_circle: DBT Job Update for Snowflake Github Demo

**Job:** Daily Job (dbt build)
**Job ID:** 123
**Run ID:** 12345
**Environment:** Production
**Status:** Running
**Run Reason:** Kicked off from UI by test@test.com
**Started at:** 2023-01-31T19:28:07Z"""
        self.check_webhook("job_run_started", "Snowflake Github Demo", expected_message)

    def test_dbt_webhook_when_job_completed(self) -> None:
        expected_message = """:green_circle: DBT Job Update for Snowflake Github Demo

**Job:** Daily Job (dbt build)
**Job ID:** 123
**Run ID:** 12345
**Environment:** Production
**Status:** Success
**Run Reason:** Kicked off from UI by test@test.com
**Started at:** 2023-01-31T19:28:07Z
**Finished at**: 2023-01-31T19:29:32Z"""
        self.check_webhook("job_run_completed", "Snowflake Github Demo", expected_message)

    def test_dbt_webhook_when_job_errored(self) -> None:
        expected_message = """:red_circle: DBT Job Update for Snowflake Github Demo

**Job:** dbt Vault
**Job ID:** 123
**Run ID:** 12345
**Environment:** dbt Vault Demo
**Status:** Errored
**Run Reason:** Kicked off from UI by test@test.com
**Started at:** 2023-01-31T21:14:41Z
**Failed at**: 2023-01-31T21:15:20Z"""
        self.check_webhook("job_run_errored", "Snowflake Github Demo", expected_message)
