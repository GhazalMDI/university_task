from django.db import models
from django.contrib.auth.models import User

class DeviceModel(models.Model):
    parent=models.ForeignKey(User,on_delete=models.CASCADE,related_name='devices')
    device_name = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=17,unique=True)

    def __str__(self):
        return f"{self.device_name} - {self.parent.username}"


class ApplicationModel(models.Model):
    social_name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.social_name


class DeviceApplicationModel(models.Model):
    device = models.ForeignKey(DeviceModel,on_delete=models.CASCADE,related_name='device_applications')
    application = models.ForeignKey(ApplicationModel, on_delete=models.CASCADE, related_name='device_applications')
    is_blocked = models.BooleanField(default=False)
    daily_limit_minutes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.device.device_name} - {self.application.social_name}"

class UsageLogModel(models.Model):
    device_application = models.ForeignKey(DeviceApplicationModel, on_delete=models.CASCADE, related_name='usage_logs')
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    usage_minutes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ScreenshotModel(models.Model):
    device_application = models.ForeignKey(DeviceApplicationModel, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='screenshots/%Y/%m/%d/')
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_application} - {self.taken_at}"


class DailyLimitModel(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Saturday'),
        (1, 'Sunday'),
        (2, 'Monday'),
        (3, 'Tuesday'),
        (4, 'Wednesday'),
        (5, 'Thursday'),
        (6, 'Friday'),
    ]
    device = models.ForeignKey(DeviceModel,on_delete=models.CASCADE,related_name='daily_limits')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    limit_minutes = models.IntegerField(default=0)
    is_unlimited = models.BooleanField(default=True)

    class Meta:
        unique_together = ['device','day_of_week']

    def __str__(self):
        return f"{self.device.device_name} - {self.get_day_of_week_display()}"