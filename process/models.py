from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
#region
# Create your models here.
class Event(models.Model):
    name_event = models.CharField(max_length = 200)

    def __str__(self):
        return self.name_event

class Member(models.Model):
    name = models.CharField(max_length = 100)
    position = models.CharField(max_length = 100)

    objects = models.Manager()

    def __str__(self):
        return "{0}({1})".format(self.name,self.position)
#endregion

class Unit(models.Model):
    unit = models.CharField(max_length = 50, verbose_name="Еденица измерения")

    def __str__(self):
        return self.unit

    class Meta:
        verbose_name ="Едениы измерения"
        verbose_name_plural ="Едениы измерения"


class Group_process(models.Model):
    name_group = models.CharField(max_length = 100,verbose_name="Название группы")

    objects = models.Manager()

    def __str__(self):
        return self.name_group

    class Meta:
        verbose_name ="Группы"
        verbose_name_plural ="Группы"

class Process(MPTTModel):
    base = models.ForeignKey('self', on_delete=models.SET_NULL, blank = True, null = True)
    parent = TreeForeignKey('self', on_delete = models.CASCADE, null = True, blank = True, verbose_name="Подпроцесс",related_name='children')
    name = models.CharField(max_length=200,verbose_name="Название процесса")
    start_event = models.CharField(max_length=200, null=True, blank = True,verbose_name="стартовое событие")
    owner = models.CharField( max_length=200, null=True, blank = True,verbose_name="владелец")
    description = models.TextField(null = True, blank = True,verbose_name="описание")
    inpt = models.FileField( blank=True, null=True,verbose_name="Вход")
    outpt = models.FileField( blank=True, null=True,verbose_name="Выход")
    resurce = models.CharField(max_length = 200, null = True, blank = True,verbose_name="Ресурсы")
    isystem = models.CharField(max_length = 200,null = True, blank = True ,verbose_name="И.Системы")
    regulations = models.CharField(max_length = 200, null = True, blank = True,verbose_name="Регламент")
    


    def __str__(self):
        return self.name

    class Meta:
        verbose_name ="Процесс"
        verbose_name_plural ="Процесс"
    
    class MPTTMeta:
        order_insertion_by = ['name']



class Expense(models.Model):
    name_process = models.OneToOneField(Process, on_delete = models.CASCADE, null = False,verbose_name="Процесс")
    name_expense = models.CharField(max_length = 200,verbose_name="название затраты")
    lead_time = models.FloatField(blank = True,verbose_name="Время выпонения(ч)")
    execution_costs = models.FloatField(blank = True,verbose_name="Затраты на выполнение этапа(тыс.руб.)")
    critical_time = models.FloatField(null = True, blank = True,verbose_name="критическая цена")
    critical_cost = models.FloatField(null = True, blank = True,verbose_name="критическая стоимость")
    expected_value_time = models.FloatField(null = True, blank = True,verbose_name="Математическое ожидание времени")
    expected_value_cost = models.FloatField(null = True, blank = True,verbose_name="Математическое ожидание стоимости")
    standard_deviation_time = models.FloatField(null=True, blank=True,verbose_name="Среднеквадратическое отклонение времени")
    standard_deviation_cost = models.FloatField(null=True, blank=True,verbose_name="Среднеквадратическое отклонение стоимости")
    sigma_time = models.FloatField(null=True, blank=True,verbose_name="уровень сигма времени")
    sigma_cost = models.FloatField(null=True, blank=True,verbose_name="уровень сигма стоимости")
    probability_time = models.FloatField(null=True, blank=True,verbose_name="Вероятность выхода показателя процесса за критичское значение времени")
    probability_cost = models.FloatField(null=True, blank=True,verbose_name="Вероятность выхода показателя процесса за критичское значение стоимости")

    objects = models.Manager()

    def __str__(self):
        return "{0}({1})".format(self.name_expense,self.name_process)

    class Meta:
        verbose_name ="Затраты"
        verbose_name_plural ="Затраты"


class Indicator(models.Model):
    name_process = models.ForeignKey(Process , on_delete = models.CASCADE, null = False,verbose_name="Процесс")
    name_indicator = models.CharField(max_length = 200,verbose_name="Название показателя")
    unit = models.ForeignKey(Unit, on_delete = models.SET_NULL, null = True,verbose_name="Единица измерения")
    criterion_ind = models.IntegerField(verbose_name="Критерий результативности")
    method = models.CharField(max_length = 200, null = True, blank = True,verbose_name="Метод расчета")
    

    objects = models.Manager()

    def __str__(self):
        return "{0}({1})".format(self.name_indicator, self.name_process)

    class Meta:
        verbose_name = "Показатель"
        verbose_name_plural = "Показатель"


