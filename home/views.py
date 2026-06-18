from django.shortcuts import render,redirect
from django.http import JsonResponse
from devices.models import UsageLogModel,DeviceModel, ScreenshotModel,DeviceApplicationModel
from django.views import View
from django.db.models import Sum



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
    TEMPLATE_NAME = 'lock_screen.html'
    def get(self,request,device_id):
        try:
            device = DeviceModel.objects.get(id=device_id,parent=request.user)
            all_apps = DeviceApplicationModel.objects.filter(
                device=device,
            ).select_related('application')
            ctx = {
                'all_apps': all_apps
            }
            return render(request,self.TEMPLATE_NAME,ctx)
        except DeviceModel.DoesNotExist:
            return JsonResponse({'error': 'not found'}, status=404)

