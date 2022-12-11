from django import template

from app.models import ResultsImages

register = template.Library()


@register.simple_tag
def get_result_images(result_id):
    return ResultsImages.objects.filter(result_id=result_id)