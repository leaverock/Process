#region impotrt
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.list import ListView
from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from . import calculations
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Process, MemberProcess, Expense, Indicator, Member, Risk, EventModels, Position, Group_process, Scenario
from .forms import *
import mptt
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import math
from io import BytesIO
import base64
from scipy.stats import norm
import xlwt


#endregion

#region основные окна
def getid(requset, id):
    requset.session['PrId']= id
    return redirect('info')

#вкладка "Общая информация"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class ProcessView(View):
    def get(self, request):
        try:
            PrID = request.session['PrId']
            process = Process.objects.get(id = PrID)
            children_process = process.get_children()
        except:
            process = Process.objects.all()
        return render(request,'process/info.html', context={'process':process, "children":children_process})

#вкладка "Участники"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class Memberview(View):
    def get(self,request):
        position = Position.objects.all().order_by('position')
        PrID = request.session['PrId']
        process = Process.objects.filter(id = PrID)
        member = MemberProcess.objects.filter(proces = PrID).order_by('proces__id', 'position__position')
        
        return render(request,'process/members.html', context={'memberprocess':member, 'process':process, 'position':position})

#вкладка "Спецификация"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class SpecificationView(View):
    def get(self,request):
        try:
            PrID = request.session['PrId']
            process = Process.objects.get(id = PrID)
            children_process = process.get_children()
        except:
            process = Process.objects.all()
        return render(request,'process/specification.html', context={'process':process,"children":children_process})

    
#вкладка "Затраты"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class ExpensesView(View):

    def get(self,request):
        PrID = request.session['PrId']
        process = Process.objects.get(id = PrID)
        children_process = process.get_children()
        expense = Expense.objects.filter(name_process__in = [proc.id for proc in process])
        children_expense = Expense.objects.get(name_process = children_process)
        return render(request,'process/expenses.html', context={'expense':expense,"children": children_expense})

#вкладка "Показатели"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class IndicatorView(View):
    def get(self,request):
        PrID = request.session['PrId']
        indic = Indicator.objects.filter(name_process__parent = PrID)
        return render(request,'process/indicators.html', context={'indicator':indic})


@login_required(login_url='/process/accounts/login/')
def login(request):
    return render(request, 'login.html',)


#вкладка "Мероприятия"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class EventView(View):
    def get(self,request):
        event = EventModels.objects.all()
        return render(request,'process/event.html', context={'event':event})

#вкладка "Риски"
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class RiskView(View):
    def get (self,request):
        exp = Expense.objects.get(id = int(request.GET.get("expense")))
        rsk = Risk.objects.filter(expense__id = int(request.GET.get("expense")))
        return render(request, 'process/risk.html', context={'risk': rsk,'exp':exp})
#вкладка "Риски"

@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class AllRiskView(View):
    def get (self,request):
        Type = request.session['Type']
        PrID = request.session['PrId']
        if Type == 'g':
            rsk = Risk.objects.filter(expense__name_process__group = PrID)
        elif Type == 'p':
            process = Process.objects.get(id = PrID).get_descendants(include_self=True)
            rsk = Risk.objects.filter(expense__name_process__in = [proc.id for proc in process])
        return render(request, 'process/allrisk.html', context={'risk': rsk})

#Сценарии рисков
@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class ScenarioView(View):   
    def get(self,request, id):
        risk = Risk.objects.get(pk = id)
        scen = Scenario.objects.filter(risk__id = id).order_by('-probability_scen')
        result = 0
        for sc in scen:
            result += sc.probability_scen
        return render(request,'process/scenario.html', context={'risk':risk,'scen':scen,"res": result })

