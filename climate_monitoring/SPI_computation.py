import os
import numpy as np
import xarray as xr
from pathlib import Path
from loguru import logger
from xclim.indices import standardized_precipitation_index

from climate_monitoring.map_generator import map_computation
from tests.config.ParseConfigFiles import ParseSPIData


def compute_SPI(dict_config: dict, dict_config_map: dict, input_path: str, output_path: str | Path,
                output_path_map: str | Path, launch_year: int, format_netcdf: str):
    ''' Compute SPI data and save the file in a repo.
        > dict_config:
            - dict of all the information contained in the yaml file for the SPI part

        > launch_year:
            - year of computation

        For more information about the other parameters, check:
        https://xclim.readthedocs.io/en/stable/indices.html#xclim.indices.standardized_precipitation_index

        Args:
            dict_config [dict]
            dict_config_map [dict]
            input_path [str]
            output_path [str or Path]
            output_path_map [str or Path]
            launch_year [int]

        Return:
            None
    '''

    resultat = []
    input_data, climdex, units, map_creator_list, start_periode, \
        end_periode, spi_period, func, freq, method, loc = ParseSPIData(dict_config)

    years = np.arange(start_periode, launch_year+1, 1)

    logger.info(f'Open netcdf files from {input_path} for years {start_periode} - {years[-1]}')
    for year in years:
        ds = xr.open_dataset(f"{input_path}/{year}/{climdex}/{climdex}_{input_data}_VALUES.nc", engine='netcdf4')
        resultat.append(ds)
        global_ds = xr.concat(resultat, dim=('time'))

    pr = global_ds[climdex]
    pr.attrs.update(units)

    for month, create_map in zip(spi_period, map_creator_list):
        SPI_array = standardized_precipitation_index(pr,
                                                     freq=freq,
                                                     window=month,
                                                     dist=func,
                                                     method=method,
                                                     fitkwargs={"floc": loc},
                                                     cal_start=f'{start_periode}-01-01',
                                                     cal_end=f'{end_periode}-12-31'
                                                     )

        SPI_array = SPI_array.drop_vars('prob_of_zero')
        SPI_array = SPI_array.rename('SPI')
        del SPI_array.attrs['time_indexer']
        del SPI_array.attrs['calibration_period']
        SPI_array = SPI_array.assign_attrs({'start_calibration_period': start_periode})
        SPI_array = SPI_array.assign_attrs({'end_calibration_period': end_periode})

        filepath = f'{output_path}/SPI/{launch_year}/'
        os.makedirs(filepath, exist_ok=True)
        logger.info(f'Save {month}-month SPI file calculated in {filepath}')
        SPI_ds = SPI_array.to_dataset(promote_attrs=True)
        SPI_ds = SPI_ds.sel(time=slice(SPI_ds.time.values[-12], SPI_ds.time.values[-1]))
        SPI_ds.to_netcdf(f'{filepath}/{month}-month_SPI_VALUES.nc', 'w', format_netcdf, engine='netcdf4')

        if create_map is True:
            map_computation(SPI_ds, dict_config_map, f'{month}-month_SPI_VALUES', output_path_map)
