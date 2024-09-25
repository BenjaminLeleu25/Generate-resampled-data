import os
import numpy as np
import xarray as xr
from pathlib import Path
from loguru import logger
from xclim.indices import standardized_precipitation_index

from ConfigurationFiles.ParseConfFiles import ParseSPIData


def compute_SPI(dict_config: dict,
                input_path: str | Path,
                filename: str,
                launch_year: int) -> xr.Dataset:
    ''' Compute SPI data and save the file in a repo.
        > dict_config:
            - dict of all the information contained in the yaml file for the SPI part

        > input_path:
            - path of the valid NetCDF file for SPI computation.
              It must have values within the interval [start_period, end_period] (minimum)

        > filename:
            - name of the NetCDF file to open

        > launch_year:
            - year of computation

        For more information about the other parameters, check:
        https://xclim.readthedocs.io/en/stable/indices.html#xclim.indices.standardized_precipitation_index

        Args:
            dict_config [dict]
            input_path [str]
            launch_year [int]

        Return:
            SPI_ds [xr.Dataset]
    '''

    resultat = []
    units, start_period, end_period, spi_period, \
        func, freq, method, loc = ParseSPIData(dict_config)

    logger.info(f'Open netcdf files from {input_path}')
    ds = xr.open_dataset(f"{input_path}/{filename}", engine='netcdf4')

    # ds = ds[climdex]
    ds.attrs.update(units)

    for month in spi_period:
        SPI_array = standardized_precipitation_index(ds,
                                                     freq=freq,
                                                     window=month,
                                                     dist=func,
                                                     method=method,
                                                     fitkwargs={"floc": loc},
                                                     cal_start=start_period,
                                                     cal_end=end_period
                                                     )

        SPI_array = SPI_array.drop_vars('prob_of_zero')
        SPI_array = SPI_array.rename('SPI')
        del SPI_array.attrs['time_indexer']
        del SPI_array.attrs['calibration_period']
        SPI_array = SPI_array.assign_attrs({'start_calibration_period': start_period})
        SPI_array = SPI_array.assign_attrs({'end_calibration_period': end_period})
        SPI_ds = SPI_array.to_dataset(promote_attrs=True)
        # Extract the last year only
        # SPI_ds = SPI_ds.sel(time=slice(SPI_ds.time.values[-12], SPI_ds.time.values[-1]))

    return SPI_ds