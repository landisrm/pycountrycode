import re
import os
import pandas as pd
from copy import copy
from functools import reduce

pkg_dir, pkg_filename = os.path.split(__file__)
data_path = os.path.join(pkg_dir, "data", "countrycode_data.csv")
data = pd.read_csv(data_path)
data.iso2c[data.iso3c == 'NAM'] = 'NA'
data_path = os.path.join(pkg_dir, "data", "cown2014.csv")
cown = pd.read_csv(data_path)
data_path = os.path.join(pkg_dir, "data", "cowc2014.csv")
cowc = pd.read_csv(data_path)

def countrycode(codes=['DZA', 'CAN'], origin='iso3c', target='country_name'):
    '''Convert to and from 12 country code schemes. Use regular expressions to
    detect country names and standardize them. Assign region/continent
    descriptors.

    Parameters
    ----------

    codes : string or list of strings
        country names or country codes to convert
    origin : string
        name of the coding scheme of origin
    target : string
        name of the coding scheme you wish to obtain

    Notes
    -----

    Valid origin codes:

        * country_name
        * iso2c : ISO 2 character
        * iso3c : ISO 3 character
        * iso3n : ISO 3 numeric
        * cown : Correlates of War numeric
        * cowc : Correlates of War character
        * un : United Nations
        * wb : World Bank
        * imf : International Monetary Fund
        * fips104 : FIPS 10-4 U.S. government geographic data
        * fao : Food & Agriculture Organization of the U.N.
        * ioc : International Olympic Committee

    Valid target codes:

        * Any valid origin code
        * region : World Bank geographic region descriptor
        * continent : Name of continent
    '''

    if type(codes) in (list, str):
        input_codes = pd.Series(codes)
    elif type(codes) == pd.core.series.Series:
        input_codes = codes
    else:
        raise TypeError('codes must be string, list, or pandas series')

    if origin == 'country_name':
        origin = 'regex'
        data['regex'] = '(?i)'+ data['regex']

    dictionary = data[[origin, target]].dropna()
    dictionary = dict(zip(data[origin], data[target]))
    if origin != 'regex':
        output_codes = input_codes.copy()
        for k in dictionary.keys():
            output_codes[input_codes.str.match(str(k))] = dictionary[k]
    else:
        output_codes = input_codes.replace(dictionary, regex=True)

    if type(codes) == list:
        output_codes = output_codes.tolist()
    elif type(codes) == str:
        output_codes = output_codes[0]

    return output_codes

def countryyear(code='iso3c', years=list(range(1990,2013))):
    if not years:
        if code == 'cown':
            out = cown
        else:
            out = cowc
    else:
        codes = data[code]
        out = pd.DataFrame(list(zip(list(range(len(codes))), codes)), columns=['idx', code])
        out = out.dropna()
        try:
            out[code][out[code]==''] = None
        except:
            pass
        out = [out.copy() for x in years]
        for i,v in enumerate(years):
            out[i]['year'] = v
        out = reduce(lambda x,y: pd.concat([x,y]), out)
    return out
