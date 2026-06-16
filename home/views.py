from django.shortcuts import render
from django.http import JsonResponse
from devices.models import UsageLogModel,DeviceModel, ScreenshotModel,DeviceApplicationModel
from django.views import View
from django.db.models import Sum



# Create your views here.
class HomeView(View):
    TEMPLATE_NAME = 'home.html'

    from django.db.models import Sum
    from devices.models import DeviceModel, ScreenshotModel, UsageLogModel

    def get(self, request):
        devices = DeviceModel.objects.filter(parent=request.user)
        screenshots = ScreenshotModel.objects.none()
        total_usage = 0

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
                'screenshots': list(screenshots)
            })
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)


class BlockAppsView(View):
    def get(self,request,device_id):
        try:
            device = DeviceModel.objects.get(id=device_id,parent=request.user)
            blocked = DeviceApplicationModel.objects.filter(
                device=device,
                is_blocked=True
            ).select_related('application')
            apps = [{"id":b.id,'name':b.application.social_name} for b in blocked]
            print(apps)
            return JsonResponse({"apps":apps})
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

