import random
# DJANGO LIB
from django.http import HttpRequest
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from courses.models import CourseGroupSubscription
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Prefetch
#REST LIB
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from rest_framework.test import APIRequestFactory
from rest_framework import generics
from rest_framework.filters import SearchFilter
# FILES
from .models import *
from .serializers import *




#* < ==============================[ <- Authentication -> ]============================== > ^#
class StudentSignInView(APIView):
    """
    Handle student sign-in requests by validating credentials and returning JWT tokens upon successful authentication.
    """

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate the user with provided credentials
        user = authenticate(username=username, password=password)

        if user is not None:
            try:
                student = user.student
            except Student.DoesNotExist:
                return Response(
                    {'error': 'No student profile associated with this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if student.block:
                return Response(
                    {'error': 'لقد تم حظرك من قبل الإدارة'},
                    status=status.HTTP_403_FORBIDDEN
                )

            refresh = RefreshToken.for_user(user)  # Generate refresh token
            access = AccessToken.for_user(user)    # Generate access token
            
            # Add Header Name To Token
            access_token = f'{settings.SIMPLE_JWT["AUTH_HEADER_TYPES"]} {access}'
            refresh_token = f'{settings.SIMPLE_JWT["AUTH_HEADER_TYPES"]} {refresh}'
            
            # Store Token In Student Model
            student.jwt_token = access_token
            student.save()

            return Response({
                'refresh_token': refresh_token,
                'access_token': access_token,
            })

        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class StudentSignUpView(APIView):
    """
    Handle student sign-up requests, validate input data, and return an access token upon successful registration.
    """

    def post(self, request):
        # Initialize the serializer with the incoming data
        serializer = StudentSignUpSerializer(data=request.data)

        # Validate the data provided by the user
        if serializer.is_valid():
            # Save the valid data, creating a new student instance
            student = serializer.save()

            # Generate an access token for the associated user
            access_token = AccessToken.for_user(student.user)
            
            # Save access_token in model student
            student.jwt_token = f'Bearer {access_token}'
            student.save()
            
            # Return the access token in the response
            return Response(
                {"access_token": f'{settings.SIMPLE_JWT["AUTH_HEADER_TYPES"]} {access_token}'},
                status=status.HTTP_200_OK
            )

        # If validation fails, return the errors in the response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentSignCodeView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,*args, **kwargs):
        code = request.data.get("code")
        student = request.user.student

        # is student edit the code before  
        if student.by_code:
            return Response({"error":"you are can not add your code "},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        try:
            code = StudentCode.objects.get(code=code)
            
            # if the code is already taken 
            if code.available == False:
                return Response({"error":"this code is already taken"},status=status.HTTP_406_NOT_ACCEPTABLE)
            
            # else sign code to student and make student by_code = True
            # update code
            code.available = False
            code.student=student
            # update student
            student.by_code = True
            student.code = code.code
            # saves
            code.save()
            student.save()
        
        except StudentCode.DoesNotExist:
            return Response({"error":"This Code Does Not Exist"},status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_201_CREATED)


#* < ==============================[ <- Reset Password  -> ]============================== > ^#

#^ Step 1 
class RequestResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        
        if not username:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user=User.objects.get(username=username)

        except User.DoesNotExist:
            
            return Response({"error":"the user not found"},status=status.HTTP_404_NOT_FOUND)

        # Generate a 6-digit PIN code
        pin_code = str(random.randint(100000, 999999))

        # Store the PIN code in cache for validation later
        cache.set(username, pin_code, timeout=60)  # 1 minutes validity
        
        # Send the PIN code to the user's WhatsApp number
        req_send = send_whatsapp_massage(
            massage=f'Your PIN code is {pin_code}',
            phone_number=f'{username}'
        )
        return Response({"success":req_send['success']}, status=status.HTTP_200_OK)

#^ Step 2
class VerifyPinCodeView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        pin_code = request.data.get('pin_code')

        if not username or not pin_code:
            return Response({"massage": "Phone number and PIN code are required.","success":False}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the stored PIN code from cache
        stored_pin_code = cache.get(username)

        if stored_pin_code is None:
            return Response({"massage": "PIN code has expired or was not sent.","success":False}, status=status.HTTP_400_BAD_REQUEST)

        if stored_pin_code != pin_code:
            return Response({"massage": "Invalid PIN code.","success":False}, status=status.HTTP_400_BAD_REQUEST)

        # If the PIN code is valid, reset the password or proceed with further actions
        return Response({"massage": "PIN code verified successfully.","success":True}, status=status.HTTP_200_OK)

#^ Step 3
class ResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        pin_code = request.data.get('pin_code')
        new_password = request.data.get('new_password')

        if not username or not pin_code or not new_password:
            return Response({"massage": "Phone number, PIN code, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Use APIRequestFactory to create a compatible HttpRequest for VerifyPinCodeView
        factory = APIRequestFactory()
        verify_request = factory.post('',data={'username': username, 'pin_code': pin_code})
        

        # Call VerifyPinCodeView
        verify_response = VerifyPinCodeView.as_view()(verify_request)
        if verify_response.status_code != status.HTTP_200_OK:
            return verify_response  # Invalid PIN code

        # Reset the password (assuming User model is used)
        try:
            user = User.objects.get(username=username)  # Adjust this based on your model
        except User.DoesNotExist:
            return Response({"massage": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        cache.delete(username)
        return Response({"massage": "Password reset successfully.","success":True}, status=status.HTTP_200_OK)



class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        student = get_object_or_404(
            Student.objects.select_related('user', 'type_education', 'year'),
            user=request.user
        )
        
        res_data = StudentProfileSerializer(student).data
        
        return Response(res_data, status=status.HTTP_200_OK)

class TeacherSignInView(APIView):
    """View for teacher sign-in"""
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        serializer = TeacherSignInSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            teacher = serializer.validated_data['teacher']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Prepare response data
            teacher_serializer = TeacherSerializer(teacher)
            
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'teacher': teacher_serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminSignInView(APIView):
    def post(self, request):
        serializer = AdminAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update student jwt_token if exists
        try:
            student = user.student
            student.jwt_token = f"Bearer {str(refresh.access_token)}"
            student.save()
        except Student.DoesNotExist:
            pass
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


#* < ==============================[ <- subscriptions -> ]============================== > ^#



class MySubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the student associated with the current user
            student = Student.objects.select_related(
                'year', 'type_education'
            ).prefetch_related(
                Prefetch('coursegroupsubscription_set', 
                        queryset=CourseGroupSubscription.objects.select_related(
                            'course', 'course_group', 'course_group__teacher'
                        ).prefetch_related(
                            'course_group__times'
                        ))
            ).get(user=request.user)

            subscriptions = student.coursegroupsubscription_set.all()
            
            # Split subscriptions
            confirmed_subs = []
            unconfirmed_subs = []
            declined_subs = []
            
            for sub in subscriptions:
                sub_data = {
                    'subscription_id': sub.id,
                    'course_id': sub.course.id if sub.course else None,
                    'course_title': sub.course.title if sub.course else None,
                    'year_id': sub.course.year.id if sub.course and sub.course.year else None,
                    'year_name': sub.course.year.name if sub.course and sub.course.year else None,
                    'group_id': sub.course_group.id if sub.course_group else None,
                    'group_capacity': sub.course_group.capacity if sub.course_group else None,
                    'teacher_id': sub.course_group.teacher.id if sub.course_group and sub.course_group.teacher else None,
                    'teacher_name': sub.course_group.teacher.name if sub.course_group and sub.course_group.teacher else None,
                    'teacher_education_language_type': sub.course_group.teacher.education_language_type if sub.course_group and sub.course_group.teacher else None,
                    'created_at': sub.created_at,
                    'confirmed_at': sub.confirmed_at,
                    'declined_at': sub.declined_at,
                    'decline_note': sub.decline_note,
                    'timeslots': [
                        {
                            'day': slot.day,
                            'time': slot.time.strftime('%H:%M')
                        } for slot in sub.course_group.times.all()
                    ] if sub.course_group else []
                }
                
                if sub.is_declined:
                    declined_subs.append(sub_data)
                elif sub.is_confirmed:
                    confirmed_subs.append(sub_data)
                else:
                    unconfirmed_subs.append(sub_data)

            response_data = {
                'student_id': student.id,
                'student_name': student.name,
                'student_code': student.code,
                'student_division': student.division,
                'student_government': student.government,
                'student_year': student.year.name if student.year else None,
                'type_education': student.type_education.name if student.type_education else None,
                'confirmed_subscriptions_count': len(confirmed_subs),
                'unconfirmed_subscriptions_count': len(unconfirmed_subs),
                'declined_subscriptions_count': len(declined_subs),
                'has_unconfirmed_subscriptions': len(unconfirmed_subs) > 0,
                'has_declined_subscriptions': len(declined_subs) > 0,
                'confirmed_subscriptions': confirmed_subs,
                'unconfirmed_subscriptions': unconfirmed_subs,
                'declined_subscriptions': declined_subs
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )