# region Imports
from geopy.distance import geodesic
import polars as pl
from utils import find_csv_files_with_keywords, paths_posisjonsdata, path_vin_kjøretøytype
from math import inf
from datetime import timedelta, datetime
# endregion

# region Konstanter
filepaths_sørbryn = find_csv_files_with_keywords(['sørbryn', 'sorbryn'])

coordinates_sørbryn = (60 + 46/60 + 20.3/3600, 11 + 18/60 + 31.3/3600)

cols = [
    'ID', 'Tid', 'Retning', 'Felt', 'Hastighet(km/t)', 
    'Antall_moduler', 'Kjøretøyklasse', 'Antall_akslinger', 
    'Akselgrupper', 'Totalvekt'] + ['a' + str(x) for x in range(10, 35)
]
# endregion

# region DF Sørbryn, dataframe med all data fra sørbryn
df_sørbryn = pl.concat(
    [
        (
            lambda df: df.with_columns(
                [pl.lit(None).alias(col) for col in cols[len(df.columns):]]
            ).rename(
                dict(zip(df.columns, cols[:len(df.columns)]))
            )
        )(
            pl.read_csv(
                filepath, 
                has_header=False, 
                separator=';', 
                decimal_comma=True, 
                truncate_ragged_lines=True, 
                ignore_errors=True
            )
        )
        for filepath in filepaths_sørbryn
    ],
    how='vertical_relaxed'
)
# endregion

# region Tidsintervallene sørbryn-sensoren har vært i drift
df_sørbryn = df_sørbryn.with_columns(
    pl.col("Tid").str.strptime(pl.Datetime, format="%Y-%m-%d-%H-%M-%S-%f").alias("parsed_date")
)

df_sørbryn = df_sørbryn.sort("parsed_date")

df_sørbryn = df_sørbryn.with_columns(
    (pl.col("parsed_date") - pl.col("parsed_date").shift(1)).alias("date_diff")
)

df_sørbryn = df_sørbryn.with_columns(
    (pl.col("date_diff") > pl.duration(days=1)).alias("is_gap")
)

df_sørbryn = df_sørbryn.with_columns(
    pl.col("is_gap").cum_sum().alias("span_id")
)

date_spans = df_sørbryn.group_by("span_id").agg(
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
# endregion

# region DF position (i samme tidsspenn som sensoren opererer og innenfor 1 km fra sensoren)
def read_and_filter(filepath):
    df = pl.read_csv(filepath, truncate_ragged_lines=True, ignore_errors=True)
    df = df.with_columns(
        pl.col('Dato').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f").alias("parsed_timestamp")
    )
    
    date_mask = None
    for start, end in date_intervals_sensor_running:
        mask = (pl.col('parsed_timestamp') >= start) & (pl.col('parsed_timestamp') <= end)
        if date_mask is None:
            date_mask = mask
        else:
            date_mask = date_mask | mask
    
    df = df.filter(date_mask)
    
    df = df.filter(pl.struct(["Latitude", "Longitude"]).map_elements(
        lambda row: geodesic(coordinates_sørbryn, (float(row["Latitude"]), float(row["Longitude"]))).km <= 1, 
        return_dtype=pl.Boolean
    ))
    
    return df

df_position = pl.concat([read_and_filter(filepath) for filepath in paths_posisjonsdata], how='vertical_relaxed')
# endregion

# region Henter ut rader der kjøretøyene er nærmest sensoren, samt estimert passeringstidspunkt ved sensoren
df_position = df_position.sort(['VIN', 'Dato'])

previous_vin = previous_previous_vin = None
previous_distance_to_sensor = previous_previous_distance_to_sensor = inf
previous_row = previous_previous_row = None

closest_registrations = []

for row in df_position.iter_rows(named=True):

    current_vin = row['VIN']
    lat, lon = float(row["Latitude"]), float(row["Longitude"])
    current_distance_to_sensor = geodesic(coordinates_sørbryn, (lat, lon)).km

    # nærmeste den passeringen kom sensoren
    if current_vin == previous_vin == previous_previous_vin and previous_previous_distance_to_sensor > previous_distance_to_sensor < current_distance_to_sensor:

        try:

            retning = float(row['Retning'])
            hastighet = float(row['Hastighet'].replace(',', '.'))
            punkt_nord_for_sensor = lat > coordinates_sørbryn[0]

            estimert_tidsforskjell_timer = previous_distance_to_sensor / hastighet

            try:
                date = datetime.strptime(previous_row['Dato'], '%Y-%m-%d %H:%M:%S.%f')
            except:
                date = datetime.strptime(previous_row['Dato'][:-1], '%Y-%m-%d %H:%M:%S.%f') # noen har 7 desimaler til millisekunder, det breaker datetime

            if 90 <= retning <= 270: # kjører sørover
                if punkt_nord_for_sensor:
                    estimert_passering = date + timedelta(hours=estimert_tidsforskjell_timer)
                else:
                    estimert_passering = date - timedelta(hours=estimert_tidsforskjell_timer)
            else: # må da være nordgående
                if punkt_nord_for_sensor:
                    estimert_passering = date - timedelta(hours=estimert_tidsforskjell_timer)
                else:
                    estimert_passering = date + timedelta(hours=estimert_tidsforskjell_timer)

            previous_row.update({
                'Distanse til sensor' : previous_distance_to_sensor,
                'Estimert passeringstidspunkt' : estimert_passering
            })

            closest_registrations.append(previous_row)

        except:
            pass

    previous_previous_row = previous_row
    previous_row = row
    previous_previous_vin = previous_vin
    previous_vin = current_vin
    previous_previous_distance_to_sensor = previous_distance_to_sensor
    previous_distance_to_sensor = current_distance_to_sensor

df_closest_registrations = pl.DataFrame(closest_registrations)
# endregion

# region Filtrerer så det kun er tilhengere (tilhengerne må jo dras rundt av en bil, er her kun interessert i bielene når de drar rundt på henger)
vin_kjøretøytype = pl.read_csv(path_vin_kjøretøytype)

vin_tilhengere = vin_kjøretøytype.filter(pl.col('type') == 'tilhenger').select(pl.col('VIN')).to_series().to_list()

df_closest_registrations = df_closest_registrations.filter(pl.col('VIN').is_in(vin_tilhengere))
# endregion

def can_be_converted_to_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

print(df_closest_registrations.filter(pl.col('Aktuell vekt').apply(can_be_converted_to_float)).select(['VIN', 'Latitude', 'Longitude', 'Dato', 'Estimert passeringstidspunkt', 'Hastighet', 'Aktuell vekt']))
