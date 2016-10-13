from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse, get_script_prefix
from roadmap.models import Organisation, Mark, Report, Period, Checkin, Value, Total
import json
from roadmap import create_reports


def index(request):
    report_list = set()
    dict_to_pass = {}
    for ch in Checkin.objects.all():
        report_list.add(ch.report)
    for report in report_list:
        period_list = set()
        for ch in Checkin.objects.filter(report=report):
            period_list.add(ch.period)
        dict_to_pass[report] = period_list
    print(dict_to_pass)
    context = {
        'dict_to_pass': dict_to_pass
        }
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


# создание xlsx файла
def report_create(request):
    post_data = request.POST.get('data', False)
    try:
        values = json.loads(post_data)
    except TypeError:
        return JsonResponse({'result':'false'})
    else:
        if create_reports.create_example(values['report'], values['period'], values['organisation']):
            return JsonResponse({'result':'ok'})
        else:
            return JsonResponse({'result':'false'})


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
            'organisation':     value.checkin.organisation.name,
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
        for value in values:
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
                        selected_value.fact = value['fact'] if value['fact'] != '' else None
                        selected_value.save()

                    try:
                        value['check']
                    except KeyError:
                        pass
                    else:
                        selected_value.check = value['check'] if value['check'] != '' else None
                        selected_value.save()

                    try:
                        value['plan']
                    except KeyError:
                        pass
                    else:
                        selected_value.plan = value['plan'] if value['plan'] != '' else None
                        selected_value.save()

    return JsonResponse({'result':'ok'})


def checkin(request, report_id, period_id):
    report = get_object_or_404(Report, pk=report_id)
    period = get_object_or_404(Period, pk=period_id)
    return render(request, 'roadmap/checkin.html', {'report': report, 'period': period})


def checkin_load(request, report_id, period_id):
    checkin_list = Checkin.objects.filter(report=report_id, period=period_id)
    mark_list = Mark.objects.filter(report=report_id).order_by('number')
    output = list()
    outputline = list()
    # формирование шапки таблицы
    outputline.append('')
    for mark in mark_list:
        outputline.append('<a href = "' + reverse('roadmap:mark', kwargs={'report_id':report_id, 'period_id':period_id, 'mark_id':mark.id}) + '">' + str(mark.number) + '</a>')
    output.append(outputline)
    # странная сторчка, чтобы не затиралось в outputline
    outputline = [1, 2]
    for checkin in checkin_list:
        outputline.clear()
        outputline.append('<a href = "' + reverse(
            'roadmap:organisation', kwargs={'report_id':report_id, 'period_id':period_id, 'organisation_id':checkin.organisation.id}) + '">' + checkin.organisation.name + '</a>')
        for mark in mark_list:
            value = Value.objects.get(checkin=checkin,mark=mark)
            outputline.append(str(value.fact))
        output.append(outputline)
        outputline = [1, 2]
    data = {'data': output}
    return JsonResponse(data)
