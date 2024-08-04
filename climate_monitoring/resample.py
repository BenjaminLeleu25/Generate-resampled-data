'''
Author: Benjamin LELEU
Date: 8 August 2024
'''

import xarray as xr
import numpy as np


def resample(dataset: xr.Dataset, method: str, dim: str, offset: int, 
             duration: str | None, parameter=None) -> xr.Dataset:
    """
        Resamples a dataset, temporally, with the desired period. This resampling can
        be apply to the entire dataset with the same function (MAX, MIN, MEAN or SUM) (by default)
        or the user can select 1 parameter only. So the dataset returned will only have
        1 parameter. So the input can be a dataset with a lot of parameters and the output
        is a dataset with all these resampled parameters or only 1 resampled parameter.

        > 'dataset' [xarray.Dataset] - Input dataset

        > 'method' [str] - method used for the resampling.
                           Can be 'MAX', 'MIN', 'MEAN', 'SUM' or 'CUMSUM'

        > 'dim' [str] - dimension for the resampling

        > 'duration' [str] - duration of the resampling
          Minutes: from 1 to inf + min (example: '15min')
            --> interpolation for the data
          Hours: from 1 to inf + h (example: '12h')
          Days: from 1 to inf + D (example: '1D')
          Months: from 1 to inf + M (example: '2M')
          Years: from 1 to inf + Y (example: '1Y')

          For more info: https://docs.xarray.dev/en/stable/generated/xarray.cftime_range.html#xarray.cftime_range

        > 'offset' [int] - used to shift the time of the dataset from local to UTC (GMT) time

        > 'parameter' [str] - name of one parameter of the dataset that we want to resample.
        ----------
        Args:
            dataset [xarray.Dataset or xarray.DataArray]
            method [str]
            dim [str]
            duration [str or None]
            offset [int]
            parameter [None or str]
        ----------
        Raises:
            TypeError  - raise an error about the type of the argument entered
            ValueError - raise an error if the number of argument not the one expected
        ----------
        Return:
            ds [Dataset]
    """

    dataset_func_dict = {'MAX': xr.Dataset.max,
                         'MIN': xr.Dataset.min,
                         'MEAN': xr.Dataset.mean,
                         'SUM': xr.Dataset.sum,
                         'CUMSUM': xr.Dataset.cumsum,
                         'P10': lambda x, dim: xr.Dataset.quantile(x, q=0.1, dim='time'),
                         'P90': lambda x, dim: xr.Dataset.quantile(x, q=0.9, dim='time')}

    dataarray_func_dict = {'MAX': xr.DataArray.max,
                           'MIN': xr.DataArray.min,
                           'MEAN': xr.DataArray.mean,
                           'SUM': xr.DataArray.sum,
                           'CUMSUM': xr.DataArray.cumsum,
                           'P10': lambda x, dim: xr.DataArray.quantile(x, q=0.1, dim='time'),
                           'P90': lambda x, dim: xr.DataArray.quantile(x, q=0.9, dim='time')}

    if isinstance(dataset, xr.Dataset) is False and isinstance(dataset, xr.DataArray) is False:
        raise TypeError(f'The object is not a dataset or dataraay. Type: {type(dataset)}\
                        Please enter xarray.Dataset or xarray.DataArray type.')

    func = dataset_func_dict[method]

    if parameter is not None:
        dataset = dataset[parameter]
        func = dataarray_func_dict[method]

    if method == 'P10' or 'P90':
        dataset = dataset.chunk(dict(time=-1))

    ds = dataset.resample({'time': duration}, offset=f'{offset}h', origin='start_day').map(func, dim=dim)
    xr.set_options(keep_attrs=True)
    ds.attrs.update({'Infos': 'Resample data',
                     'Offset': offset})

    if isinstance(ds, xr.Dataset) is False:
        ds = ds.to_dataset()

    return ds
