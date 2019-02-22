from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView
)
from django.views import View
from django.views.generic import FormView
from django.views.generic.edit import SingleObjectMixin, FormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Min, F, Q
from django.contrib import messages

from core.decorators import user_executor, user_validator

from cdmsoro.forms import BukisForm, BukisValidationForm, UpdateBukisForm
from cdmsoro.models import (
    PermintaanResume, Avident, UpdatePermintaan
)
from userprofile.models import Profile
from masterdata.models import (
    Circuit, Order
)
from  masterdata.forms import ResumeOrderForm

import random

@login_required
def index(request):
    if request.user.is_authenticated:
        return redirect('cdmsoro:per_bukis_list')
    
    return redirect('cdmsoro:bukis')


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

        profile_max_count = Profile.objects.filter(group='EX').aggregate(Min('counter'))
        p_obj = list(Profile.objects.filter(group='EX', counter=profile_max_count['counter__min']))
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

        print(msg, doc)

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