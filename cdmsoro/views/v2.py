from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse

from cdmsoro.models import PermintaanResume
from cdmsoro.forms import BukisValidationForm
from masterdata.forms import (
    ResumeOrderForm, ResumeOrderForm_v2
)

def index(request):
    per_bukis_objs = PermintaanResume.objects.filter(resume__isnull=True)[:10]
    content = {
        'bukis_list': per_bukis_objs
    }
    return render(request, 'cdmsoro/v2/pg-index.html', content)


def permin_bukis_detail_view(request, id):
    data = dict()
    per_bukis = get_object_or_404(PermintaanResume, pk=id)
    form = BukisValidationForm(request.POST or None)
    resume_form = ResumeOrderForm(request.POST or None, initial={'circuit': per_bukis.id})
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.permintaan_resume = per_bukis
            instance.save()

        if resume_form.is_valid() and per_bukis.is_approved():
            instance = resume_form.save(commit=False)
            instance.type_order = 'RO'
            instance.create_by = request.user
            instance.save()
            PermintaanResume.objects.filter(pk=id).update(resume=instance)

    content = {
        'per_bukis': per_bukis,
        'form': form,
        'bukis_form': resume_form
    }

    data['html'] = render_to_string(
        'cdmsoro/v2/includes/partial-permitaan-bukis-detail.html',
        content,
        request = request
    )
    
    return JsonResponse(data)