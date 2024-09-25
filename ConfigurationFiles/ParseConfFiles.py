def ParseSPIData(dict_config: dict)
    units = dict_config['units']
    start_period = dict_config['start_period']
    end_period = dict_config['end_period']
    spi_duration = dict_config['spi_duration']
    func = dict_config['function']
    freq = dict_config['freq']
    method = dict_config['method']
    loc = dict_config['floc_param']

    return units, start_period, end_period, spi_duration, \
        func, freq, method, loc 