from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Process,Unit,Expense,Indicator, MemberProcess, Risk,EventModels, Position, Group_process, Scenario

admin.site.register(Process,MPTTModelAdmin)
admin.site.register(Unit)
admin.site.register(Expense)
admin.site.register(Indicator)
admin.site.register(MemberProcess)
admin.site.register(Risk)
admin.site.register(EventModels)
admin.site.register(Position)
admin.site.register(Group_process)
admin.site.register(Scenario)

