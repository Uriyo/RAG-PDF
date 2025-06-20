from django.urls import path
from knowledge.views import AskQuestionView, UploadDocumentView

urlpatterns = [
    path("ask-question/", AskQuestionView.as_view(), name="ask-question"),
    path("upload-doc/", UploadDocumentView.as_view(), name="upload-doc"),
] 