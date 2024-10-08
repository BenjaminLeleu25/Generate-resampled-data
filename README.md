# Generate-resampled-data  

This repository allows you resample hourly (or others) satellite data in NetCDF format into daily, monthly or annual.  
There are 2 different parts:  
- how to use these functions? (explain in a Notebook)
- how to create a configuration file and linked the functions we created before?  
The functions are grouped in the repository _climate_monitoring_ and some example in _Notebook_.

## How to acces C3S data thanks to the API?
On the website of Copernicus, you can find the skeleton of the API (follow this [link](https://cds.climate.copernicus.eu/how-to-api)).  

You have to create an account on Copernicus climate data store.  

> For the part _Install the CDS API key_, you need to create a file in $HOME/.cdsapirc and copy/paste the lines _url_ and _key_ corresponding

Via VSCode:
- open new file
- paste the line of the _CDS API key_
- save it in home/codespace/ (par exemple, /home/... in general) with the name .cdsapirc