@method_decorator(login_required(login_url='/process/accounts/login/'), name = 'dispatch')
class GraphicView(View):
    def get(self, request):
        PrID = request.session['PrId']
        expense = Expense.objects.get(name_process = PrID)
        expense1 = Expense.objects.get(name_process__base = PrID)
        mu =float(expense.expected_value_time)
        sigma = float(expense.standard_deviation_time)
        muc =float(expense1.expected_value_time)
        sigmac = float(expense1.standard_deviation_time)
        x_axis = np.arange(mu - 5*sigma, mu + 5*sigma, 0.001)
        plt.plot(x_axis, norm.pdf(x_axis,mu,sigma), color = 'k')
        plt.plot(x_axis, norm.pdf(x_axis,muc,sigmac), color = 'g')
        plt.axvline(x=mu,linewidth=2, color='k', linestyle = ":")
        plt.axvline(x=muc,linewidth=2, color='g', linestyle = ":")
        plt.axvline(x=expense.critical_time,linewidth=2, color='r')
        plt.ylabel('Вероятность')
        plt.xlabel('Показатель')
        plt.title("Время")
        plt.legend()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        plt.clf()
        plt.cla()
        mu1 =float(expense.expected_value_cost)
        sigma1 = float(expense.standard_deviation_cost)
        x_axis = np.arange(mu1 - 5*sigma1, mu1 + 5*sigma1, 0.001)
        mu1c =float(expense1.expected_value_cost)
        sigma1c = float(expense1.standard_deviation_cost)
        plt.plot(x_axis, norm.pdf(x_axis,mu1,sigma1), color = 'k')
        plt.plot(x_axis, norm.pdf(x_axis,mu1c,sigma1c), color = 'g')
        plt.axvline(x=mu1,linewidth=2, color='k' , linestyle = ":")
        plt.axvline(x=mu1c,linewidth=2, color='g' , linestyle = ":")
        plt.axvline(x=expense.critical_cost,linewidth=2, color='r')
        plt.ylabel('Вероятность')
        plt.xlabel('Показатель')
        plt.title("Стоимость")
        plt.legend()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic1 = base64.b64encode(image_png)
        graphic1 = graphic1.decode('utf-8')
        plt.clf()
        plt.cla()
        return render(request,'process/graphics.html',{'graphic':graphic,'graphic1':graphic1})


#endregion

#region расчеты
    
#расчеты показателей для рисков    
def calculate(request):
    if request.method == "POST":
        risk = Risk.objects.get(id = request.POST.get("id"))
        risk.expected_value_time = calculations.expected_value_time(risk.id)#математическое ожидание риска для времени
        risk.standard_deviation_time = calculations.standard_deviation_time(risk.id)#среднеквадратическое откланение риска для времени
        risk.expected_value_cost = calculations.expected_value_cost(risk.id)#математическое ожидание риска для стоимости
        risk.standard_deviation_cost = calculations.standard_deviation_cost(risk.id)#среднеквадратическое откланение риска для стоимости
        risk.probability = calculations.realization(risk.id)#вероятность реализации риска
        risk.save()
        # ind = Indicator.objects.get(id = risk.indicator.id)
        # expected_value = calculations.expected_indicator(ind.id)#математическое ожидание прцесса
        # standard_deviation = calculations.devation_indicator(ind.id)#среднеквадратическое отклонение процесса
        # right_critical_value = ind.right_critical_value#правое критическое значение
        # right_sigma = calculations.gamma(right_critical_value,expected_value,standard_deviation)#уровень сигма с права
        # left_critical_value = ind.left_critical_value#левое критическое значение
        # left_sigma = calculations.gamma(left_critical_value,expected_value,standard_deviation)#уровень сигма с лева 
        # ind.left_sigma = left_sigma
        # ind.right_sigma = right_sigma
        # ind.probability = round(calculations.probability(right_sigma, left_sigma)*100,2)# вероятность выхода показателя процесса за крит. значение
        # ind.expected_value = expected_value
        # ind.standard_deviation = standard_deviation
        # rsk = Risk.objects.filter(indicator__id = ind.id)
        # for r in rsk:
        #     expected_value = calculations.expected_indicator1(ind.id, r.id)#математическое ожидание прцесса без расчитываемого риска
        #     standard_deviation = calculations.devation_indicator1(ind.id, r.id)#среднеквадратическое откланение процесса без расчитываемого риска
        #     if standard_deviation !=0:
        #         sigma1 = calculations.gamma(right_critical_value,expected_value,standard_deviation)
        #     else:
        #         sigma1 = 0
        #     deltagamma = sigma1-right_sigma#значимсоть риска
        #     r.significance_risk = deltagamma
        #     r.save()
        # ind.save()

    return HttpResponseRedirect("risk/scen/"+str(request.POST.get("id"))+"/")
