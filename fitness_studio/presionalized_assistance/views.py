from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import PersonalizedFitnessPlan
from .serializers import FitnessPlanSerializer
import datetime
import re
import json
import google.generativeai as genai
from django.conf import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def generate_plan_with_gemini(goal, start_date, duration, hours, budget):
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

    prompt = f"""
    I want you to create a personalized fitness plan.
    Goal: {goal}
    Start Date: {start_date}
    Duration: {duration} days
    Daily Workout Hours: {hours}
    Budget: {budget}

    For each day, provide:
    - Meal Plan
    - Workout Plan

    Output ONLY the following JSON list format:
    [
      {{
        "mealPlan": "...",
        "exercisePlan": "..."
      }},
      ...
    ]
    Only give me a list of {duration} objects. Don't include anything else like notes or comments.
    """

    response = model.generate_content(prompt)
    raw_text = response.text
    print("Gemini Response:", raw_text)

    try:
        match = re.search(r'\[\s*{.*}\s*\]', raw_text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON found in Gemini response.")

        json_str = match.group(0)
        parsed_days = json.loads(json_str)

        # Add actual date fields
        base_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        plan_data = []

        for i, day in enumerate(parsed_days):
            current_date = base_date + datetime.timedelta(days=i)
            plan_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "mealPlan": day.get("mealPlan", ""),
                "exercisePlan": day.get("exercisePlan", "")
            })

        return plan_data

    except Exception as e:
        print("Gemini Parsing Error:", e)
        raise ValueError("Failed to parse JSON from Gemini response.")
  
class AI_Assistance_List_View(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        goal = data.get("goal")
        start_date = data.get("start_date")
        duration = int(data.get("duration", 30))
        hours = int(data.get("daily_workout_hours", 1))
        budget = data.get("budget")

        if not all([goal, start_date, duration, hours, budget]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            generated_plan = generate_plan_with_gemini(goal, start_date, duration, hours, budget)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        plan = PersonalizedFitnessPlan.objects.create(
            user=request.user,
            plan_name=f"{goal.capitalize()} Plan ({start_date})",
            description=f"{goal.capitalize()} plan generated with Gemini AI.",
            start_date=start_date,
            duration=duration,
            price=budget,
            plan_details=generated_plan
        )
        return Response(FitnessPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class FitnessPlanListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        plans = PersonalizedFitnessPlan.objects.filter(user=request.user)
        return Response(FitnessPlanSerializer(plans, many=True).data)


class FitnessPlanDateDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, plan_id, target_date):
        try:
            plan = PersonalizedFitnessPlan.objects.get(id=plan_id, user=request.user)
            for day_plan in plan.plan_details:
                if day_plan.get("date") == target_date:
                    return Response(day_plan)
            return Response({"error": "No plan found for the given date."}, status=status.HTTP_404_NOT_FOUND)
        except PersonalizedFitnessPlan.DoesNotExist:
            return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
