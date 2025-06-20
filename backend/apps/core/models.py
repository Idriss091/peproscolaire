"""
Modèles de base réutilisables
"""
from django.db import models
import uuid


class BaseModel(models.Model):
    """
    Modèle abstrait de base avec champs communs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True