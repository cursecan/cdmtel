from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView
)
from django.views import View
from django.http import JsonResponse
from django.views.generic import FormView
from django.views.generic.edit import SingleObjectMixin, FormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Max, Min, F, Q, ExpressionWrapper, PositiveIntegerField, OuterRef, Subquery
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.postgres.search import SearchVector

from core.decorators import user_executor, user_validator

from cdmsoro.forms import (
    BukisForm, BukisValidationForm, UpdateBukisForm, UploadDocForm
)
from cdmsoro.models import (
    PermintaanResume, Avident, UpdatePermintaan
)
from userprofile.models import Profile
from masterdata.models import (
    Circuit, Order
)
from  masterdata.forms import ResumeOrderForm

import random


def set_obj_pagination(obj_v, rownum, page):
    paginator = Paginator(obj_v, rownum)

    try :
        obj_list = paginator.page(page)
    except PageNotAnInteger:
        obj_list = paginator.page(1)
    except EmptyPage:
        obj_list = paginator.page(paginator.num_pages)

    return obj_list


@login_required
def index(request):
    return redirect('home')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_executor, name='dispatch')
class UclosedOrderView(ListView):
    template_name = 'cdmsoro/pg-unclosed-order.html'
    paginate_by = 20
    context_object_name = 'order_list'

    def get_queryset(self):
        return Order.objects.filter(create_by=self.request.user, closed=False)


@method_decorator(login_required, name='dispatch')
# @method_decorator(user_validator, name='dispatch')
class UnValidateBukisView(ListView):
    template_name = 'cdmsoro/pg-unvalidate.html'
    paginate_by = 20
    context_object_name = 'bukis_list'

    def get_queryset(self):
        queryset = PermintaanResume.objects.filter(validate=False)
        return queryset


@method_decorator(login_required, name='dispatch')
# @method_decorator(user_validator, name='dispatch')
class DetailUnvalidateView(DetailView):
    model = PermintaanResume
    template_name = 'cdmsoro/pg-detail-unvalidate.html'
    context_object_name = 'bukis'
    pk_url_kwarg = 'id'


@login_required
# @user_validator
def detailUnvalidateView(request, id):
    bukis_obj = get_object_or_404(PermintaanResume, pk=id, validate=False)
    form = BukisValidationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.permintaan_resume = bukis_obj
            instance.save()
            
            if instance.action == 'APP':
                messages.success(request, "Request permintaan bukis SID %s diterima dan segera diproces." %(bukis_obj.sid.sid))
            else :
                messages.success(request, "Request bukis SID %s ditolak dan dikemballikan ke requester unutk di update." %(bukis_obj.sid.sid))
            return redirect('cdmsoro:unvalidate')

    content = {
        'bukis': bukis_obj,
        'form': form
    }
    return render(request, 'cdmsoro/pg-detail-unvalidate.html', content)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_executor, name='dispatch')
class ValidateInactionView(ListView):
    template_name = 'cdmsoro/pg-inaction-resume.html'
    context_object_name = 'bukis_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = PermintaanResume.objects.filter(
            validate = True, validation__action='APP', resume__isnull=True,
            executor = self.request.user
        ).distinct()
        return queryset


@login_required
@user_executor
def detailValidateActionView(request, id):
    permintaa_obj = get_object_or_404(PermintaanResume, pk=id, resume__isnull=True, executor=request.user)
    form = ResumeOrderForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.type_order = 'RO'
            instance.circuit = permintaa_obj.sid
            instance.create_by = request.user
            instance.save()
            PermintaanResume.objects.filter(pk=id).update(resume=instance)

            return redirect('cdmsoro:bukis_action')

    content = {
        'bukis': permintaa_obj,
        'form': form,
    }
    return render(request, 'cdmsoro/pg-detail-inaction.html', content)



class PermintaanBukisListView(ListView):
    template_name = 'cdmsoro/pg-bukis.html'
    model = PermintaanResume
    context_object_name = 'bukis_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(sid__sid__contains=search)
        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BukisForm()
        return context


