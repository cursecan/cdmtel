from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import (
    TemplateView, ListView
)
from tablib import Dataset
from .resources import (
    InputKoreksiResource, ExportKoreksiResource
)
from .models import InputKoreksi


class InputKoreksiTemplateView(TemplateView):
    template_name = 'koreksi/input-koreksi-pg.html'

class InputKoreksiListView(ListView):
    template_name = 'koreksi/input-koreksi-pg.html'
    model = InputKoreksi
    paginate_by = 10

def simple_upload(request):
    if request.method == 'POST':
        person_resource = InputKoreksiResource()
        dataset = Dataset()
        new_persons = request.FILES['myfile']

        imported_data = dataset.load(new_persons.read())
        result = person_resource.import_data(dataset, dry_run=True)  # Test the data import
        
        if not result.has_errors():
            person_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'koreksi/simple-upload-pg.html')


def export(request):
    person_resource = ExportKoreksiResource()
    dataset = person_resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="koreksi.xls"'
    return response