from .models import Lap

def lapFormating(lap: Lap):
    return {
        'id': lap.id,
        'session': lap.session.id,
        'time': lap.time,
        'compound': lap.compound.name,
        'date': lap.date,
        'temperature': lap.temperature,
        'comments': lap.comments,
        'fuel': lap.fuel,
        'tyrePressure': {
            'frontRight': lap.tyre_pressure_fr,
            'frontLeft': lap.tyre_pressure_fl,
            'rearRight': lap.tyre_pressure_rr,
            'rearLeft': lap.tyre_pressure_rl
        },
        'tyreTemperatures': {
            'frontRight': lap.tyre_temperature_fr,
            'frontLeft': lap.tyre_temperature_fl,
            'rearRight': lap.tyre_temperature_rr,
            'rearLeft': lap.tyre_temperature_rl
        },
        'usure_plaquette': lap.usure_plaquette,
        'lap_type': lap.lap_type,
        'lap_index_session': lap.lap_index_session,
        'lap_index_tyre': lap.lap_index_tyre,
        'sectors': {
            'sector1': lap.sector1,
            'sector2': lap.sector2,
            'sector3': lap.sector3
        },
        'tc_level': lap.tc_level,
        'abs_level': lap.abs_level,
        'valid': lap.valid_lap,
        'tyre_set': lap.tyre_set,
        'driver': lap.session.driver.name,
        'car': lap.session.car.name,
        'track': lap.session.track.name,
    }