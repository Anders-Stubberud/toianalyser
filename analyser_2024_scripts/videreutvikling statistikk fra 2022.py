import os
import utils
import polars as pl

YEARS = [2021, 2022, 2023, 2024]

DF_CONVOYS = pl.read_csv(utils.path_bil_tilhenger_matching)

DF_ALL_VEHICLE_DATA = pl.concat([
    pl.read_csv(
        os.path.join(utils.path_dir_kjøretøysdata, kjøretøysdata),
        truncate_ragged_lines=True,
        ignore_errors=True,
        separator=';',
        decimal_comma=True
    ).with_columns([
        pl.col('Distanse (km)').str.replace_all(',', '.').cast(pl.Float64).alias('Distanse (km)'),
        pl.col('Snitthastighet').str.replace_all(',', '.').cast(pl.Float64).alias('Snitthastighet')
    ]).filter(
        (pl.col('Distanse (km)') >= 20) & 
        (pl.col('Snitthastighet') >= 20) &    
        (pl.col('Distanse (km)').is_not_null()) &               
        (pl.col('Distanse (km)').is_not_nan())
    )
    for kjøretøysdata in os.listdir(utils.path_dir_kjøretøysdata) if kjøretøysdata.endswith('.csv')
], how='vertical_relaxed')

SCHEMA = [
    'Ekvipasje', 
    'Snitt 2021', 'Snitt 2022', 'Snitt 2023', 'Snitt 2024',
    'Median 2021', 'Median 2022', 'Median 2023', 'Median 2024',
    'Min 2021', 'Min 2022', 'Min 2023', 'Min 2024',
    'Max 2021', 'Max 2022', 'Max 2023', 'Max 2024'
]

def get_df_convoy(convoy):
    vins_in_convoy = DF_CONVOYS.filter(pl.col('ekvipasje') == convoy).select('VIN_lastebil').to_series().to_list()
    return DF_ALL_VEHICLE_DATA.filter(pl.col('VIN').is_in(vins_in_convoy))

def get_df_convoy_year(df_convoy, year):
    df_convoy_datetime = df_convoy.with_columns(
        pl.col("Dato").str.strptime(pl.Datetime, format="%m/%d/%Y %I:%M:%S %p").alias("date")
    )
    return df_convoy_datetime.filter(df_convoy_datetime["date"].dt.year() == year)

def convert_to_numeric(df, column):
    return df.with_columns(
        pl.col(column).cast(pl.Float64, strict=False).alias(column)
    )

def get_avg_property(df_convoy_year, property):
    df_convoy_year = convert_to_numeric(df_convoy_year, property)
    return df_convoy_year.select(pl.col(property).mean()).item()

def get_median_property(df_convoy_year, property):
    df_convoy_year = convert_to_numeric(df_convoy_year, property)
    return df_convoy_year.select(pl.col(property).median()).item()

def get_min_property(df_convoy_year, property):
    df_convoy_year = convert_to_numeric(df_convoy_year, property)
    return df_convoy_year.select(pl.col(property).min()).item()

def get_max_property(df_convoy_year, property):
    df_convoy_year = convert_to_numeric(df_convoy_year, property)
    return df_convoy_year.select(pl.col(property).max()).item()

for property, alias in utils.PROPERTIES_AND_ALIASES:

    all_data = []

    for convoy in utils.alle_ekvipasjer:
        data_convoy = [convoy]

        df_convoy = get_df_convoy(convoy)
        df_convoy_years = [get_df_convoy_year(df_convoy, year) for year in YEARS]

        avg_property_years = [get_avg_property(df_convoy_year, property) for df_convoy_year in df_convoy_years]
        median_property_years = [get_median_property(df_convoy_year, property) for df_convoy_year in df_convoy_years]
        min_property_years = [get_min_property(df_convoy_year, property) for df_convoy_year in df_convoy_years]
        max_property_years = [get_max_property(df_convoy_year, property) for df_convoy_year in df_convoy_years]

        data_convoy.extend(avg_property_years + median_property_years + min_property_years + max_property_years)

        all_data.append(data_convoy)

    df_result = pl.DataFrame(all_data, schema=SCHEMA)
    output_path = os.path.join(utils.path_dir_resultater_videreutvikling_statistikk_2022, f'{alias}.csv')
    df_result.write_csv(output_path)
