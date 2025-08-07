from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import User, FoodPrediction
import os
import google.generativeai as genai
from django.conf import settings
import base64
from django.core.files.base import ContentFile
import json
import re

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Helper function to extract numeric values from text
def extract_numeric_value(text_value):
    if text_value is None:
        return 0
    
    # If it's already a number, return it
    if isinstance(text_value, (int, float)):
        return float(text_value)
    
    # Try to convert directly to float if possible
    try:
        return float(text_value)
    except (ValueError, TypeError):
        pass
    
    # Try to extract the first number found in the string
    numbers = re.findall(r'\d+(?:\.\d+)?', str(text_value))
    if numbers:
        return float(numbers[0])
    
    # If no number found, return 0
    return 0

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Basic validation
        if '@' not in email:
            return JsonResponse({'status': 'error', 'message': 'Email must contain @'})
        
        if password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'User Already Registered'})
        
        # Create user
        User.objects.create(name=name, email=email, password=password)
        return JsonResponse({'status': 'success', 'message': 'Registration Successfully'})
    
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Basic validation
        if '@' not in email:
            return JsonResponse({'status': 'error', 'message': 'Email must contain @'})
        
        try:
            user = User.objects.get(email=email, password=password)
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            return JsonResponse({'status': 'success', 'message': 'Login Successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User Not Register'})
    
    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    return redirect('home')

def prediction(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    if request.method == 'POST' and request.FILES.get('food_image'):
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        
        image_file = request.FILES['food_image']
        
        # Validate file is an image
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(image_file.name)[1].lower()
        
        if ext not in valid_extensions:
            return JsonResponse({
                'status': 'error',
                'message': 'Please Upload the Food Image (jpg, jpeg, png, or gif)'
            })
            
        # Process image with Gemini API
        try:
            # Convert image to base64 format
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Reset file pointer
            image_file.seek(0)
            
            # Configure Gemini model - Updated to use gemini-1.5-flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare prompt
            prompt = """
            Identify this food and provide its name, calorie content, fat content, and energy value.
            If this is not a food image, please respond with 'This is not a food image'.
            Format the response as JSON with fields: food_name, calories, fat, energy.
            
            IMPORTANT: Provide only numeric values (no text) for calories, fat, and energy fields.
            If exact values are unknown, provide your best estimate as a single number.
            
            For example: {"food_name": "Apple", "calories": 52, "fat": 0.2, "energy": 218}
            """
            
            # Make API request
            response = model.generate_content([
                prompt,
                {"mime_type": f"image/{image_file.name.split('.')[-1]}", "data": base64_image}
            ])
            
            try:
                # Parse the response text to extract JSON
                response_text = response.text
                # Find JSON content
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    food_data = json.loads(json_str)
                    
                    # Check if this is not a food image
                    if food_data.get('food_name', '').lower() == 'this is not a food image':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Please Upload the Food Image'
                        })
                else:
                    # Fallback if JSON parsing fails
                    food_data = {
                        'food_name': 'Unknown Food',
                        'calories': 0,
                        'fat': 0,
                        'energy': 0
                    }
            except Exception as e:
                # Fallback if any parsing error occurs
                food_data = {
                    'food_name': 'Unknown Food',
                    'calories': 0,
                    'fat': 0,
                    'energy': 0
                }
            
            # Save the prediction
            prediction = FoodPrediction.objects.create(
                user=user,
                food_name=food_data.get('food_name', 'Unknown Food'),
                calories=extract_numeric_value(food_data.get('calories', 0)),
                fat=extract_numeric_value(food_data.get('fat', 0)),
                energy=extract_numeric_value(food_data.get('energy', 0)),
                image=image_file
            )
            
            return JsonResponse({
                'status': 'success',
                'food_name': prediction.food_name,
                'calories': prediction.calories,
                'fat': prediction.fat,
                'energy': prediction.energy,
                'image_url': prediction.image.url
            })
        
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Error processing image. Please try again.'})
    
    elif request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Please Upload the Image'})
    
    # Get user's previous predictions
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        predictions = FoodPrediction.objects.filter(user_id=user_id).order_by('-created_at')[:5]
        context = {'predictions': predictions}
        return render(request, 'prediction.html', context)
    
    return render(request, 'prediction.html')
