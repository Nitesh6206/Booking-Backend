from django.db import models
from django.contrib.auth.models import User

class PersonalizedFitnessPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fitness_plans")
    plan_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    plan_details = models.JSONField(blank=True, null=True)  # JSON list of daily plans
    start_date = models.DateField()
    duration = models.IntegerField(help_text="Duration in days")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan_name} ({self.user.username})"
