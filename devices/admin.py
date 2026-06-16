from django.contrib import admin
from .models import *


admin.site.register(DeviceModel)
admin.site.register(ApplicationModel)
admin.site.register(DeviceApplicationModel)
admin.site.register(UsageLogModel)
admin.site.register(ScreenshotModel)
