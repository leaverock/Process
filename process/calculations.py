from .models import Scenario, Risk, Expense,Process
import math
from scipy import integrate


#Математическое ожидание риска для времени
def expected_value_time(id):
    result = 0
    scenario = Scenario.objects.filter(risk__id = id)
    for scen in scenario:
        result += scen.probability_scen * scen.impact_time /100

    return result

#Математическое ожидание риска для стоимости
def expected_value_cost(id):
    result = 0
    scenario = Scenario.objects.filter(risk__id = id)
    for scen in scenario:
        result += scen.probability_scen * scen.impact_cost /100

    return result

#среднеквадратическое отклонение риска для времени
def standard_deviation_time(id):
    result = 0
    scenario = Scenario.objects.filter(risk__id = id)
    E = expected_value_time(id)
    for scen in scenario:
        result += scen.probability_scen/100*(scen.impact_time - E)**2
        print(result)
    res = math.sqrt(result)
    return res

#среднеквадратическое отклонение риска для стоимости
def standard_deviation_cost(id):
    result = 0
    scenario = Scenario.objects.filter(risk__id = id)
    E = expected_value_cost(id)
    for scen in scenario:
        result += scen.probability_scen/100*(scen.impact_cost - E)**2
    return math.sqrt(result)

#Математическое ожидание процесса для времени
def expected_process_time(id):
    result = 0
    expense = Expense.objects.get(pk = id)
    risk = Risk.objects.filter(expense__id = id)
    for rsk in risk:
        result += rsk.expected_value
    result += expense.criterion_ind
    print("calc")
    return result
    
#Математическое ожидание процесса для стоимости
def expected_process_cost(id):
    result = 0
    expense = Expense.objects.get(pk = id)
    risk = Risk.objects.filter(expense__id = id)
    for rsk in risk:
        result += rsk.expected_value
    result += expense.criterion_ind
    return result

def sum_risk_for_process(id):
    risk_result_expected_value_time = 0
    risk_result_expected_value_cost = 0
    risk_result_standard_deviation_time = 0
    risk_result_standard_deviation_cost = 0
    process = Process.objects.filter(parent = id)
    if process ==None:
        return 0,0
    else:
        for pr in process:
            expense = Expense.objects.filter(name_process = pr.id).first()
            if expense:
                risk = Risk.objects.filter(expense = expense.id)
                if risk:
                    for rsk in risk:
                        risk_result_expected_value_time += rsk.expected_value_time + sum_risk_for_process(pr.id)[0]
                        risk_result_expected_value_cost += rsk.expected_value_cost + sum_risk_for_process(pr.id)[1]
                        risk_result_standard_deviation_time += rsk.standard_deviation_time + sum_risk_for_process(pr.id)[2]
                        risk_result_standard_deviation_cost += rsk.standard_deviation_cost + sum_risk_for_process(pr.id)[3]
                else:
                    risk_result_expected_value_time += sum_risk_for_process(pr.id)[0]
                    risk_result_expected_value_cost += sum_risk_for_process(pr.id)[1]
                    risk_result_standard_deviation_time += sum_risk_for_process(pr.id)[2]
                    risk_result_standard_deviation_cost += sum_risk_for_process(pr.id)[3]
            else:
                risk_result_expected_value_time += sum_risk_for_process(pr.id)[0]
                risk_result_expected_value_cost += sum_risk_for_process(pr.id)[1]
                risk_result_standard_deviation_time += sum_risk_for_process(pr.id)[2]
                risk_result_standard_deviation_cost += sum_risk_for_process(pr.id)[3]      
        return risk_result_expected_value_time, risk_result_expected_value_cost, risk_result_standard_deviation_time, risk_result_standard_deviation_cost

def summ_all_process(id):
    result_time = 0
    result_cost = 0
    process = Process.objects.filter(parent = id)
    if process ==None:
        return 0,0
    else:
        for pr in process:
            expense = Expense.objects.filter(name_process = pr.id).first()
            if expense:
                result_time += expense.lead_time + summ_all_process(pr.id)[0]
                result_cost += expense.execution_costs + summ_all_process(pr.id)[1]
            else:
                result_time += summ_all_process(pr.id)[0]
                result_cost += summ_all_process(pr.id)[1]
        return result_time, result_cost

#среднеквадратическое отклонение процесса
def devation_indicator(id):
    result = 0
    risk = Risk.objects.filter(indicator__id = id)
    for rsk in risk:
        result += rsk.standard_deviation**2
    return math.sqrt(result)

""" #Математическое ожидание процесс без одного риска
def expected_indicator1(id, risk_id):
    result = 0
    indicator = Indicator.objects.get(pk = id)
    risk = Risk.objects.filter(indicator__id = id).exclude(id = risk_id)
    for rsk in risk:
        result += rsk.expected_value
    result += indicator.criterion_ind
    return result """

#среднеквадратическое отклонение процесса без одного риска
def devation_indicator1(id, risk_id):
    result = 0
    risk = Risk.objects.filter(indicator__id = id).exclude(id = risk_id)
    for rsk in risk:
        result += rsk.standard_deviation**2
    return math.sqrt(result)

#Вероятность реализации
def realization(id):
    result = 0
    scenario = Scenario.objects.filter(risk__id = id)
    for scen in scenario:
        if scen.impact_time != 0 and scen.impact_cost !=0:
            result +=scen.probability_scen

    return result

#гамма(Уровень сигма)
def gamma(l,u,q):
    x = l-u
    return x/q

#Вероятность выхода показателя за крит. знач
def probability(sigma):
    return 1 - normalvariate(sigma-1.5)

#Стандартное нормальное распределение
def normalvariate(y):
    return 1/math.sqrt(2*math.pi) * integrate.quad(f,-math.inf,y)[0]

#Функция для интегралла при расчете ст. норм. распределения
def f(x):
    return math.e**(-(x**2/2))