class BukisFormView(FormView):
    template_name = 'cdmsoro/pg-bukis.html'
    form_class = BukisForm
    success_url = '/cdm/request-bukis/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bukis_list'] = PermintaanResume.objects.all()
        return context

    def form_valid(self, form):
        pic = form.cleaned_data['pic']
        sid = form.cleaned_data['circuit']
        msg = form.cleaned_data['message']
        doc = form.cleaned_data['avident']

        # MIN COUNTER XXX
        min_counter = Profile.objects.filter(group='EX').aggregate(
            r_min = Min(F('counter') * F('multiple'), output_field=PositiveIntegerField())
        )
        prfile_objs = Profile.objects.filter(group='EX').annotate(
            counting = ExpressionWrapper(
                F('counter') * F('multiple'), output_field=PositiveIntegerField()
            )
        ).filter(
            counting = min_counter['r_min']
        )
        
        p_obj = list(prfile_objs)
        # PROFILE CHOICES
        
        choices_profile = random.choice(p_obj)

        circuit_obj = Circuit.objects.get(sid=sid)
        per_bukis_obj = PermintaanResume.objects.create(
            pic = pic,
            message = msg,
            sid = circuit_obj,
            suspend = circuit_obj.get_suspend_order(),
            executor = choices_profile.user,
        )
        avident_obj = Avident.objects.create(
            document = doc,
            leader = per_bukis_obj
        )
        messages.success(self.request, "Permintaan bukis berhasil di tambahkan.")

        return super().form_valid(form)


class PermintaanBukisView(View):
    def get(self, request, *args, **kwargs):
        view = PermintaanBukisListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = BukisFormView.as_view()
        return view(request, *args, **kwargs)



def bukisView(request):
    form = BukisForm()
    bukis_objs = PermintaanResume.objects.all()
    search = request.GET.get('search', None)
    if search:
        bukis_objs = bukis_objs.filter(sid__sid=search)

    if request.method == 'POST':
        form = BukisForm(request.POST, request.FILES)
        if form.is_valid():
            pic = form.cleaned_data['pic']
            sid = form.cleaned_data['circuit']
            msg = form.cleaned_data['message']
            doc = form.cleaned_data['avident']

            circuit_obj = Circuit.objects.get(sid=sid)
            per_bukis_obj = PermintaanResume.objects.create(
                pic = pic,
                message = msg,
                sid = circuit_obj,
                suspend = circuit_obj.get_suspend_order()
            )
            avident_obj = Avident.objects.create(
                document = doc,
                leader = per_bukis_obj
            )
    page = request.GET.get('page', None)
    paginator = Paginator(bukis_objs, 20)
    try:
        bukis_obj = paginator.page(page)
    except PageNotAnInteger:
        bukis_obj = paginator.page(1)
    except EmptyPage:
        bukis_obj = paginator.page(paginator.num_pages)

    content = {
        'form': form,
        'bukis_list': bukis_obj
    }
    return render(request, 'cdmsoro/pg-bukis.html', content)


class DetailPermintaanBukis(DetailView):
    template_name = 'cdmsoro/pg-update-permintaan-bukis.html'
    context_object_name = 'bukis'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return PermintaanResume.objects.filter(validate=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UpdateBukisForm()
        return context


class PostUpdatePermintaaView(SingleObjectMixin, FormView):
    template_name = 'cdmsoro/pg-update-permintaan-bukis.html'
    form_class = UpdateBukisForm
    pk_url_kwarg = 'id'
    success_url = '/cdm/request-bukis/'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=PermintaanResume.objects.filter(validate=True))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        msg = form.cleaned_data.get('message')
        doc = form.cleaned_data.get('doc')
        update_obj = UpdatePermintaan.objects.create(
            permintaan_resume = self.object,
            message = msg
        )
        Avident.objects.create(
            leader = self.object,
            document = doc
        )
        return super().form_valid(form)


class UpdatePermintaanView(View):
    def get(self, request, *args, **kwargs):
        view = DetailPermintaanBukis.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostUpdatePermintaaView.as_view()
        return view(request, *args, **kwargs)




# ===================================================

