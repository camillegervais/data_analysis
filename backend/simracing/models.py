from django.db import models
import datetime

# Create your models here.
class Compound(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

class Track(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    length = models.FloatField(default=0)
    country = models.CharField(max_length=255)
    turn = models.IntegerField(default=0)

class Car(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year = models.IntegerField(default=0)
    weight = models.FloatField(default=0)
    power = models.FloatField(default=0)
    torque = models.FloatField(default=0)
    top_speed = models.FloatField(default=0)

class Driver(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField(default=0)

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    weather = models.CharField(max_length=255, default="")
    session_type = models.CharField(max_length=255, default='Started')#'Started' -> 'Checked'

class Lap(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    time = models.FloatField(default=0)
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    date = models.DateField(default=0)
    temperature = models.FloatField(default=0)
    comments = models.TextField()
    fuel = models.IntegerField(default=0)
    tyre_pressure_fr = models.FloatField(default=0)
    tyre_pressure_fl = models.FloatField(default=0)
    tyre_pressure_rr = models.FloatField(default=0)
    tyre_pressure_rl = models.FloatField(default=0)
    tyre_temperature_fr = models.IntegerField(default=0)
    tyre_temperature_fl = models.IntegerField(default=0)
    tyre_temperature_rr = models.IntegerField(default=0)
    tyre_temperature_rl = models.IntegerField(default=0)
    usure_plaquette = models.FloatField(default=0)
    lap_type = models.CharField(max_length=255, default='Completed')#'Completed'/'Chrono'/'Crash'/'Cool down'/'Outlap'
    lap_index_session = models.IntegerField(default=1)
    lap_index_tyre = models.IntegerField(default=1)
    sector1 = models.IntegerField(default=0)
    sector2 = models.IntegerField(default=0)
    sector3 = models.IntegerField(default=0)
    tc_level = models.IntegerField(default=0)
    abs_level = models.IntegerField(default=0)
    valid_lap = models.BooleanField(default=True)
    tyre_set = models.IntegerField(default=0)
    telemetry_file = models.FileField(upload_to='telemetry_files/', null=True, blank=True)  # Nouveau champ pour le fichier HDF5

    


