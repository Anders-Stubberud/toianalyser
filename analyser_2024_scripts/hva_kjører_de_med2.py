from geopy.distance import geodesic
import polars as pl
from utils import find_csv_files_with_keywords, paths_posisjonsdata, path_vin_kjøretøytype
import math
from datetime import timedelta, datetime
from typing import Optional, Tuple

filepath_aanestad_vest = 'c:\\toianalyser\\analyser_2024_scripts\\..\\WIM-data\\Kistler_Aanestad\\20231001-20240123_Aanestad_Vestgående.csv'
MAX_DISTANCE_SENSOR_KM = 2.5
coordinates_aanestad_vest_ish = (60.8721283,11.4429347)

def timeintervals_sensor_running(df: pl.DataFrame):
    df = df.with_columns(
        pl.col("StartTimeStr").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S%.f%z").alias("parsed_date")
    )

    df = df.sort("parsed_date")

    df = df.with_columns(
        (pl.col("parsed_date") - pl.col("parsed_date").shift(1)).alias("date_diff")
    )

    df = df.with_columns(
        (pl.col("date_diff") > pl.duration(days=1)).alias("is_gap")
    )

    df = df.with_columns(
        pl.col("is_gap").cum_sum().alias("span_id")
    )

    date_spans = df.group_by("span_id").agg(
        [
            pl.col("parsed_date").min().alias("first_date"),
            pl.col("parsed_date").max().alias("last_date")
        ]
    )

    date_spans = date_spans.with_columns(
        (pl.col("last_date") - pl.col("first_date")).alias("span_duration")
    )

    filtered_date_spans = date_spans.filter(
        pl.col("span_duration") > pl.duration(days=1)
    )

    date_intervals_sensor_running = filtered_date_spans.select(["first_date", "last_date"]).to_numpy()

    return date_intervals_sensor_running

# Posisjonspunkter innen MAX_DISTANCE_SENSOR_KM fra sensoren som ble registrert i samme tidsperiode som sensoren var i drift, og eventuelt i den retningen sensoren virker
def relevant_position_points(filepath, date_intervals, coordinates_sensor, direction=None):
    df = pl.read_csv(filepath, truncate_ragged_lines=True, ignore_errors=True)
    df = df.with_columns(
        pl.col('Dato').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f").alias("parsed_timestamp")
    )
    
    date_mask = None
    for start, end in date_intervals:
        mask = (pl.col('parsed_timestamp') >= start) & (pl.col('parsed_timestamp') <= end)
        if date_mask is None:
            date_mask = mask
        else:
            date_mask = date_mask | mask
    
    df = df.filter(date_mask)

    df = df.filter(pl.struct(["Latitude", "Longitude"]).map_elements(
        lambda row: geodesic(coordinates_sensor, (float(row["Latitude"]), float(row["Longitude"]))).km <= MAX_DISTANCE_SENSOR_KM, 
        return_dtype=pl.Boolean
    ))

    lower, upper = direction - 45 if direction - 45 >= 0 else 360 - direction - 45, (direction + 45) % 360

    if direction:
        df = df.filter((pl.col('Retning').cast(int) > lower) | (pl.col('Retning').cast(int) < upper)) # kjører i den retningen sensoren fanger opp 

    return df