""" 
#расчет приоритета для мероприятия
def calculate_preority(request):
    if request.method == "POST":
        event = EventModels.objects.get(name_risk__id = request.POST.get("id")  )
        risk = Risk.objects.get(id = request.POST.get("id"))
        ind = Indicator.objects.get(id = risk.indicator.id)
        risk.expected_value = calculations.expected_value(risk.id)#математическое ожидание риска
        risk.standard_deviation = calculations.standard_deviation(risk.id)#среднеквадратическое откланение риска
        risk.probability = calculations.realization(risk.id)#вероятность реализации риска
        risk.save()
        expected_value = calculations.expected_indicator(ind.id)#математическое ожидание прцесса
        standard_deviation = calculations.devation_indicator(ind.id)#среднеквадратическое откланение процесса
        critical_value = ind.critical_value#критическое значение
        sigma1 = calculations.gamma(critical_value,expected_value,standard_deviation)#уровень сигма измененного показателя
        sigma = ind.sigma#уровень сигма старого показателя
        priority = sigma1-sigma
        event.priority = priority#Приоритет мероприятия
        event.save()
        expected_value = calculations.expected_indicator(ind.id)#математическое ожидание прцесса
        standard_deviation = calculations.devation_indicator(ind.id)#среднеквадратическое отклонение процесса
        right_critical_value = ind.right_critical_value#критическое значение
        right_sigma = calculations.gamma(right_critical_value,expected_value,standard_deviation)#уровень сигма
        left_critical_value = ind.left_critical_value#критическое значение
        left_sigma = calculations.gamma(left_critical_value,expected_value,standard_deviation)#уровень сигма
        ind.sigma = left_sigma
        ind.probability = round(calculations.probability(right_sigma, left_sigma)*100,2)# вероятность выхода показателя процесса за крит. значение
        ind.expected_value = expected_value
        ind.standard_deviation = standard_deviation
        rsk = Risk.objects.filter(indicator__id = ind.id)
        for r in rsk:
            expected_value = calculations.expected_indicator1(ind.id, r.id)#математическое ожидание прцесса без расчитываемого риска
            standard_deviation = calculations.devation_indicator1(ind.id, r.id)#среднеквадратическое откланение процесса без расчитываемого риска
            if standard_deviation !=0:
                sigma1 = calculations.gamma(right_critical_value,expected_value,standard_deviation)
            else:
                sigma1 = 0
            deltagamma = sigma1-right_sigma#значимсоть риска
            r.significance_risk = deltagamma
            r.save()
        ind.save()
    return HttpResponseRedirect("/process/event/")
 """
#Расчитать вероятность выхода показателя процесса за крит. значение 
def calculate_all_risk(request):
    ind = Indicator.objects.get(id = request.POST.get('idind'))
    expected_value = calculations.expected_indicator(ind.id)#математическое ожидание прцесса
    standard_deviation = calculations.devation_indicator(ind.id)#среднеквадратическое отклонение процесса
    right_critical_value = ind.right_critical_value#правое критическое значение
    right_sigma = calculations.gamma(right_critical_value,expected_value,standard_deviation)#уровень сигма с права
    left_critical_value = ind.left_critical_value#левое критическое значение
    left_sigma = calculations.gamma(left_critical_value,expected_value,standard_deviation)#уровень сигма с лева 
    ind.left_sigma = left_sigma
    ind.right_sigma = right_sigma
    ind.probability = round(calculations.probability(right_sigma, left_sigma)*100,2)# вероятность выхода показателя процесса за крит. значение
    ind.expected_value = expected_value
    ind.standard_deviation = standard_deviation
    ind.save()
    return redirect("risk"+'/?indicator='+str(request.POST.get("idind")))

