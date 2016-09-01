from django.db import models
from roadmap.formula_eval_function import formula_eval
import re


# Организация
class Organisation(models.Model):
    number_full = models.IntegerField(null=True, blank=True)
    name_full = models.CharField(max_length=128)
    number = models.IntegerField(null=True, blank=True)
    name_medium = models.CharField(max_length=128, blank=True)
    name_short = models.CharField(max_length=64)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_full


# Период
class Period(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


# Отчёт
class Report(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Показатель
class Mark(models.Model):
    report = models.ForeignKey(Report)
    number = models.DecimalField(max_digits=6, decimal_places=3)
    point = models.CharField(max_length=6, blank=True)
    name = models.CharField(max_length=256)
    unit = models.CharField(max_length=64, blank=True)
    round = models.IntegerField(default=2)
    formula = models.CharField(max_length=64, blank=True)
    affect = models.ManyToManyField('self', symmetrical=False, blank=True)
    description = models.TextField(blank=True)

    pattern = re.compile('\[(.+?)\]')

    class Meta:
        unique_together = ("report","number")

    def __str__(self):
        return str(self.number) + ": " + str(self.name)


# Значение
class Value(models.Model):
    report = models.ForeignKey(Report)
    period = models.ForeignKey(Period)
    organisation = models.ForeignKey(Organisation)
    mark = models.ForeignKey(Mark)
    fact = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    plan = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    check = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    class Meta:
        unique_together = ("report","period","organisation","mark")

    def __str__(self):
        return str(self.fact) + " (" + str(self.check) + ")" + " / " + str(self.plan)

    def save(self, *args, **kwargs):
        # применим формулу из Показателей
        if self.mark.formula:

            mark_replace_list = self.mark.pattern.findall(self.mark.formula)
            formula = { 'fact':self.mark.formula, 'check': self.mark.formula, 'plan': self.mark.formula }

            for mark_replace in mark_replace_list:
                replace_values = Value.objects.values().get(report = self.report, period = self.period, organisation = self.organisation, mark__number = mark_replace)

                for i in formula:
                    formula[i] = re.sub(
                        r'\['+ mark_replace + '\]',
                        str(replace_values[i]),
                        formula[i]
                    )

            try:
                self.fact = formula_eval(formula['fact'])
            except (ZeroDivisionError, IndexError):
                self.fact = None

            try:
                self.check = formula_eval(formula['check'])
            except (ZeroDivisionError, IndexError):
                self.check = None

            try:
                self.plan = formula_eval(formula['plan'])
            except (ZeroDivisionError, IndexError):
                self.plan = None

        super(Value, self).save(*args, **kwargs)

        # пересчитаем Значения, зависящие от нашего, по Формуле
        affect_mark_list = Mark.objects.filter (affect = self.mark)

        for affect_mark in affect_mark_list:
            affect_value = Value.objects.get(report = self.report, period = self.period, organisation = self.organisation, mark = affect_mark)
            affect_value.save()

        # обновим Итого
        value_list = Value.objects.filter(report=self.report, period=self.period, mark=self.mark).values()
        total = { 'fact': 0, 'check': 0, 'plan': 0 }

        for value in value_list:
            for key, item in total.items():
                if value[key]:
                    total[key] += value[key]

        total_save, created = Total.objects.update_or_create(report=self.report, period=self.period, mark=self.mark, defaults=total)


# Константа
class Constant(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return "{" + str(self.name) + "}: " + str(self.description)


# Значение константы
class CVal(models.Model):
    report = models.ForeignKey(Report)
    period = models.ForeignKey(Period)
    constant = models.ForeignKey(Constant)
    fact = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    class Meta:
        unique_together = ("report","period","constant")

    def __str__(self):
        return str(self.fact)


# Итого
class Total(models.Model):
    report = models.ForeignKey(Report)
    period = models.ForeignKey(Period)
    mark = models.ForeignKey(Mark)
    fact = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    plan = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    check = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)

    class Meta:
        unique_together = ("report","period","mark")

    def __str__(self):
        return str(self.fact) + " (" + str(self.check) + ")" + " / " + str(self.plan)

    def save(self, *args, **kwargs):
        # применим формулу из Показателей
        if self.mark.formula:

            mark_replace_list = self.mark.pattern.findall(self.mark.formula)
            formula = { 'fact':self.mark.formula, 'check': self.mark.formula, 'plan': self.mark.formula }

            for mark_replace in mark_replace_list:
                replace_values = Total.objects.values().get(report = self.report, period = self.period, mark__number = mark_replace)

                for i in formula:
                    formula[i] = re.sub(
                        r'\['+ mark_replace + '\]',
                        str(replace_values[i]),
                        formula[i]
                    )

            try:
                self.fact = formula_eval(formula['fact'])
            except (ZeroDivisionError, IndexError):
                self.fact = None

            try:
                self.check = formula_eval(formula['check'])
            except (ZeroDivisionError, IndexError):
                self.check = None

            try:
                self.plan = formula_eval(formula['plan'])
            except (ZeroDivisionError, IndexError):
                self.plan = None

        super(Total, self).save(*args, **kwargs)

        # пересчитаем Значения, зависящие от нашего, по Формуле
        affect_mark_list = Mark.objects.filter (affect = self.mark)

        for affect_mark in affect_mark_list:
            affect_value = Total.objects.get(report = self.report, period = self.period, mark = affect_mark)
            affect_value.save()
