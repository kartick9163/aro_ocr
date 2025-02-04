from django.db import models

from django.utils.timezone import localtime
import pytz

class user_details(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    mobile_no = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=True)
    access_type = models.CharField(max_length=255, null=True)
    organization = models.CharField(max_length=255, null=True)
    user_role = models.CharField(max_length=255, null=True)
    email_status = models.CharField(max_length=255, null=True)
    preference_flg = models.CharField(max_length=255, null=True)
    jwt_token = models.TextField(null=True)

    class Meta:
        db_table = 'user_details'

    def save(self, *args, **kwargs):
        if self.registration_date:
            ist = pytz.timezone('Asia/Kolkata')
            self.registration_date = localtime(self.registration_date, ist)
        super().save(*args, **kwargs)

class api_key(models.Model):
    slno = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    user_id = models.IntegerField(null=True)  # INT field
    api_keys = models.CharField(max_length=255, null=True)
    api_name = models.CharField(max_length=255, null=True)
    free_count = models.IntegerField(null=True)
    created_time = models.DateTimeField(auto_now_add=True, null=True)  # DATETIME field

    class Meta:
        db_table = 'api_key'  # Table name

class user_preference(models.Model):
    slno = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    user_id = models.IntegerField(null=True)  # INT field
    purpose = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'user_preference'