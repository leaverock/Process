from django.shortcuts import render_to_response, redirect
from django import template
from process.models import Process, Group_process


register = template.Library()

@register.inclusion_tag('tree.html')
def tree():
    process = Process.objects.all()
    group = Group_process.objects.all()
    return {'nodes':process, 'group':group}