def calculate_all_for_process(request):
    if request.method =="POST":
        id = request.session['PrId']
        process = Process.objects.get(id = id)
        critical_value_time = float(request.POST.get("critical_value_time"))
        critical_value_cost = float(request.POST.get("critical_value_cost"))
        summ = calculations.summ_all_process(process.id)
        sumrisk = calculations.sum_risk_for_process(process.id)
        expense = Expense.objects.filter(name_process = id).first()
        expected_value_with_risk_time = sumrisk[0]+summ[0]
        expected_value_with_risk_cost = sumrisk[1]+summ[1]
        gamma_time = calculations.gamma(critical_value_time,expected_value_with_risk_time,sumrisk[2])
        gamma_cost = calculations.gamma(critical_value_cost,expected_value_with_risk_cost,sumrisk[3])
        probability_time = calculations.probability(gamma_time)*100
        probability_cost = calculations.probability(gamma_cost)*100
        if expense != None:
            expense.delete()
        exp = Expense()
        exp.name_process = process
        exp.name_expense = "Итог"
        exp.lead_time = summ[0]
        exp.execution_costs = summ[1]
        exp.expected_value_time = expected_value_with_risk_time
        exp.expected_value_cost = expected_value_with_risk_cost
        exp.standard_deviation_time = sumrisk[2]
        exp.standard_deviation_cost = sumrisk[3]
        exp.critical_time = critical_value_time
        exp.critical_cost = critical_value_cost
        exp.sigma_time = gamma_time
        exp.sigma_cost = gamma_cost
        exp.probability_time = probability_time
        exp.probability_cost = probability_cost
        exp.save()
        risk = Risk()
        risk.name_risk = "Итог"
        risk.description = "итог по процессу"
        risk.expense = exp
        risk.expected_value_time = sumrisk[0]
        risk.expected_value_cost = sumrisk[1]
        risk.standard_deviation_time = sumrisk[2]
        risk.standard_deviation_cost = sumrisk[3]
        risk.save()
        
        return redirect('expenses')
    else:
        return render(request,'create/add_critical.html',{})



#endregion
#region Мероприятия
#Выбор процесса для проведения меропритий
def choise_process(request):
    process = Process.objects.all()
    return render(request, "create/event/choise_process.html",{'process':process})
#рекурсивный метод для создания копии процесса
def coppy(id, parent = None):
    process = Process.objects.get(pk = id)
    if parent:
        pproc = Process.objects.get(pk = parent)
    else:
        pproc = None
    bproc = Process.objects.get(pk = id)
    new_process = process
    new_process.id = None
    new_process.lft = None
    new_process.rght = None
    new_process.tree_id = None
    new_process.level = None
    new_process.parent = pproc
    new_process.base = bproc
    new_process.name += "*"
    new_process.save()
    expenses = Expense.objects.filter(name_process = bproc)
    for exp in expenses:
        risk = Risk.objects.filter(expense = exp)
        exp.pk = None
        exp.name_process = new_process
        exp.save()
        for rsk in risk:
            scenario = Scenario.objects.filter(risk = rsk)
            rsk.pk = None
            rsk.expense = exp
            rsk.save()
            for scn in scenario:
                scn.pk = None
                scn.risk = rsk
                scn.save()
    indicator = Indicator.objects.filter(name_process = bproc)
    for ind in indicator:
        ind.pk = None
        ind.name_process = new_process
        ind.save()
    proc = Process.objects.get(id = id).get_children()
    for pr in proc:
        coppy(pr.id, new_process.id)
