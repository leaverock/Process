import time

from django.conf import settings


# https://habr.com/ru/post/62844/
# https://stackoverflow.com/questions/17901341/django-how-to-make-a-variable-available-to-all-templates
# К каждому static файлу нужно добавить "{{cache_key}}",
# чтобы заставлять браузер загружать новую версию static файлов при перезапуске сервера

def cache_key(request):
    cache = str(int(time.time()))
    return {'cache_key': '?' + cache}