from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
import json
from roadmap.models import Organisation, Mark, Report, Period, Checkin, Value, Total


def index(request):
    period_list = Period.objects.all()
    report_list = Report.objects.all()
    organisation_list = Organisation.objects.order_by('number')
    mark_list = Mark.objects.order_by('number')
    context = {
        'period_list': period_list,
        'report_list': report_list,
        'organisation_list': organisation_list,
        'mark_list': mark_list }
    return render(request, 'roadmap/index.html', context)


def organisation(request, report_id, period_id, organisation_id):
    report = get_object_or_404(Report, pk=report_id)
    period = get_object_or_404(Period, pk=period_id)
    organisation = get_object_or_404(Organisation, pk=organisation_id)
    return render(request, 'roadmap/organisation.html', {'report': report, 'period': period, 'organisation': organisation})


# все показатели данной организации за период
def organisation_load(request, report_id, period_id, organisation_id):
    value_list = Value.objects.filter(checkin__report=report_id, checkin__period=period_id, checkin__organisation=organisation_id).order_by('mark__number')
    output = list()
    for value in value_list:
        output.append({
            'id':       value.id,
            'point':    value.mark.point,
            'mark':     value.mark.name,
            'fact':     value.fact,
            'check':    value.check,
            'plan':     value.plan
        })
    data = {'data': output}
    return JsonResponse(data)


def mark(request, report_id, period_id, mark_id):
    report = get_object_or_404(Report, pk=report_id)
    period = get_object_or_404(Period, pk=period_id)
    mark = get_object_or_404(Mark, pk=mark_id)
    return render(request, 'roadmap/mark.html', {'report': report, 'period': period, 'mark': mark})


# все организации с данным показателем за период
def mark_load(request, report_id, period_id, mark_id):
    value_list = Value.objects.filter(checkin__report=report_id, checkin__period=period_id, mark=mark_id).order_by('checkin__organisation__number')
    output = list()
    for value in value_list:
        output.append({
            'id':               value.id,
            'organisation':     value.checkin.organisation.name_short,
            'fact':             value.fact,
            'check':            value.check,
            'plan':             value.plan
        })
    total = Total.objects.get(report=report_id, period=period_id, mark=mark_id)
    output.append({
        'id':               '',
        'organisation':     'Итого',
        'fact':             total.fact,
        'check':            total.check,
        'plan':             total.plan
    })
    data = {'data': output}
    return JsonResponse(data)


def value_save(request):
    post_data = request.POST.get('data', False)
    try:
        values = json.loads(post_data)
    except TypeError:
        return JsonResponse({'result':'false'})
    else:
        for value in values['data']:
            if (value['id']):
                try:
                    selected_value = Value.objects.get(pk=value['id'])
                except (KeyError, Value.DoesNotExist):
                    return JsonResponse({'result':'false'})
                else:
                    try:
                        value['fact']
                    except KeyError:
                        pass
                    else:
                        selected_value.fact = value['fact']
                        selected_value.save()

                    try:
                        value['check']
                    except KeyError:
                        pass
                    else:
                        selected_value.check = value['check']
                        selected_value.save()

                    try:
                        value['plan']
                    except KeyError:
                        pass
                    else:
                        selected_value.plan = value['plan']
                        selected_value.save()

    return JsonResponse({'result':'ok'})
