from django.shortcuts import render
from simracing.inertial_mapping import inertial_mapping
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Car, Track, Driver, Session, Lap
import h5py
import simracing.data_analysis.classifier as classifier
import numpy as np

from django.db.models import Avg, StdDev, Sum

from .data_formating import lapFormating

#create a new session in the database with the request's information
@api_view(['GET', 'POST'])
def newSession(request):
    if request.method == 'POST':
        driver = Driver.objects.get(name=request.data.get('driver'))
        track = Track.objects.get(name=request.data.get('track'))
        car = Car.objects.get(name=request.data.get('car'))
        session = Session.objects.get_or_create(driver=driver, track=track, car=car, weather=request.data.get('weather'), session_type='Started')
        print('Session created')
        return Response({'id': Session.objects.order_by('id').last().id})
    return Response({'error': 'Invalid request'})
    
#return the list of cars, tracks and drivers in the database   
@api_view(['GET'])
def getTrackCarDriver(request):
    cars = [car.name for car in Car.objects.all()]
    tracks = [track.name for track in Track.objects.all()]
    drivers = [driver.name for driver in Driver.objects.all()]
    print('Info returned')
    return Response({'cars': cars, 'tracks': tracks, 'drivers': drivers})

#return the list of laps for a specific track
@api_view(['GET'])
def getLaps(request):
    query = Lap.objects.all()
    if request.GET.get('track') != "all":
        track_id = Track.objects.get(name=request.GET.get('track')).id
        query = query.filter(session__track=track_id)
    if request.GET.get('car') != "all":
        car_id = Car.objects.get(name=request.GET.get('car')).id
        query = query.filter(session__car=car_id)
    if request.GET.get('driver') != "all":
        driver_id = Driver.objects.get(name=request.GET.get('driver')).id
        query = query.filter(session__driver=driver_id)
    if request.GET.get('session') != "all":
        query = query.filter(session=request.GET.get('session'))
    laps = [{'id': lap.id, 'time': lap.time, 'track': lap.session.track.name, 'car': lap.session.car.name, 'driver': lap.session.driver.name, 'fuel': lap.fuel, 'compound': lap.compound.name, 'temp': lap.temperature, 'type': lap.lap_type, 'index_session': lap.lap_index_session} for lap in query]
    return Response({'laps': [lapFormating(lap) for lap in query.all()]})

#return the laps statistics for a corresponding configuration of track, driver and car
@api_view(['GET'])
def prepareRace(request):
    track = Track.objects.get(name = request.GET.get('track'))
    sessions = Session.objects.filter(track = track)
    laps = Lap.objects.filter(session__track__name = request.GET.get('track'), session__driver__name = request.GET.get('driver'), session__car__name = request.GET.get('car'))
    meanTime = laps.aggregate(Avg('time'))['time__avg']
    stdTime = laps.aggregate(StdDev('time'))['time__stddev']
    totalTime = int(meanTime) * int(request.GET.get('laps'))
    return Response({'totalTime': totalTime, 'meanTime': meanTime, 'stdTime': stdTime})

#return the list of sessions
@api_view(['GET'])
def getSession(request):
    sessions = Session.objects.all()
    for session in sessions:
        laps = Lap.objects.filter(session=session)
        completed = (laps.filter(lap_type="Completed").count() == 0)
        if completed:
            session.session_type = "Completed"
            session.save()
        else:
            session.session_type = "Started"
            session.save()
    sessions = [{'id': session.id, 'driver': session.driver.name, 'track': session.track.name, 'car': session.car.name, 'weather': session.weather, 'type': session.session_type, 'lap_count': Lap.objects.filter(session=session).count()} for session in Session.objects.all()]
    return Response({'sessions': sessions})

#update the lap_type of a lap
@api_view(['POST'])
def updateLap(request):
    lap = Lap.objects.get(id=request.data.get('id'))
    lap.lap_type = request.data.get('lap_type')
    lap.save()
    print('Lap updated')
    return Response({'message': 'Lap updated successfully'})

#give back the information of a session
@api_view(['GET'])
def getSessionInfo(request):
    session = Session.objects.get(id=request.GET.get('id'))
    laps = [{'lap': lapFormating(lap), 'driver': session.driver.name} for lap in Lap.objects.filter(session=session)]
    return Response({'laps': laps, 'track': session.track.name, 'weather': session.weather, 'car': session.car.name})

#give back statistics of a session
@api_view(['GET'])
def getSessionStat(request):
    session = Session.objects.get(id=request.GET.get('id'))
    laps = Lap.objects.filter(session=session)
    meanTime = laps.aggregate(Avg('time'))['time__avg']
    stdTime = laps.aggregate(StdDev('time'))['time__stddev']
    totalTime = laps.aggregate(Sum('time'))['time__sum']
    return Response({
        'totalTime': totalTime,
        'meanTime': meanTime,
        'stdTime': stdTime
        })

@api_view(['GET'])
def getLapInfo(request):
    lap = Lap.objects.get(id=request.GET.get('id'))
    session = Session.objects.get(id=lap.session.id)
    return Response({
        'lap': lapFormating(lap),
        'session': {
            'track': session.track.name,
            'car': session.car.name,
            'driver': session.driver.name,
            'weather': session.weather
        }
    })

@api_view(['GET'])
def getLapTelemetry(request):
    lap = Lap.objects.get(id=request.GET.get('id'))
    h5_file = h5py.File(lap.telemetry_file, 'r')
    if 'position' in h5_file.keys():
        position = h5_file['position'][:]
    else:
        position = None
    dataset = {
        'speed': np.round(h5_file['speed'][:], 2),
        'brake': h5_file['brake'][:],
        'throttle': h5_file['throttle'][:],
        'gear': h5_file['gear'][:],
        'rpm': h5_file['rpm'][:],
        'distance': h5_file['distance'][:],
        'tyre_temperature_fl': h5_file['tyre_temperature'][:, 0],
        'tyre_temperature_fr': h5_file['tyre_temperature'][:, 1],
        'tyre_temperature_rl': h5_file['tyre_temperature'][2, :],
        'tyre_temperature_rr': h5_file['tyre_temperature'][3, :],
        'position': position[:, :],
    }
    reports = {}
    for key in list(dataset.keys())[:-5]:
        reports[key] = {
            'mean': round(np.mean(h5_file[key][:]), 2),
            'stddev': round(np.std(h5_file[key][:]), 2),
            'min': round(np.min(h5_file[key][:]), 2),
            'max': round(np.max(h5_file[key][:]), 2)
        }
    h5_file.close()
    return Response({
        'dataset': dataset,
        'report': reports
    })

@api_view(['GET'])
def getEstimationLap(request):
    estimated_lap_type = classifier.predict_lap_type(request.GET.get('id'), Session.objects.get(id=request.GET.get('session_id')).track.id)
    return Response({
        'lap_type': estimated_lap_type
    })

@api_view(['POST'])
def doInertialMapping(request):
    print("In POST request")
    try:
        inertial_mapping(request.data.get('lap_id'))
    except Exception as e:
        return Response({'error': f'Inertial mapping failed: {str(e)}'})
    return Response({'message': 'Inertial mapping completed successfully'})