def jsPostPerminUploadDoc(request, id):
    permin_obj = get_object_or_404(PermintaanResume, pk=id, validate=False)
    data = dict()
    data['is_valid'] = False

    form = UploadDocForm(request.POST, request.FILES)
    if form.is_valid():
        doc = form.cleaned_data['doc']

        Avident.objects.create(
            document = doc,
            leader = permin_obj
        )

        data['is_valid'] = True
    
    content = {
        'permin_resume': permin_obj
    }

    data['html'] = render_to_string(
        'cdmsoro/includes/partial-upload-document.html',
        content, request=request
    )

    return JsonResponse(data)


def circuitListView(request):
    page = request.GET.get('page', 1)
    q = request.GET.get('q', None)
    status = request.GET.get('sto', None)

    circuit_objs = Circuit.objects.all()

    if status:
        circuit_objs = circuit_objs.filter(
            is_active = True if status == '1' else False
        )
    
    if q:
       circuit_objs = circuit_objs.annotate(
           search = SearchVector(
               'sid', 'account__account_number',
               'account__bp', 'account__customer_name'
           )
       ).filter(search=q)

    paginate_circuit = set_obj_pagination(circuit_objs, 20, page)

    content = {
        'circuit_list': paginate_circuit,
        'c_circuit': circuit_objs.aggregate(
            c_suspend = Count('sid', filter=Q(is_active=False)),
            c_active = Count('sid', filter=Q(is_active=True))
        )
    }
    return render(request, 'cdmsoro/pg_circuit_list.html', content)


def circuitDetailView(request, id):
    circuit_obj = get_object_or_404(Circuit, pk=id, is_active=False)
    unclosed_permin_bukis = circuit_obj.permin_bukis.filter(closed=False)
    if unclosed_permin_bukis.exists():
        return redirect('cdmsoro:v3_permin_bukis_detail', unclosed_permin_bukis.latest('timestamp').id)

    form = BukisForm(request.POST or None, request.FILES or None, initial={'circuit': circuit_obj.sid})
    if request.method == 'POST':
        if form.is_valid():
            circuit = form.cleaned_data['circuit']
            pic = form.cleaned_data['pic']
            msg = form.cleaned_data['message']
            e_fl = form.cleaned_data['avident']


            v_group = 'EX'
            if circuit_obj.get_suspend_order().order_label == 2:
                # JIKA SUSPEND KONTRAK
                v_group = 'EC'

            # MIN COUNTER XXX
            min_counter = Profile.objects.filter(group=v_group).aggregate(
                r_min = Min(F('counter') * F('multiple'), output_field=PositiveIntegerField())
            )
            prfile_objs = Profile.objects.filter(group=v_group).annotate(
                counting = ExpressionWrapper(
                    F('counter') * F('multiple'), output_field=PositiveIntegerField()
                )
            ).filter(
                counting = min_counter['r_min']
            )
            
            p_obj = list(prfile_objs)
            # PROFILE CHOICES
            
            choices_profile = random.choice(p_obj)

            permit_obj = PermintaanResume.objects.create(
                pic = pic,
                message = msg,
                sid = circuit_obj,
                suspend = circuit_obj.get_suspend_order(),
                executor = choices_profile.user
            )

            Avident.objects.create(
                document = e_fl,
                leader = permit_obj
            )

            return redirect('cdmsoro:v3_permin_bukis_detail', permit_obj.id)

    content = {
        'circuit': circuit_obj,
        'form': form,
    }
    return render(request, 'cdmsoro/pg_circuit_detail.html', content)


def perminBukisDetailview(request, id):
    perbukis_obj = get_object_or_404(PermintaanResume, pk=id, closed=False)
    form = UpdateBukisForm(request.POST or None)
    if request.method == 'POST':
        if not perbukis_obj.validate:
            if form.is_valid():
                UpdatePermintaan.objects.create(
                    permintaan_resume = perbukis_obj,
                    message = form.cleaned_data['message']
                )
                messages.success(request, 'Update permintaan bukis sudah disimpan.')
                return redirect('cdmsoro:v3_permin_bukis_detail', id)

        messages.success(request, 'Permintaan sudah approved menunggu process buka isolir.')

    content = {
        'permin_bukis': perbukis_obj,
        'validation_list': perbukis_obj.validation_set.all(),
        'form': form
    }
    return render(request, 'cdmsoro/pg_perminbukis_customer_detail.html', content)