from django.test import TestCase
from task_router import workspace
from django.conf import settings
import vcr


def scrub_string(string, replacement=''):
    def before_record_response(response):
        current_body = response['body']['string'].decode('utf8')
        fixed_body = current_body.replace(string, replacement)
        response['body']['string'] = fixed_body.encode('utf8')
        return response
    return before_record_response

filtered_vcr = vcr.VCR(
    before_record_response=scrub_string(settings.TWILIO_ACCOUNT_SID, '<account_sid>'),
)


class WorkspaceTests(TestCase):

    @filtered_vcr.use_cassette('fixtures/vcr_create_workspace.yaml',
                               filter_headers=['authorization'])
    def test_setup_creates_a_workspace(self):
        workspace.HOST = 'http://example.com'
        workspace.BOB_NUMBER = '+15005550006'
        workspace.ALICE_NUMBER = '+15005550008'
        workspace_info = workspace.setup()
        self.assertEqual('WWf9d79f9a07d0f0a5460256dbf1cf8dc8',
                         workspace_info.workflow_sid)
        self.assertEqual('WA94672b43ad2fe2101bd6cff3585e082c',
                         workspace_info.activities['Offline'].sid)
        self.assertEqual(workspace_info.activities['Idle'].sid,
                         workspace_info.post_work_activity_sid)