class Position(models.Model):

    position = models.CharField(max_length = 200,verbose_name="Должность")
    
    objects = models.Manager()

    def __str__(self):
        return  str(self.position)

    class Meta:
        verbose_name="Должность"
        verbose_name_plural="Должность"

class MemberProcess(models.Model):
    
    RESPONSOBILITY_STATUS = (
        ('не учавтвует','не участвует'),
        ('О','Ответственный'),
        ('И' ,'Исполнитель'),
        ('К','консултант'),
        ('Н','наблюдатель')
    )

    proces = models.ForeignKey(Process, on_delete = models.CASCADE, null = False,verbose_name="Процесс")
    position = models.ForeignKey(Position, on_delete = models.CASCADE, null = True,verbose_name="Долнжость")
    responsability = models.CharField(max_length = 20, choices = RESPONSOBILITY_STATUS,verbose_name="Ответсвенность")

    objects = models.Manager()

    def __str__(self):
        return str(self.proces)

    class Meta:
        verbose_name="матрица ответсвенности"
        verbose_name_plural="матрица ответсвенности"



class Risk(models.Model):
    direction = models.CharField(null = True, blank = True, max_length = 200,verbose_name="Направление деятельбности")
    name_risk = models.CharField(max_length = 200,verbose_name="название риска")
    description = models.TextField(verbose_name="описание")
    owner = models.CharField(null = True, blank = True, max_length = 200,verbose_name="Владелец")
    expense = models.ForeignKey(Expense, verbose_name="Название затраты", on_delete=models.CASCADE)
    probability = models.FloatField(null = True, blank=True,verbose_name="Вероятность реализации")
    expected_value_time = models.FloatField(null = True,verbose_name="Математическое ожидание времени")
    expected_value_cost = models.FloatField(null = True,verbose_name="Математическое ожидание стоимости")
    standard_deviation_time = models.FloatField(null = True,verbose_name="Среднеквадратическое отклонение времени")
    standard_deviation_cost = models.FloatField(null = True,verbose_name="Среднеквадратическое отклонение стоимости")
    significance_risk_time = models.CharField(max_length = 200, null = True,verbose_name="значимость риска для времени")
    significance_risk_cost = models.CharField(max_length = 200, null = True,verbose_name="значимость риска для стоимости")

    def get_absolute_url(self):
        return reverse("scenar", args=[str(self.id)])
    

    objects = models.Manager()

    def __str__(self):
        return "{0}({1})".format(self.name_risk, self.expense)

    class Meta:
        verbose_name="Риск"
        verbose_name_plural="Риск"



class Scenario(models.Model):
    risk = models.ForeignKey(Risk, on_delete = models.CASCADE, blank = True,verbose_name="Риск")
    description_scen = models.CharField(max_length = 200, null = True,verbose_name="описание сценария")
    probability_scen = models.FloatField( null = True,verbose_name="Вероятность реализации")
    impact_time = models.FloatField( null = True,verbose_name="Влияние на время")
    impact_cost = models.FloatField( null = True,verbose_name="Влияние на стоимсоть")

    objects = models.Manager()

    def __str__(self):
        return "{0}({1})".format(self.risk.name_risk, self.description_scen)

    class Meta:
        verbose_name="Сценарий"
        verbose_name_plural="Сценарий"


class EventModels(models.Model):
    PEREODOCITY = (
        ('р','разовое'),
        ('и' ,'регулярное'),
    )
    
    expense = models.ForeignKey(Expense, on_delete = models.CASCADE,verbose_name = "Затрата")
    owner = models.CharField(max_length = 150,verbose_name = "Владелец")
    number = models.IntegerField(verbose_name = "Номер")
    name_event = models.CharField(max_length=  200,verbose_name = "Название мероприятия")
    description = models.TextField(verbose_name = "Описание")
    responsible_persons = models.CharField(max_length = 200,verbose_name = "Ответственное лицо")
    periodicity = models.CharField(max_length = 20, choices = PEREODOCITY,verbose_name = "Переодичность")
    critical_date = models.DateField(verbose_name = "Срок выполнения")
    priority = models.FloatField(null=True, blank=True,verbose_name = "Приоритет")

    objects = models.Manager()

    def __str__(self):
        return self.name_event
    
    class Meta:
        verbose_name = "Мероприятия"
        verbose_name_plural = "Мероприятия"
