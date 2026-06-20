import json

from django.shortcuts import render,redirect
from django.http import JsonResponse
from devices.models import UsageLogModel,DailyLimitModel,DeviceModel, ScreenshotModel,DeviceApplicationModel
from django.views import View
from django.db.models import Sum
from django.db.models.functions import ExtractWeekDay
from datetime import date




# Create your views here.
class HomeView(View):
    TEMPLATE_NAME = 'home.html'
    login_url = '/account/login/'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('Account:Login')


        devices = DeviceModel.objects.filter(parent=request.user)
        screenshots = ScreenshotModel.objects.none()
        total_usage = 0
        if not devices.exists():
            return render(request, self.TEMPLATE_NAME)
        if devices.exists():
            first_device = devices.first()

            screenshots = ScreenshotModel.objects.filter(
                device_application__device=first_device
            ).order_by('-taken_at')

            total_usage = UsageLogModel.objects.filter(
                device_application__device=first_device
            ).aggregate(total=Sum('usage_minutes'))['total'] or 0

        ctx = {
            'devices': devices,
            'screenshots': screenshots,
            'total_usage': total_usage,
        }
        return render(request, self.TEMPLATE_NAME, ctx)

class DeviceInfoView(View):
    def get(self, request, device_id):
        try:
            device = DeviceModel.objects.get(id=device_id, parent=request.user)
            screenshots = ScreenshotModel.objects.filter(
                device_application__device=device
            ).order_by('-taken_at').values('id', 'image', 'taken_at')

            return JsonResponse({
                'device_name': device.device_name,
                'screenshots': list(screenshots),
                'device_information':{
                    'id': device.id,
                    'device_name': device.device_name,
                    'mac_address': device.mac_address,
                }
            })
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)


class BlockAppsView(View):
    TEMPLATE_NAME = 'lock_screen.html'
    def get(self,request,device_id):
        try:
            device = DeviceModel.objects.get(id=device_id,parent=request.user)
            all_apps = DeviceApplicationModel.objects.filter(
                device=device,
            ).select_related('application')
            all_blocked = all_apps.exists() and not all_apps.filter(is_blocked=False).exists()

            ctx = {
                'all_apps': all_apps,
                'device_id':device_id,
                'all_blocked': all_blocked,
            }
            return render(request,self.TEMPLATE_NAME,ctx)
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

    def post(self,request,device_id):
        try:
            device = DeviceModel.objects.get(id=device_id,parent=request.user)
            data = json.loads(request.body)

            is_blocked = data.get("is_blocked")
            DeviceApplicationModel.objects.filter(device=device).update(is_blocked=is_blocked)
            return JsonResponse({"success":True, "is_blocked": is_blocked})
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)


class ToggleAppBlockView(View):
    def post(self, request, app_id):
        try:
            app = DeviceApplicationModel.objects.get(
                id=app_id,
                device__parent=request.user
            )
            data = json.loads(request.body)
            app.is_blocked = data.get('is_blocked')
            app.save()
            return JsonResponse({'success': True})
        except DeviceApplicationModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

class ScreenTimeView(View):
    TEMPLATE_NAME = 'time_managment.html'

    def get(self, request, device_id):
        try:

            PYTHON_WEEKDAY_TO_CUSTOM = {
                5: 0,  # Saturday
                6: 1,  # Sunday
                0: 2,  # Monday
                1: 3,  # Tuesday
                2: 4,  # Wednesday
                3: 5,  # Thursday
                4: 6,  # Friday
            }

            device = DeviceModel.objects.get(id=device_id, parent=request.user)

            for day_num, _ in DailyLimitModel.DAYS_OF_WEEK:
                DailyLimitModel.objects.get_or_create(
                    device=device, day_of_week=day_num
                )

            daily_limits = DailyLimitModel.objects.filter(device=device).order_by('day_of_week')

            usage_by_day = UsageLogModel.objects.filter(device_application__device=device).annotate(weekday=ExtractWeekDay('created_at'))\
                .values('weekday').annotate(total=Sum('usage_minutes'))

            usage_map = {item['weekday']: item['total'] for item in usage_by_day}
            today = date.today()
            used_today = UsageLogModel.objects.filter(
                device_application__device=device,
                created_at__date=today
            ).aggregate(total=Sum('usage_minutes'))['total'] or 0

            today_limit = DailyLimitModel.objects.filter(
                device=device, day_of_week=today.weekday()
            ).first()

            left_today = max(today_limit.limit_minutes - used_today,
                             0) if today_limit and not today_limit.is_unlimited else None


            today_custom_day = PYTHON_WEEKDAY_TO_CUSTOM[today.weekday()]

            today_limit = DailyLimitModel.objects.filter(
                device=device, day_of_week=today_custom_day
            ).first()
            ctx = {
                'device_id': device_id,
                'daily_limits': daily_limits,
                'used_today': used_today,
                'left_today': left_today,
                'today_limit': today_limit,
                'today_custom_day': today_custom_day,
            }
            return render(request, self.TEMPLATE_NAME, ctx)
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)



    def post(self,request,device_id):
        try:
            device =  DeviceModel.objects.get(id=device_id, parent=request.user)
            data = json.loads(request.body)
            day_of_week = data.get("day_of_week")
            delta = data.get('delta',0)
            daily, _ = DailyLimitModel.objects.get_or_create(
                device=device, day_of_week=day_of_week
            )
            daily.limit_minutes = max(daily.limit_minutes + delta, 0)
            daily.is_unlimited = False
            daily.save()
            return JsonResponse({'success': True, 'limit_minutes': daily.limit_minutes})
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)