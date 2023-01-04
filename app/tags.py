
from cleantext import clean
from django import template

from app.models import ResultsImages, Results

register = template.Library()


@register.simple_tag
def get_result_images(result_id):
    return ResultsImages.objects.filter(result_id=result_id)


@register.simple_tag
def update_description(result_id, description):
    description = description.replace('\\r', ' ')
    description = clean(description, extra_spaces=True, numbers=True, punct=True, stp_lang='english')
    Results.objects.filter(id=result_id).update(
        description=description
    )

    return description
