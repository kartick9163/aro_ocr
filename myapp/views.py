from datetime import datetime, timedelta  # Import only what you need from the datetime module
import json, jwt, logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.template import loader
from django.utils.timezone import now
from .models import user_details, api_key, user_preference
from . import send_email, base64_to_text, ip4, generate_api_key




def vrfy_html(request):
  template = loader.get_template('vrfy.html')
  return HttpResponse(template.render())



def email_vrfy(request):
    if request.method == 'GET':
        emailid = base64_to_text(request.GET.get('uid'))
        if emailid:
            try:
                user = user_details.objects.filter(email=emailid).first()

                if user:
                    email_status = user.email_status

                    if email_status == '0':  # Unverified
                        user.email_status = '1'  # Update to verified
                        user.save()
                        return HttpResponseRedirect(f"http://{ip4()}:8000/api/vrfy_html")
                    else:
                        template = loader.get_template('already_vrfy.html')
                        return HttpResponse(template.render())
                else:
                    template = loader.get_template('something_went_wrong.html')
                    return HttpResponse(template.render())
            
            except Exception as e:
                logging.error(f"Error in email verification: {str(e)}")
                template = loader.get_template('something_went_wrong.html')
                return HttpResponse(template.render())
        
        else:
            template = loader.get_template('something_went_wrong.html')
            return HttpResponse(template.render())

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            reqbody = json.loads(request.body.decode('utf-8'))
            
            fullname = reqbody.get('fullname')
            email = reqbody.get('email')
            mobile_no = reqbody.get('mobile_no')
            password = reqbody.get('password')
            access_type = reqbody.get('access_type')

            # Validate required fields
            if not (fullname and email and mobile_no and password and access_type):
                return JsonResponse({'error': 'Missing required fields', 'status': False, 'code': '3'})

            # Check if email already exists
            if user_details.objects.filter(email=email).exists():
                return JsonResponse({'msg': 'Email already exists', 'code': '2', 'status': False})

            # Save the user details in the database
            user = user_details(
                fullname=fullname,
                email=email,
                mobile_no=mobile_no,
                password=password,  
                registration_date=now(),
                email_status='0',
                preference_flg='0',
                access_type=access_type
            )
            user.save()

            send_email('kartickdutta2153@gmail.com', email, 'Register Yourself', fullname)

            return JsonResponse({'msg': 'User registered successfully', 'status': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON input', 'status': False})
        
        except Exception as e:
            return JsonResponse({'error': {str(e)}, 'status': False})

    return JsonResponse({'error': 'Method not allowed', 'status': False})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            SECRET_KEY = "arodek"
            data = json.loads(request.body.decode('utf-8'))

            email_id = data.get('email')
            password = data.get('password')

            if not email_id or not password:
                return JsonResponse({'msg': 'Username and password are required', 'status': False, 'code': '3'})

            # Fetch the user from the database
            user = user_details.objects.filter(email=email_id).first()
            if not user:
                return JsonResponse({'msg': 'Invalid email or password', 'code': '2', 'status': False})
            
            if password != user.password:  
                return JsonResponse({'msg': 'Invalid email or password', 'code': '2', 'status': False})

            # Check email status
            if user.email_status != '1':
                return JsonResponse({'msg': 'Please verify your email', 'code': '1', 'status': False})

            # Create the JWT token
            token_payload = {
                'user_id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'mobile_no': user.mobile_no,
                'access_type': user.access_type,
                'registration_date': user.registration_date.isoformat() if user.registration_date else None,
                'organization': user.organization,
                'user_role': user.user_role,
                'preference_flg': user.preference_flg,
                'email_status': user.email_status,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 2 hours
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

            # Update the JWT token in the database
            user.jwt_token = token
            user.save()

            return JsonResponse({
                'msg': 'Login successful',
                'status': True,
                'token': token
            })

        except json.JSONDecodeError:
            return JsonResponse({'msg': 'Invalid JSON input', 'status': False})

        except Exception as e:
            return JsonResponse({'msg': f"An error occurred: {str(e)}", 'status': False})

    return JsonResponse({'msg': 'Method not allowed', 'status': False})



@csrf_exempt
def usr_preference(request):
    if request.method == 'POST':
        try:
            reqbody = json.loads(request.body.decode('utf-8'))
            preference = reqbody.get('preference')
            email = reqbody.get('email')

            if not preference or not email:
                return JsonResponse({'msg': 'Preference or email is missing', 'status': False})
            
            user = user_details.objects.filter(email=email).first()

            if user:
                preferences_list = preference.split(",")
                user_preferences = [
                    user_preference(user_id=user.id, purpose=pref.strip()) for pref in preferences_list
                ]
                user_preference.objects.bulk_create(user_preferences)
                user.preference_flg = '1'
                user.save()

                return JsonResponse({"msg": "User preferences added successfully", "status": True})
            else:
                return JsonResponse({'msg': 'User not found', 'status': False})

        except Exception as e:
            return JsonResponse({'msg': {str(e)}, 'status': False})

    else:
        return JsonResponse({"msg": "Method not allowed", "status": False})
    

@csrf_exempt
def user_role(request):
    if request.method == 'POST':
        try:            
            reqbody = json.loads(request.body.decode('utf-8'))
            role = reqbody.get('role')
            email = reqbody.get('email')

            if not role or not email:
                return JsonResponse({'msg': 'Role or email is missing', 'status': False})

            # Fetch the user based on email
            user = user_details.objects.filter(email=email).first()

            if user:
                user.user_role = role
                user.save()

                return JsonResponse({"msg": 'User role updated successfully', "status": True})
            else:
                return JsonResponse({'msg': 'User not found', 'status': False})

        except Exception as e:
            return JsonResponse({'msg': f"Error: {str(e)}", 'status': False})
    else:
        return JsonResponse({"msg": "Method not allowed", "status": False})
    

@csrf_exempt
def resend_mail(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})

    try:
        reqbody = json.loads(request.body.decode('utf-8'))
        email = reqbody.get('email')

        if not email:
            return JsonResponse({'msg': 'Email is missing', 'status': False})
        user = user_details.objects.filter(email=email).first()

        if not user:
            return JsonResponse({'msg': 'User not found', 'status': False})
        fullname = user.fullname
        send_email('kartickdutta2153@gmail.com', email, 'Register Yourself', fullname)

        return JsonResponse({'msg': 'Email resent successfully', 'status': True})

    except Exception as e:
        return JsonResponse({'msg': f'An error occurred: {str(e)}', 'status': False})
    

@csrf_exempt
def generate_apikey(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})

    try:
        reqbody = json.loads(request.body.decode('utf-8'))
        email = reqbody.get('email')
        api_name = reqbody.get('api_name')

        if not api_name:
            return JsonResponse({'msg': 'Please enter an API key name', 'status': False})

        current_time = datetime.now()

        # Fetch the user details based on the email
        user = user_details.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'msg': 'Email not found', 'status': False})

        jwt_token = user.jwt_token
        SECRET_KEY = 'arodek'

        try:
            # Decode the JWT token
            decoded_jwt_token = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
            jwt_exp = decoded_jwt_token.get('exp')

            # Generate API key
            api_key_value = generate_api_key()

            # Check if the API name already exists for this user
            api_name_exists = api_key.objects.filter(api_name__iexact=api_name, user_id=user.id).exists()
            if api_name_exists:
                return JsonResponse({"msg": "API name cannot be the same", 'status': False})

            # Create a new API key record
            api_key.objects.create(
                api_keys=api_key_value,
                user_id=user.id,
                api_name=api_name,
                created_time=current_time,
                free_count=10
            )

            return JsonResponse({'msg': 'API key generated successfully', 'status': True})

        except jwt.ExpiredSignatureError:
            return JsonResponse({'msg': 'Token has expired', 'status': False})
        except jwt.InvalidTokenError:
            return JsonResponse({'msg': 'Invalid token', 'status': False})

    except Exception as e:
        return JsonResponse({'msg': f'An error occurred: {str(e)}', 'status': False})
    

