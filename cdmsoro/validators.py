from django.core.exceptions import ValidationError
import os

def validate_file_size(value):
    filesize = value.size
    if filesize > 1048576:
        raise ValidationError('Max file size 1MB.')
    return value


def validate_file_extension(value):
    allowed_ext = ['.pdf', '.png', '.jpeg', '.jpg', '.gif']
    ext = os.path.splitext(value.name)[1]
    if ext not in allowed_ext:
        raise ValidationError('Extention file must be .pdf .png .gif .jpg .jpeg')
    return value