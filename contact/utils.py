import uuid
import os


def generate_image_path(instance, filename):
    model_name = instance.__class__.__name__.lower()
    unique_filename = f"{uuid.uuid4().hex}/{instance.pk}"
    return os.path.join('images', model_name, unique_filename)
