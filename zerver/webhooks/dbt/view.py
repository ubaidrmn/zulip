from django.http import HttpRequest, HttpResponse

from zerver.decorator import webhook_view
from zerver.lib.response import json_success
from zerver.lib.typed_endpoint import JsonBodyPayload, typed_endpoint
from zerver.lib.validator import WildValue, check_string
from zerver.lib.webhooks.common import check_send_webhook_message
from zerver.models import UserProfile


DBT_EVENT_STATUS_EMOJI_MAPPER = {
    "job.run.started": ":yellow_circle:",
    "job.run.completed": ":green_circle:",
    "job.run.errored": ":red_circle:",
}

def extract_data_from_payload(payload: JsonBodyPayload[WildValue]) -> dict[str, str]:
    data: dict[str, str] = {
        "event_type": payload["eventType"].tame(check_string),
        "job_run_id": payload["data"]["runId"].tame(check_string),
        "job_id": payload["data"]["jobId"].tame(check_string),
        "job_run_status": payload["data"]["runStatus"].tame(check_string),
        "job_name": payload["data"]["jobName"].tame(check_string),
        "project_name": payload["data"]["projectName"].tame(check_string),
        "environment_name": payload["data"]["environmentName"].tame(check_string),
        "run_reason": payload["data"]["runReason"].tame(check_string),
        "started_at": payload["data"]["runStartedAt"].tame(check_string),
    }
    errored_at = payload["data"].get("runErroredAt")
    finished_at = payload["data"].get("runFinishedAt")
    if errored_at:
        data["errored_at"] = errored_at.tame(check_string)
    elif finished_at:
        data["finished_at"] = finished_at.tame(check_string)
    return data


def get_job_run_body(data: dict[str, str]) -> str:
    template = """{status_emoji} DBT Job Update for {project_name}

**Job:** {job_name}
**Job ID:** {job_id}
**Run ID:** {job_run_id}
**Environment:** {environment_name}
**Status:** {job_run_status}
**Run Reason:** {run_reason}
**Started at:** {started_at}"""
    body = template.format(status_emoji=DBT_EVENT_STATUS_EMOJI_MAPPER[data["event_type"]], **data)
    if data.get("errored_at"):
        body += f"\n**Failed at**: {data['errored_at']}"
    elif data.get("finished_at"):
        body += f"\n**Finished at**: {data['finished_at']}"
    return body


@webhook_view("DBT")
@typed_endpoint
def api_dbt_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    *,
    payload: JsonBodyPayload[WildValue],
) -> HttpResponse:
    data = extract_data_from_payload(payload)
    body = get_job_run_body(data)
    topic_name = data["project_name"]
    check_send_webhook_message(request, user_profile, topic_name, body)
    return json_success(request)
