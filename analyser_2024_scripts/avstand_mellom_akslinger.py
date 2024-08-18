import utils
import os
import polars as pl
import numpy as np
import matplotlib.pyplot as plt

INDEX_AXLE_INFORMATION = 8
INDEX_GROSS_WEIGHT = 9
INDEX_START_AXLE_WEIGHT = 10
LIMIT_ESAL_VALUE = 10
INDEX_DATE = 1

datasets_bwim = (
    os.path.join('..', 'WIM-data', '202210 okt22 14-20', 'Sorbryn_2022_newer_nswd_v0,9.csv'),
    # os.path.join('..', 'WIM-data', '202210 okt22 14-20', 'Sorbryn_2022_newer_nswd_v10022023.csv'),
    os.path.join('..', 'WIM-data', '202210 okt22 14-20', 'Tangensvingen_2022_newer_nswd.csv'),
    # os.path.join('..', 'WIM-data', '202210 okt22 14-20', 'Tangensvingen_2022_newer_nswd_v0,9.csv'),
    # os.path.join('..', 'WIM-data', '202210 okt22 14-20', 'Tangensvingen_2022_newer_nswd_v27122022.csv'),
    os.path.join('..', 'WIM-data', '202302 feb23 21-27', 'Sorbryn_feb2023_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202302 feb23 21-27', 'Tangensvingen_feb2023_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202304 april23 17-23', 'Sorbryn_april2023_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202304 april23 17-23', 'Tangensvingen_April2023_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202310 okt23 16-22', 'Sorbryn_oktober2023_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202310 okt23 16-22', 'Tangensvingen_Oktober2023_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202402 feb24 26feb-3mars', 'Sorbryn_february2024_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202402 feb24 26feb-3mars', 'Tangensvingen_Februari2024_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202404 april24 18-24', 'Sorbryn_april2024_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', '202404 april24 18-24', 'Tangensvingen_April2024_newer_nswd.csv'),
    os.path.join('..', 'WIM-data', 'Fredrikstadbrua', 'Fredrikstad_february2024_newer_nswd.csv')
)

datasets_kistler = (
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20160808-31_Kistler Øysand_4913151-export(1).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20160901-30_Kistler Øysand_4913151-export(2).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20161001-31_Kistler Øysand_4913151-export(3)-fixed.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20161101-30_Kistler Øysand_4913151-export(4).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20161201-31_Kistler Øysand_4913151-export(5).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20170101-31_Kistler Øysand_4913151-export(6).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20170201-28_Kistler Øysand_4913151-export(7).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20170301-31_Kistler Øysand_4913151-export(8).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20170401-05_Kistler Øysand_4913151-export(9)-fixed.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180316_1.3.1_Kistler Øysand_4913151-export(24).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180401-30_Kistler Øysand_4796227-export(12).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180501-31(21-26)_Kistler Øysand_4796227-export(13).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180601-30(11-30)_Kistler Øysand_4796227-export(14).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180701-31(01-11)_Kistler Øysand_4796227-export(15).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180801-31(10-31)_Kistler Øysand_4796227-export(16).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Øysand', '20180901-30_Kistler Øysand 4796227-export(17).csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Skibotn', 'combinedFiles_E8_2018_kalibrert_4okt.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Skibotn', 'combinedFiles_E8_2019.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Skibotn', 'combinedFiles_E8_2020.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20150513-20150531_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20150601-20150630_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20150701-20150731_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20150801-20150831_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20150901-20150930_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20151001-20151031_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20151101-20151130_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20151201-20151231_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20160101-20160131_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20160201-20160229_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20160301-20160331_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20160401-20160430_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Verdal', '20160501-20160531_Kistler Verdal 4796227.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Aanestad', '20221014-20 Kistler_R3_ostg.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Aanestad', '20221014-20 Kistler_R3_vestg.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Aanestad', '20240123-20240612_R3 østgående.csv'),
    os.path.join('..', 'WIM-data', 'Kistler_Aanestad', '20240122-20240612_R3 vestgående.csv'),
    # os.path.join('..', 'WIM-data', 'Kistler_Aanestad', '20231001-20240123_Aanestad_Ostgående.csv'),
    # os.path.join('..', 'WIM-data', 'Kistler_Aanestad', '20231001-20240123_Aanestad_Vestgående.csv')
)

def bwim_row_iteration(row):
    dic = {}
    axle = 0
    num_axles = row[7]         
    index_distance_axles = 11 + num_axles
    for i in range(index_distance_axles, index_distance_axles + num_axles - 1):
        axle += 1
        try:
            dic[axle] = row[i]
        except:
            return False, False
    return dic, num_axles

def distance_and_weight_bwim(location):
    axles_and_distances = {i : [[] for _ in range(2, i + 1)] for i in range(2,10)}

    for dataset in datasets_bwim:
        if not location.lower() in dataset.lower():
            continue
        data = os.path.join(utils.current_dir, dataset)
        df = pl.read_csv(data, has_header=False, truncate_ragged_lines=True, ignore_errors=True, separator=';', decimal_comma=True)

        for row in df.iter_rows():        
            distances, num_axles = bwim_row_iteration(row)
            if not distances:
                continue
            for axle in range(num_axles - 1):
                if float(str(distances[axle + 1]).replace(',', '.')) > 10:
                    continue
                axles_and_distances[num_axles][axle].append(float(str(distances[axle + 1]).replace(',', '.'))) 

    for key, item in axles_and_distances.items():
        for dist, distances in enumerate(item):
            # Plot the histogram
            plt.hist(distances, bins=100)

            # Set the x-axis label
            plt.xlabel('Distanse, meter')

            # Set the y-axis label
            plt.ylabel('Antall passeringer')

            # Create the title (same as filename)
            title = f'{location}, {key}-akslet kjøretøy, distanse fra aksel {dist + 1} til aksel {dist + 2}'
            plt.title(title)

            # Create the filename
            filename = f'{title}.png'

            # Save the plot
            plt.savefig(os.path.join('resultater_akseldistanser_bwim', location, filename))

            # Clear the plot for the next iteration
            plt.clf()
                    

# distance_and_weight_bwim('sorbryn')
distance_and_weight_bwim('tangensvingen')
