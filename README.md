# Food Calorie Prediction Web Application

A web application that predicts calorie, fat, and energy values from food images using the Google Gemini AI API.

## Features

- **User Authentication**: Register and login functionality
- **Food Image Analysis**: Upload food images to get nutritional information
- **Prediction History**: View your recent food predictions
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python, Django
- **Database**: SQLite
- **AI API**: Google Gemini 1.5 Flash

## How It Works

1. **Register/Login**: New users register with name, email, and password. Existing users login with email and password.
2. **Upload Image**: After logging in, users can upload a food image on the prediction page.
3. **Get Results**: The application analyzes the image using Google's Gemini AI and displays the food name, calories, fat, and energy values.
4. **History**: Users can view their previous food predictions.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd FCP
   ```

2. Install dependencies:
   ```
   pip install django pillow google-generativeai
   ```

3. Apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Run the development server:
   ```
   python manage.py runserver
   ```

5. Visit `http://127.0.0.1:8000/` in your browser

## Gemini API Key

The application uses Google's Gemini 1.5 Flash API for image analysis. The API key is configured in the settings.py file.

## Project Structure

- **foodcalorie**: Main Django project
- **foodimgcalorie**: Django app for food image analysis
- **templates**: HTML templates
- **static**: Static files (CSS, JS, images)
- **media**: Uploaded food images

## Credits

Developed by Group no. 24 Batch of 2025, Sanjivani College of Engineering. 