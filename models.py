from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(upload_to='avatars/', blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class DailyPlanner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateField()

    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
class Deen(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    fajr = models.BooleanField(default=False)
    dhuhr = models.BooleanField(default=False)
    asr = models.BooleanField(default=False)
    maghrib = models.BooleanField(default=False)
    isha = models.BooleanField(default=False)

    adhkar_morning = models.BooleanField(default=False)
    adhkar_evening = models.BooleanField(default=False)

    quran_pages = models.IntegerField(default=0)

    kitab_name = models.CharField(max_length=200, blank=True)

    kitab_pages = models.IntegerField(default=0)

class Sport(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    stretching = models.BooleanField(default=False)

    steps = models.IntegerField(default=0)

    water = models.FloatField(default=0)

    gym = models.BooleanField(default=False)

    swimming = models.BooleanField(default=False)

    sleep_hours = models.FloatField(default=0)

class Regime(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    breakfast_calories = models.IntegerField(default=0)

    lunch_calories = models.IntegerField(default=0)

    dinner_calories = models.IntegerField(default=0)

    snack_calories = models.IntegerField(default=0)

    weight = models.FloatField(null=True, blank=True)

    target_calories = models.IntegerField(default=1000)

class Learning(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    language = models.CharField(max_length=100)

    speaking = models.IntegerField(default=0)

    reading = models.IntegerField(default=0)

    writing = models.IntegerField(default=0)

    listening = models.IntegerField(default=0)

    new_activity = models.CharField(max_length=200, blank=True)

    culture_topic = models.CharField(max_length=200, blank=True)

class SelfCare(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    skincare_morning = models.BooleanField(default=False)

    skincare_evening = models.BooleanField(default=False)

    haircare = models.BooleanField(default=False)

    journaling = models.BooleanField(default=False)

    mood = models.CharField(max_length=50)

class HomeCare(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    bed = models.BooleanField(default=False)

    desk = models.BooleanField(default=False)

    dishes = models.BooleanField(default=False)

    cleaning = models.BooleanField(default=False)

    duration = models.IntegerField(default=0)