#создание копии процесса
def coppy_process(request):
    coppy(request.GET.get('process'))
    return redirect("choise_expense"+'/?process='+str(request.GET.get("process")))

#Выбор затраты для меропрития
def choise_expense(request):
    process = Process.objects.filter(base = request.GET.get('process')).latest("id").get_descendants(include_self=True)
    expense = Expense.objects.filter(name_process__in = [proc.id for proc in process])
    return render(request,'create/event/choise_expense.html', context={'expense':expense})

#Создание Мероприятия
def add_event(request):
    expense = request.GET.get("expense")
    if request.method == "POST":
        form = AddEvent(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.expense = Expense.objects.get(id  = expense) 
            event.save()  
            return redirect("change_expense", expense)
                 
    else:
        form = AddEvent()
    return render(request, "create/event/addevent.html",{'form':form})

def change_expense(request, id):
    expence = get_object_or_404(Expense,id= id)
    if request.method == "POST":
        form = AddExpense(request.POST, instance=expence)
        if form.is_valid():
            expence = form.save()
            expence.save()
            return redirect('risk_event', id)
    else:
        form = AddExpense(instance=expence)
    return render(request, "create/event/change_expense.html",{'form':form})

def risk_event(request, id):
    exp = Expense.objects.get(id = id)
    rsk = Risk.objects.filter(expense__id = id)
    return render(request, 'create/event/event_risk.html', context={'risk': rsk,'exp':exp})

#Редактирование сценария при создании мерроприятия
def edit_scen_event(request, id):
    scen = get_object_or_404(Scenario, id = id)
    if request.method == "POST":
        form = AddScenario(request.POST, instance=scen)
        if form.is_valid():
            scenar = form.save(commit=False)
            scenar.save()  
            return HttpResponseRedirect("/process/addevent/editscen/"+str(scen.risk.id)+"/")
    else:
        form = AddScenario(instance=scen)
    return render(request, "edit/edit_scenario.html",{'form':form})
#endregion
#region добавление
#Форма добавления процесса
def add_process(request):
    if request.method == "POST":
        form = Addprocess(request.POST)
        if form.is_valid():
            process = form.save(commit=False)
            process.save()
            request.session['ProcessID'] = process.id
            return redirect('addmember')
    else:
        form = Addprocess()
    return render(request, "create/addprocess.html",{'form':form})

#Форма добавления ответсвтенных лиц на матрицу ответственности
def add_memeber(request):
    if request.method == "POST":
        form = AddMember(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.proces = Process.objects.get(id=request.session['ProcessID'])
            member.save()
            if 'save' in request.POST:
                return redirect('addexpence')
            elif 'save-other' in request.POST:
                return redirect('addmember')
    else:
        form = AddMember()
    return render(request, "create/addmember.html",{'form':form})

#Форма добавления затрат
def add_expense(request):
    if request.method == "POST":
        form = AddExpense(request.POST)
        if form.is_valid():
            expence = form.save(commit=False)
            expence.name_process = Process.objects.get(id=request.session['ProcessID']) 
            expence.save()
            if 'save' in request.POST:
                return redirect('addindicator')
            elif 'save-other' in request.POST:
                return redirect('addexpence')
    else:
        form = AddExpense()
    return render(request, "create/addexpence.html",{'form':form})

#Форма добавления показателя
def add_indicator(request):
    if request.method == "POST":
        form = AddIndicator(request.POST)
        if form.is_valid():
            indicator = form.save(commit=False)
            indicator.name_process = Process.objects.get(id=request.session['ProcessID'])
            ind = Indicator.objects.filter(name_process__id = request.session['ProcessID']) 
            indicator.save()
            if 'save' in request.POST:
                return redirect('info')
            elif 'save-other' in request.POST:
                return redirect('addindicator')
            elif 'exit' in request.POST:
                return redirect('indicator')
    else:
        form = AddIndicator()
        ind = Indicator.objects.filter(name_process__id = request.session['ProcessID']) 
    return render(request, "create/addindicator.html",{'form':form, 'indicator':ind})

#Создание риска
def create_risk(request):
    if request.method == "POST":
        risk = Risk()
        risk.direction = request.POST.get("direction_inpt")
        risk.name_risk = request.POST.get("name_risk_inpt")
        risk.description = request.POST.get("description_inpt")
        risk.owner = request.POST.get("owner_inpt")
        risk.expense = Expense.objects.get(id = request.POST.get("expid"))
        risk.save()
        return HttpResponseRedirect("risk/scen/"+str(risk.pk)+"/")

#Создание сценария
def create_scenario(request):
    if request.method == "POST":
        scenario = Scenario()
        scenario.risk = Risk.objects.get(id = request.POST.get("id"))
        scenario.description_scen = request.POST.get("description_scen")
        scenario.probability_scen = request.POST.get("probability_scen")
        scenario.impact_time = request.POST.get("impact_time")
        scenario.impact_cost = request.POST.get("impact_cost")
        scenario.save()
    return HttpResponseRedirect("risk/scen/"+str(request.POST.get("id"))+"/")


#Добавить ед. измерения
def add_unit(request):
    if request.method == "POST":
        form = AddUnit(request.POST)
        if form.is_valid():
            unit = form.save()
            unit.save()  
                 
    else:
        form = AddUnit()
    return render(request, "create/addunit.html",{'form':form})

#Добавить группу
def add_group(request):
    if request.method == "POST":
        form = AddGroup(request.POST)
        if form.is_valid():
            group = form.save()
            group.save()  
                 
    else:
        form = AddGroup()
    return render(request, "create/addgroup.html",{'form':form})

#Добавить должность
def add_position(request):
    if request.method == "POST":
        form = AddPosition(request.POST)
        if form.is_valid():
            unit = form.save()
            unit.save()  
                 
    else:
        form = AddPosition()
    return render(request, "create/addposition.html",{'form':form})

#endregion

#region редактирование
#Редактировать затраты  
def edit_expense(request):
    expence = get_object_or_404(Expense,id= int(request.GET.get("checkedfield")))
    if request.method == "POST":
        form = AddExpense(request.POST, instance=expence)
        if form.is_valid():
            expence = form.save()
            expence.save()
            if 'save' in request.POST:
                return redirect('addindicator')
            elif 'save-other' in request.POST:
                return redirect('addexpence')
    else:
        form = AddExpense(instance=expence)
    return render(request, "edit/editexpence.html",{'form':form})

#Форма редактирования покзател
def edit_indicator(request):
    ind = get_object_or_404(Indicator, id =int(request.GET.get("checkedfield")))
    if request.method == "POST":
        form = AddIndicator(request.POST, instance= ind)
        if form.is_valid():
            indicator = form.save(commit=False)
            indicator.save()
            if 'save' in request.POST:
                return redirect('info')
            elif 'save-other' in request.POST:
                return redirect('addindicator')
            elif 'exit' in request.POST:
                return redirect('indicator')
    else:
        if ind !=None:
            form = AddIndicator(instance= ind)
        else:
            HttpResponse(status = 404)
    return render(request, "edit/editindicator.html",{'form':form})

#Форма редактирования процесса
def edit_proces(request):
    proc = get_object_or_404(Process, pk = int(request.GET.get("checkedfield")))
    if request.method == "POST":
        form = Addprocess(request.POST, instance= proc)
        if form.is_valid():
            process = form.save()
            process.save()
            return redirect('addexpence')
    else:
        if proc !=None:
            form = Addprocess( instance= proc)
        else:
            HttpResponse(status = 404)
        form = Addprocess( instance= proc)
    return render(request, "edit/editprocess.html",{'form':form})

#Редактирование риска при создании мерроприятия
def edit_riskevent(request, id):
    risk = Risk.objects.get(pk = id)
    scen = Scenario.objects.filter(risk__id = id).order_by('-probability_scen')
    result = 0
    for sc in scen:
        result += sc.probability_scen
    return render(request,'process/eventriskedit.html', context={'risk':risk,'scen':scen,"res": result })


#редактировать сценарий
def edit_scen(request):
    scen = get_object_or_404(Scenario, id = request.GET.get('scenario'))
    if request.method == "POST":
        form = AddScenario(request.POST, instance=scen)
        if form.is_valid():
            scenar = form.save(commit=False)
            scenar.save()  
            return HttpResponseRedirect("/process/risk/scen/"+str(scen.risk.id)+"/")
    else:
        form = AddScenario(instance=scen)
    return render(request, "edit/edit_scenario.html",{'form':form})


#endregion
#region функции
#Создание копии процесса
def create_coppy(request):
    process = Process.objects.all()
    context = {}
    if request.method == "GET":            
        process = Process.objects.get(id = int(request.GET.get("checkedfield")))
        bproc = Process.objects.get(pk = int(request.GET.get("checkedfield")))
        new_process = process
        new_process.id = None
        new_process.lft = None
        new_process.rght = None
        new_process.tree_id = None
        new_process.level = None
        new_process.name += "-coppy"
        new_process.base = bproc
        new_process.save()
        expenses = Expense.objects.filter(name_process = process.id)
        indicator = Indicator.objects.filter(name_process = process.id)
        proc = Process.objects.get(id = int(request.GET.get("checkedfield"))).get_children()
        for exp in expenses:
            risk = Risk.objects.filter(expense = exp.id)
            exp.pk = None
            exp.name_process = new_process
            exp.save()
            for rsk in risk:
                rsk.pk = None
                rsk.expense = exp
                rsk.save()
        for ind in indicator:
            ind.pk = None
            ind.name_process = new_process
            ind.save()
        for pr in proc:
            coppy(pr.id, new_process.id)
        PrID = request.session['PrId']
        processes = Process.objects.get(id = PrID).get_descendants(include_self=True)
        context['process'] = processes
    return render(request, 'process/infotable.html', context)
#Удаление процееса
def delete(request):
        process = Process.objects.all()
        context = {}
        if request.method == "GET":            
            process = Process.objects.get(id = int(request.GET.get("checkedfield")))
            process.delete()
            PrID = request.session['PrId']
            processes = Process.objects.get(id = PrID).get_descendants(include_self=True)
            context['process'] = processes
        return render(request, 'process/infotable.html', context)

def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="process.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    description_sheet = wb.add_sheet("Текстовое описание")
    process_sheet = wb.add_sheet('Process')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['','Исходный процесс','Измененный процесс' ]

    for col_num in range(len(columns)):
        process_sheet.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    process = Process.objects.get(id = request.session['PrId'])
    change_process = Process.objects.get(base = process.id)
    expense = Expense.objects.get(name_process = process.id)
    expense_change = Expense.objects.get(name_process = change_process.id)
    rows = [['Стоимость процесса без учета рисков, тыс. руб.', expense.execution_costs,expense_change.execution_costs],
            ['Стоимость процесса с учетом рисков, тыс. руб.', expense.expected_value_cost,expense_change.expected_value_cost],
            ['Вероятность реализации стоимости', expense.probability_cost,expense_change.probability_cost],
            ['Время выполнения процесса без учета рисков, дн.', expense.lead_time,expense_change.lead_time],
            ['Время выполнения процесса с учетом рисков, дн.', expense.expected_value_time,expense_change.expected_value_time],
            ['Вероятность реализации времения', expense.probability_time,expense_change.probability_time],
            ]

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            process_sheet.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
#endregion