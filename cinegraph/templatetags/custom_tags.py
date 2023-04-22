from django import template

register = template.Library()


register = template.Library()


register = template.Library()


@register.filter
def department_filter(crew, department_name):
    filtered_crew = [
        person for person in crew if person.department == department_name]
    if filtered_crew:
        return {'department_name': department_name, 'filtered_crew': filtered_crew}
    return None
