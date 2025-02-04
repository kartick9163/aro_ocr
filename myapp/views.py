from datetime import datetime, timedelta  
import json, jwt
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.template import loader
# from django.utils.timezone import now
from . import send_email, base64_to_text, ip4, generate_api_key




def vrfy_html(request):
  template = loader.get_template('vrfy.html')
  return HttpResponse(template.render())



def email_vrfy(request):
    if request.method == 'GET':
        emailid = base64_to_text(request.GET.get('uid'))

        if emailid:
            with connection.cursor() as cursor:
                cursor.execute("SELECT email_status FROM user_details WHERE email = %s", [emailid])
                user_data = cursor.fetchone()
                
                if user_data:
                    email_status = user_data[0]
                    if email_status == '0':
                        cursor.execute("UPDATE user_details SET email_status = 1 WHERE email = %s", [emailid])
                        connection.commit()
                        return HttpResponseRedirect(f"http://{ip4()}:8000/api/vrfy_html")
                    
                    else:
                        template = loader.get_template('already_vrfy.html')
                        return HttpResponse(template.render())                        
                else:
                    template = loader.get_template('something_went_wrong.html')
                    return HttpResponse(template.render())
                    
        else:
            template = loader.get_template('something_went_wrong.html')
            return HttpResponse(template.render())

    else:
        return HttpResponse("Invalid request method.", status=405)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:

            current_time = datetime.now()
            reqbody = json.loads(request.body.decode('utf-8'))
            
            fullname = reqbody.get('fullname')
            email = reqbody.get('email')
            mobile_no = reqbody.get('mobile_no')
            password = reqbody.get('password')
            access_type = reqbody.get('access_type')

            if not (fullname and email and mobile_no and password and access_type ):
                return JsonResponse({'error': 'Missing required fields', 'status': False, 'code':'3'})

            
            with connection.cursor() as cursor:

                cursor.execute("SELECT id FROM user_details WHERE email = %s", [email])
                alldata3 = cursor.fetchone()
                if alldata3:
                    return JsonResponse({'msg': 'Email already exists', 'code':'3','status': False})

                
                
                cursor.execute("SELECT id FROM user_details WHERE email = %s", [email])
                alldata2 = cursor.fetchone()
                if alldata2:
                    return JsonResponse({'msg': 'Email already exists', 'code':'2','status': False})
                               
                
                cursor.execute(
                    "INSERT INTO user_details (fullname, email, mobile_no, password, registration_date, email_status, preference_flg, access_type) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                    [fullname, email, mobile_no, password, current_time, '0', '0', access_type]
                )
                connection.commit()

                # send_email('kartickdutta2153@gmail.com', email, 'Register Yourself', fullname)  # Send verification email

                return JsonResponse({'msg': 'User registered successfully', 'status': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON input', 'status': False})
        
        except Exception as e:
            print(f"Register failed: {str(e)}")
            return JsonResponse({'error': 'Internal server error', 'status': False})

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
                return JsonResponse({'msg': 'Username and password are required', 'status': False, 'code':'3'})

            with connection.cursor() as cursor:
                cursor.execute("SELECT id, fullname, email, mobile_no, password, registration_date, organization, user_role, preference_flg, email_status, jwt_token, access_type FROM user_details WHERE BINARY email = %s", [email_id])
                user_data = cursor.fetchone()

                if not user_data:
                    return JsonResponse({'msg': 'Invalid email or password', 'code' : '2' ,'status': False})

                (
                    user_id, fullname, email, mobile_no, stored_password,
                    registration_date, organization, user_role, preference_flg, email_status, jwt_token, access_type
                ) = user_data

                if email_status != '1':
                    return JsonResponse({'msg': 'Please verify your email', 'code': '1', 'status': False})

                # Verify password (plain-text comparison)
                if password != stored_password:
                    return JsonResponse({'msg': 'Invalid username or password', 'code' : '2' ,'status': False})

                # Create the JWT token
                token_payload = {
                    'user_id': user_id,
                    'fullname': fullname,
                    'email': email,
                    'mobile_no': mobile_no,
                    'access_type':access_type,
                    'registration_date': registration_date.isoformat() if registration_date else None,
                    'organization': organization,
                    'user_role': user_role,
                    'preference_flg':preference_flg,
                    'email_status': email_status,
                    'iat': datetime.utcnow(),
                    'exp': datetime.utcnow() + timedelta(hours=2)  # Token expires in 1 hour
                }
                token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

                # Store the token in the database
                cursor.execute(
                    "UPDATE user_details SET jwt_token = %s WHERE id = %s",
                    [token, user_id]
                )
                
                user_details = {
                    'user_id': user_id,
                    'fullname': fullname,
                    'email': email,
                    'mobile_no': mobile_no,
                    'access_type':access_type,
                    'registration_date': registration_date,
                    'organization': organization,
                    'user_role': user_role,
                    'email_status': email_status,
                }

                return JsonResponse({
                    'msg': 'Login successful',
                    'status': True,
                    'token': token
                })

        except json.JSONDecodeError:
            return JsonResponse({'msg': 'Invalid JSON input', 'status': False})

        except Exception as e:
            print(f"Login failed: {str(e)}")
            return JsonResponse({'msg': 'Internal server error', 'status': False})

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

            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM user_details WHERE email = %s", [email])
                alldata = cursor.fetchone()

            if alldata:
                user_id = alldata[0]  
                preferences_list = preference.split(",")  

                with connection.cursor() as cursor:
                    for pref in preferences_list:
                        cursor.execute(
                            "INSERT INTO user_preference (purpose, user_id) VALUES (%s, %s)",
                            [pref.strip(), user_id]
                        )
                    cursor.execute(
                        "UPDATE user_details SET preference_flg = '1' WHERE id = %s",
                        [user_id]
                    )
                    connection.commit()

                return JsonResponse({"msg": "User preferences added successfully", "status": True})
            else:
                return JsonResponse({'msg': 'User not found', 'status': False})        
        except Exception as e:
            print(f"User preference update failed: {str(e)}")
            return JsonResponse({'msg': 'Internal server error', 'status': False})
    else:
        return JsonResponse({"msg": "Method not allowed", "status": False})
    

@csrf_exempt
def user_role(request):
    if request.method == 'POST':
        reqbody = json.loads(request.body.decode('utf-8'))
        role = reqbody.get('role')
        email = reqbody.get('email')
        with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM user_details WHERE email = %s", [email])
                alldata = cursor.fetchone()
        if alldata:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE user_details SET user_role = %s WHERE email = %s",[role, email])
                connection.commit()
            return JsonResponse({"msg":'user role updated successfully',"status":True})
        else:
            return JsonResponse({'msg':'Something went wrong','status':False})
    else:
        return JsonResponse({"msg":"method not allowed", "status":False})

@csrf_exempt
def resend_mail(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})

    try:
        reqbody = json.loads(request.body.decode('utf-8'))
        email = reqbody.get('email')

        with connection.cursor() as cursor:
            cursor.execute("SELECT fullname FROM user_details WHERE email = %s", [email])
            result = cursor.fetchone()
        fullname = result[0]
        send_email('kartickdutta2153@gmail.com', email, 'Register Yourself', fullname)

        return JsonResponse({'msg': 'Email resent successfully', 'status': True})
    
    except Exception as e:
        return JsonResponse({'msg': f'An error occurred: {str(e)}', 'status': False})
    
@csrf_exempt
def generate_apikey(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})
    
    reqbody = json.loads(request.body.decode('utf-8'))
    email = reqbody.get('email')
    api_name = reqbody.get('api_name')
    if not api_name:
        return JsonResponse({'msg':'please enter an api key name', 'status':False})
    current_time = datetime.now()
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT jwt_token, id FROM user_details WHERE email = %s", [email])
        result = cursor.fetchone()
        
        if not result:
            return JsonResponse({'msg': 'Email not found', 'status': False})
        
        user_id = result[1]
        jwt_token = result[0]
    
    SECRET_KEY = 'arodek'
    try:
        decoded_jwt_token = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        jwt_exp = decoded_jwt_token.get('exp')
        api_key = generate_api_key()

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_key WHERE BINARY api_name = %s AND user_id = %s", [api_name, user_id])
            apinamecount = cursor.fetchone()[0]  
        
        if apinamecount > 0:
            return JsonResponse({"msg": "API name cannot be the same", 'status': False})

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO api_key (api_keys, user_id, api_name, created_time, free_count) VALUES (%s, %s, %s, %s, %s)", [api_key, user_id, api_name, current_time, 10])
            connection.commit()  

        return JsonResponse({'msg': 'api key generated successfully', 'status': True})
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({'msg': 'Token has expired', 'status': False})
    except jwt.InvalidTokenError:
        return JsonResponse({'msg': 'Invalid token', 'status': False})

