from django.http import JsonResponse, HttpResponse
from datetime import datetime
from dateutil.parser import parse
from django.views import View
from roster.models import Shift
from roster.forms import ShiftForm

class ShiftView(View):
    def verify_date_parameters(self, request):
        try:
            start = parse(request.GET["start"])
            end = parse(request.GET["end"])
        except KeyError as e:
            return JsonResponse({"error": f"Please specify the {e} parameter!"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        return (start, end)

class ShiftFeed(ShiftView):
    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("roster.view_shift"):
            return JsonResponse({"error": "Insufficient permission!"}, status=401)

        res = self.verify_date_parameters(request)
        if not isinstance(res, tuple):
            return res
        shifts = Shift.objects.filter(start__range=res)
        events = [shift.generate_event() for shift in shifts]
        return JsonResponse(events, safe=False)

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm("roster.add_shift"):
            return JsonResponse({"error": "Insufficient permission!"}, status=401)
        if not request.POST:
            return JsonResponse({"error": "Empty post!"}, status=400)

        shift = ShiftForm(request.POST)
        if shift.is_valid():
            shift.save()
            return JsonResponse({"error": ""})
        else:
            return JsonResponse({"error": "Invalid form!", "validationErrors": shift.errors}, status=400)


class ShiftFeedUser(ShiftView):
    def get(self, request, uid=None, *args, **kwargs):
        if not request.user.has_perm("roster.view_shift"):
            return JsonResponse({"error": "Insufficient permission!"}, status=401)
        if not uid:
            JsonResponse({"error": "Invalid user id."}, status=404)
        res = self.verify_date_parameters(request)
        if not isinstance(res, tuple):
            return res
        shifts = Shift.objects.filter(start__range=res, worker=uid)
        events = [shift.generate_event() for shift in shifts]
        return JsonResponse(events, safe=False)

class ShiftFeedDepartment(ShiftView):
    def get(self, request, did=None, *args, **kwargs):
        if not request.user.has_perm("roster.view_shift"):
            return JsonResponse({"error": "Insufficient permission!"}, status=401)
        if not did:
            JsonResponse({"error": "Invalid user id."}, status=404)
        res = self.verify_date_parameters(request)
        if not isinstance(res, tuple):
            return res
        shifts = Shift.objects.filter(start__range=res, department=did)
        events = [shift.generate_event() for shift in shifts]
        return JsonResponse(events, safe=False)


class ShiftEdit(View):
    def post(self, request, sid, *args, **kwargs):
        if not request.user.has_perm("roster.change_shift"):
            return JsonResponse({"error": "Insufficient permission!"}, status=401)

        try:
            instance = Shift.objects.get(pk=sid)
        except Exception as e:
            return JsonResponse({"error": "Shift not found"}, status=404)

        shift = ShiftForm(request.POST, instance=instance)
        if shift.is_valid():
            shift.save()
            return JsonResponse({"error": ""})
        else:
            return JsonResponse({"error": "Invalid form!", "validationErrors": shift.errors}, status=400)

    def delete(self, request, sid, *args, **kwargs):
        if not request.user.has_perm("roster.delete_shift"):
            return JsonResponse({"error": "Insufficient permission!"}, status=401)

        try:
            instance = Shift.objects.get(pk=sid)
        except Exception as e:
            return JsonResponse({"error": "Shift not found"}, status=404)

        instance.delete()
        # instance.save()

        return JsonResponse({"error": None})
