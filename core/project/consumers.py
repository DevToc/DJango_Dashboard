import json
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer
from django.shortcuts import get_object_or_404
from core.project.models import Project


class ProjectConsumer(WebsocketConsumer):
    def connect(self):
        self.id = self.scope.get("url_route").get("kwargs").get("project_id")
        userId = self.scope.get("url_route").get("kwargs").get("user_id")
        self.userId = userId
        print("%%%%%%%%% Connecting project", self.id, "userid", userId)
        if self.id:
            project = get_object_or_404(Project, pk=self.id)
            project.is_viewing = True
            project.is_viewing_user_id = self.userId
            project.save()
        self.accept()

    def disconnect(self, close_code):
        self.id = self.scope.get("url_route").get("kwargs").get("project_id")
        print("%%%%%%%%% Disconnecting project", self.id)

        if self.id:
            project = get_object_or_404(Project, pk=self.id)
            project.is_viewing = False
            project.is_viewing_user = None
            project.save()
        #raise StopConsumer()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
