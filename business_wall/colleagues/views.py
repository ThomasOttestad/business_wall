from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from departments.models import Department
from django.db.models import Q
import itertools

class ColleaguesView(View):
    def get(self, request, *args, **kwargs):

        page = int(request.GET.get("p", 1))
        psize = int(request.GET.get("pSize", 10))
        query = request.GET.get("q", None)



        if query:
            departments = Department.objects.filter(name__contains=query)
            colleagues = User.objects.filter(
                Q(first_name__contains=query) |
                Q(last_name__contains=query)  |
                Q(username__contains=query)   |
                Q(pk__in=sum([[u.pk for u in d.get_members()] for d in departments], []))
            )
        else:
            colleagues = User.objects.all()

        paginator = Paginator(colleagues, psize)
        try:
            currentPage = paginator.page(page)
        except EmptyPage:
            raise Http404

        print(list(currentPage))
        context = {
            "colleagues": currentPage,
            "paginator": paginator,
            "query": query if query else ""
        }

        return render(request, "colleagues.html", context)
