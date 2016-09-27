import xlsxwriter
from roadmap.models import Organisation, Mark, Report, Period, Checkin, Value, Total


# создание тестового документа xlsx
def create_example(report_id, period_id, organisation_id):
	organisation = Organisation.objects.get(pk=organisation_id)
	period = Period.objects.get(pk=period_id)
	report = Report.objects.get(pk=report_id)

	workbook = xlsxwriter.Workbook(organisation.name + ', ' + period.name + '.xlsx')
	worksheet = workbook.add_worksheet(organisation.name)

	worksheet.set_column(0, 0, 20)
	bold = workbook.add_format({'bold': True})

	# Шапка
	worksheet.write('A1', organisation.name, bold)
	worksheet.write(2, 0, '№п/п', bold)
	worksheet.write(2, 1, 'Наименование показателя', bold)
	worksheet.write(2, 2, 'Факт', bold)
	worksheet.write(2, 3, 'Проверка', bold)
	worksheet.write(2, 4, 'План', bold)
	row = 3

	value_list = Value.objects.filter(checkin__report=report_id, checkin__period=period_id, checkin__organisation=organisation_id).order_by('mark__number')
	
	# Таблица
	for value in value_list:
		col = 0
		worksheet.write(row, col, row-2)
		worksheet.write(row, col+1, value.mark.name)
		worksheet.write(row, col+2, value.fact)
		worksheet.write(row, col+3, value.check)
		worksheet.write(row, col+4, value.plan)
		row += 1


	workbook.close()

	return True