# Posisjonspunktene som er punktet fra turen nærmest sensoren, fra periodene hvor sensorene var i drift, direction er for eksempelvis Aanestad vest for å kun fange vestgående trafikk
def closest_registrations_df(df_sensor: pl.DataFrame, coordinates_sensor: Tuple[float, float], direction: Optional[int]=None):

    def vehicle_is_heading_towards_sensor(start_lat, start_lon, direction, target_lat, target_lon):

        def dot_product(v1, v2):
            return v1[0] * v2[0] + v1[1] * v2[1]

        def calculate_target_vector(lat1, lon1, lat2, lon2):
            lat1_rad = degrees_to_radians(lat1)
            lon1_rad = degrees_to_radians(lon1)
            lat2_rad = degrees_to_radians(lat2)
            lon2_rad = degrees_to_radians(lon2)
            
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            magnitude = math.sqrt(dlat**2 + dlon**2)
            
            return (dlat / magnitude, dlon / magnitude)

        def degrees_to_radians(degrees):
            return degrees * math.pi / 180

        def direction_to_unit_vector(direction):
            rad = degrees_to_radians(direction)
            return (math.cos(rad), math.sin(rad))

        direction_vector = direction_to_unit_vector(direction)
        target_vector = calculate_target_vector(start_lat, start_lon, target_lat, target_lon)
        
        dp = dot_product(direction_vector, target_vector)
        
        return dp > 0

    date_intervals = timeintervals_sensor_running(df_sensor)
    df_position = pl.concat([relevant_position_points(filepath, date_intervals, coordinates_sensor, direction) for filepath in paths_posisjonsdata], how='vertical_relaxed').sort(['VIN', 'Dato'])

    previous_row = None
    previous_vin = previous_previous_vin = None
    previous_distance_to_sensor = previous_previous_distance_to_sensor = math.inf
    closest_registrations = []

    for row in df_position.iter_rows(named=True):

        current_vin = row['VIN']
        lat, lon = float(row["Latitude"]), float(row["Longitude"])
        current_distance_to_sensor = geodesic(coordinates_sensor, (lat, lon)).km

        # nærmeste den passeringen kom sensoren
        if current_vin == previous_vin == previous_previous_vin and previous_previous_distance_to_sensor > previous_distance_to_sensor < current_distance_to_sensor:
            direction = float(row['Retning'])
            speed = float(row['Hastighet'].replace(',', '.'))

            estimert_tidsforskjell_timer = previous_distance_to_sensor / speed

            try:
                date = datetime.strptime(previous_row['Dato'], '%Y-%m-%d %H:%M:%S.%f')
            except:
                date = datetime.strptime(previous_row['Dato'][:-1], '%Y-%m-%d %H:%M:%S.%f') # noen har 7 desimaler til millisekunder, det breaker datetime

            if vehicle_is_heading_towards_sensor(lat, lon, direction, coordinates_sensor[0], coordinates_sensor[1]):
                estimert_passering = date + timedelta(hours=estimert_tidsforskjell_timer)
            else:
                estimert_passering = date - timedelta(hours=estimert_tidsforskjell_timer)

            previous_row.update({
                'Distanse til sensor' : previous_distance_to_sensor,
                'Estimert passeringstidspunkt' : estimert_passering
            })

            closest_registrations.append(previous_row)

        previous_row = row
        previous_previous_vin = previous_vin
        previous_vin = current_vin
        previous_previous_distance_to_sensor = previous_distance_to_sensor
        previous_distance_to_sensor = current_distance_to_sensor

    df_closest_registrations = pl.DataFrame(closest_registrations)
    vin_tilhengere = pl.read_csv(path_vin_kjøretøytype).filter(pl.col('type') == 'tilhenger').select(pl.col('VIN')).to_series().to_list()

    return df_closest_registrations.filter(pl.col('VIN').is_in(vin_tilhengere)) if len(df_closest_registrations) >= 1 else None

# Behandler sensordaten i chunks fordi den opprinnelige df'en er så stor at den krasjer programmet
def analyze_in_chunks(filepath_sensor: str, coordinates_sensor: Tuple[float, float], direction: Optional[int] = None):
    dfs_results = []
    num_chunks = 10
    df = pl.read_csv(filepath_sensor, separator=';', skip_rows=6, has_header=True, truncate_ragged_lines=True, ignore_errors=True)
    total_len = len(df)
    chunk_size = total_len // num_chunks

    for i in range(num_chunks):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_chunks - 1 else total_len
        df_chunk = df[start:end]
        df_chunk_result = closest_registrations_df(df_chunk, coordinates_sensor, direction)
        if df_chunk_result is not None:
            dfs_results.append(df_chunk_result)

    df_result = pl.concat(dfs_results)

    return df_result

print(analyze_in_chunks(filepath_aanestad_vest, coordinates_aanestad_vest_ish, 250).select(['VIN', 'Latitude', 'Longitude', 'Dato', 'Estimert passeringstidspunkt', 'Hastighet', 'Aktuell vekt']))
