from django.db import models

# Create your models here.
class user_details(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    fullname = models.CharField(max_length=255, null=True)  # VARCHAR field
    email = models.CharField(max_length=255, null=True)  # Email field
    mobile_no = models.CharField(max_length=255, null=True)  # VARCHAR field
    password = models.CharField(max_length=255, null=True)  # VARCHAR field
    registration_date = models.DateTimeField(auto_now_add=True, null=True)  # DATETIME field
    access_type = models.CharField(max_length=255, null=True)  # VARCHAR field
    organization = models.CharField(max_length=255, null=True)  # VARCHAR field
    user_role = models.CharField(max_length=255, null=True)  # VARCHAR field
    email_status = models.CharField(max_length=255, null=True)  # VARCHAR field
    preference_flg = models.CharField(max_length=255, null=True)  # VARCHAR field
    jwt_token = models.TextField(null=True)  # Longtext field

    class Meta:
        db_table = 'user_details'  # Table name

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