@csrf_exempt
def fetch_api(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})

    try:
        reqbody = json.loads(request.body.decode('utf-8'))
        email = reqbody.get('email')

        # Fetch user details
        user = user_details.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'msg': 'Email not found', 'status': False})

        jwt_token = user.jwt_token
        SECRET_KEY = 'arodek'

        try:
            # Decode the JWT token
            jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})

            # Fetch associated API keys
            api_keys = api_key.objects.filter(user_id=user.id).values('api_keys', 'api_name', 'created_time')

            if api_keys.exists():
                api_data = [
                    {
                        "api_name": item['api_name'],
                        "api_key": item['api_keys'],
                        "created_time": item['created_time'],
                    }
                    for item in api_keys
                ]
                return JsonResponse({"msg": api_data, "status": True})
            else:
                return JsonResponse({"msg": [], "message": "No key available", "status": False})

        except jwt.ExpiredSignatureError:
            return JsonResponse({'msg': 'Token has expired', 'status': False}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'msg': 'Invalid token', 'status': False})

    except Exception as e:
        return JsonResponse({'msg': f'An error occurred: {str(e)}', 'status': False})



@csrf_exempt
def delete_api_key(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})    

    try:
        reqbody = json.loads(request.body.decode('utf-8'))
        email = reqbody.get('email')
        api_name = reqbody.get('api_name')

        # Check if email exists in user_details
        user = user_details.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'msg': 'User not found', 'status': False})

        jwt_token = user.jwt_token
        user_id = user.id
        SECRET_KEY = 'arodek'

        try:
            # Validate the JWT token
            jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})

            # Check and delete the API key
            deleted_count, _ = api_key.objects.filter(api_name=api_name, user_id=user_id).delete()

            if deleted_count > 0:
                return JsonResponse({'msg': 'API key deleted successfully', 'status': True})
            else:
                return JsonResponse({'msg': 'API key not found or deletion failed', 'status': False})

        except jwt.ExpiredSignatureError:
            return JsonResponse({'msg': 'Token has expired', 'status': False})
        except jwt.DecodeError:
            return JsonResponse({'msg': 'Invalid token', 'status': False})

    except Exception as e:
        return JsonResponse({'msg': f'An error occurred: {str(e)}', 'status': False})
    