@csrf_exempt
def fetch_api(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})

    reqbody = json.loads(request.body.decode('utf-8'))
    email = reqbody.get('email')

    with connection.cursor() as cursor:
        cursor.execute("SELECT jwt_token, id FROM user_details WHERE email = %s", [email])
        result = cursor.fetchone()

        if not result:
            return JsonResponse({'msg': 'Email not found', 'status': False})
        
        user_id = result[1]
        jwt_token = result[0]

    SECRET_KEY = 'arodek'  
    
    try:
        jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT api_keys, api_name, created_time FROM api_key WHERE user_id = %s", 
                [user_id]
            )
            result = cursor.fetchall()

        if result:
            api_data = [
                {"api_name": item[1], "api_key": item[0], "created_time": item[2]} 
                for item in result
            ]
            return JsonResponse({"msg": api_data, "status": True})
        else:
            return JsonResponse({"msg": result, 'message':'No key available',"status": False})

    except jwt.ExpiredSignatureError:
        return JsonResponse({'msg': 'Token has expired', 'status': False},status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'msg': 'Invalid token', 'status': False})

@csrf_exempt
def delete_api_key(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed', 'status': False})    
    reqbody = json.loads(request.body.decode('utf-8'))
    email = reqbody.get('email')
    api_name = reqbody.get('api_name')
    with connection.cursor() as cursor:
        cursor.execute("SELECT jwt_token, id FROM user_details WHERE email = %s", [email])
        result = cursor.fetchone()
    if not result:
        return JsonResponse({'msg': 'User not found', 'status': False})
    jwt_token, user_id = result
    SECRET_KEY = 'arodek'
    try:
        jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM api_key WHERE BINARY api_name = %s AND BINARY user_id = %s", [api_name, user_id])
            rows_affected = cursor.rowcount

        if rows_affected > 0:
            return JsonResponse({'msg': 'API key deleted successfully', 'status': True})
        else:
            return JsonResponse({'msg': 'Something went wrong', 'status': False})

    except jwt.ExpiredSignatureError:
        return JsonResponse({'msg': 'Token has expired', 'status': False})
    except jwt.DecodeError:
        return JsonResponse({'msg': 'Invalid token', 'status': False})

