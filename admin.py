from django.contrib import admin
from roadmap.models import Organisation, Report, Period, Checkin, Mark, Value, Constant, ConstVal


class MarkAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super(MarkAdmin, self).save_related(request, form, formsets, change)
        form.instance.affect.clear()

        if (change and form.instance.formula):
            mark_variable_list = form.instance.pattern.findall(form.instance.formula)
            for mark_variable in mark_variable_list:
                mark_affect = Mark.objects.get( number=mark_variable )
                form.instance.affect.add( mark_affect )


admin.site.register(Organisation)
admin.site.register(Report)
admin.site.register(Period)
admin.site.register(Checkin)
admin.site.register(Mark, MarkAdmin)
admin.site.register(Value)
admin.site.register(Constant)
admin.site.register(ConstVal)
