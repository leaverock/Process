from django import forms
from .models import Process, MemberProcess, Expense,Indicator, EventModels, Group_process, Unit, Position, Scenario

class Addprocess(forms.ModelForm):
    
    class Meta:
        model = Process
        fields = '__all__'
        exclude = ('number',)


class AddExpense(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ('name_expense','lead_time','execution_costs')
        


class AddIndicator(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"
        exclude = ('name_process',)


class AddMember(forms.ModelForm):
    class Meta:
        model = MemberProcess
        fields = "__all__"
        exclude = ('proces',)

class AddScenario(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = "__all__"
        exclude = ('risk',)


class AddEvent(forms.ModelForm):
    
    class Meta:
        model = EventModels
        fields = "__all__"
        exclude = ('priority','expense')


class AddGroup(forms.ModelForm):

    class Meta:
        model = Group_process
        fields = "__all__"

class AddUnit(forms.ModelForm):

    class Meta:
        model = Unit
        fields = "__all__"

class AddPosition(forms.ModelForm):

    class Meta:
        model = Position
        fields = "__all__"
