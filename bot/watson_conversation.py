from watson_developer_cloud import AssistantV1


class WatsonConversation(object):

    def __init__(self):
        self.assistant = AssistantV1(version='2018-08-01',
                        url='https://gateway.watsonplatform.net/assistant/api',
                        iam_apikey='no_9KcvcLhlKT8j4tb2q_OBYDP3EqNhyrVqnh-kre_Iv')

    def get_watson_message(self, user_text):
        response = self.assistant.list_workspaces(headers={'Custom-Header': 'custom_value'})
        workspace_id = response.get_result()['workspaces'][0]['workspace_id']
        return self.assistant.message(workspace_id=workspace_id, input={ 'text': user_text}).get_result()