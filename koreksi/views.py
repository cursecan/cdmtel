from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import (
    TemplateView, ListView
)
from tablib import Dataset
from .resources import (
    InputKoreksiResource, ExportKoreksiResource
)
from .models import (
    InputKoreksi, DocumentImportTemplate,
)


class InputKoreksiTemplateView(TemplateView):
    template_name = 'koreksi/input-koreksi-pg.html'

class InputKoreksiListView(ListView):
    template_name = 'koreksi/input-koreksi-pg.html'
    paginate_by = 10

    def get_queryset(self):
        query = InputKoreksi.objects.all()
        due = self.request.GET.get('duedate', None)
        if due:
            query = query.filter(timestamp__date=due)
        return query

def simple_upload(request):
    docs = DocumentImportTemplate.objects.filter(is_valid=True)
    msg = None
    is_valid = False
    if request.method == 'POST':
        person_resource = InputKoreksiResource()
        dataset = Dataset()
        new_persons = request.FILES['myfile']

        imported_data = dataset.load(new_persons.read())
        result = person_resource.import_data(dataset, dry_run=True)  # Test the data import
        
        msg = 'Error while uploading data. Invalid data resource.'
        is_valid = False
        if not result.has_errors():
            if not result.has_validation_errors():
                msg = 'Upload data completed.'
                is_valid = True
                person_resource.import_data(dataset, dry_run=False)  # Actually import now
            
    content = {
        'doc': docs.first(),
        'msg': msg,
        'is_valid': is_valid,
    }
    return render(request, 'koreksi/simple-upload-pg.html', content)


def export(request):
    person_resource = ExportKoreksiResource()
    dataset = person_resource.export()
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="koreksi.xls"'
    return response