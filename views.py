from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
import json
from roadmap.models import Organisation, Mark, Report, Period, Value


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


def organisation_load(request, report_id, period_id, organisation_id):
    value_list = Value.objects.filter(report=report_id, period=period_id, organisation=organisation_id).order_by('mark__number')
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


def organisation_save(request, report_id, period_id, organisation_id):
    post_data = request.POST.get('data', False)
    try:
        marks = json.loads(post_data)
    except TypeError:
        return JsonResponse({'result':'false'})
    else:
        for mark in marks['data']:
            try:
                selected_value = Value.objects.get(pk=mark['id'])
            except (KeyError, Value.DoesNotExist):
                return JsonResponse({'result':'false'})
            else:
                for i in ['fact','check','plan']:
                    if (mark[i]==''):
                        mark[i]=None
                selected_value.fact = mark['fact']
                selected_value.check = mark['check']
                selected_value.plan = mark['plan']
                selected_value.save()

    return JsonResponse({'result':'ok'})


def mark(request, report_id, period_id, mark_id):
    report = get_object_or_404(Report, pk=report_id)
    period = get_object_or_404(Period, pk=period_id)
    mark = get_object_or_404(Mark, pk=mark_id)
    return render(request, 'roadmap/mark.html', {'report': report, 'period': period, 'mark': mark})


def mark_load(request, report_id, period_id, mark_id):
    value_list = Value.objects.filter(report=report_id, period=period_id, mark=mark_id).order_by('organisation__number')
    output = list()
    for value in value_list:
        output.append({
            'id':               value.id,
            'organisation':     value.organisation.name_short,
            'fact':             value.fact,
            'check':            value.check,
            'plan':             value.plan
        })
    data = {'data': output}
    return JsonResponse(data)


def mark_save(request, report_id, period_id, mark_id):
    post_data = request.POST.get('data', False)
    try:
        organisations = json.loads(post_data)
    except TypeError:
        return JsonResponse({'result':'false'})
    else:
        for organisation in organisations['data']:
            try:
                selected_value = Value.objects.get(pk=organisation['id'])
            except (KeyError, Value.DoesNotExist):
                return JsonResponse({'result':'false'})
            else:
                for i in ['fact','check','plan']:
                    if (organisation[i]==''):
                        organisation[i]=None
                selected_value.fact = organisation['fact']
                selected_value.check = organisation['check']
                selected_value.plan = organisation['plan']
                selected_value.save()

    return JsonResponse({'result':'ok'})