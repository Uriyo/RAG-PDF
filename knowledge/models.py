from django.db import models


class Document(models.Model):
    """Represents an uploaded knowledge source file."""

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title 