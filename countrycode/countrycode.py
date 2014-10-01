import re
import os
import pandas as pd
import copy
import warnings
from functools import reduce

pkg_dir, pkg_filename = os.path.split(__file__)

data_path = os.path.join(pkg_dir, "data", "countrycode_data.csv")
data = pd.read_csv(data_path, encoding='utf-8')
data.iso2c[data.iso3c == 'NAM'] = 'NA'

# Make regexes case insensitive and ignore text after the end
data.regex =  '(?i)' + data.regex + '.*'

# Replace NaN in regex with pattern that won't match anything
# See http://stackoverflow.com/questions/1723182/a-regex-that-will-never-be-matched-by-anything?lq=1
nevermatch = r'(?!x)x'
data.regex[pd.isnull(data.regex)] = nevermatch


data_path = os.path.join(pkg_dir, "data", "cown2014.csv")
cown = pd.read_csv(data_path)

data_path = os.path.join(pkg_dir, "data", "cowc2014.csv")
cowc = pd.read_csv(data_path)


def countrycode(sourcevar, origin, destination, warn=True):

    '''Convert to and from 12 country code schemes. Uses regular expressions to
    detect country names and standardize them. Assign region/continent
    descriptors.

    Parameters
    ----------

    sourcevar : string, list, or pandas Series of strings containing
        country names or country codes to convert
    origin : string
        name of the coding scheme of origin
    destination : string
        name of the coding scheme you wish to obtain
    warn : logical
        Whether to print elements from sourcevar for which no match was found

    Notes
    -----

    Valid origin strings:

        * regex : match names in sourcevar
        * label_name : abbreviated country names based on UN standard
        * un_name : official UN country names
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

    Valid destination string:

        * Any valid origin string
        * region : World Bank geographic region descriptor
        * continent : Name of continent
    '''

    if type(sourcevar) in (list, str):
        in_names = pd.Series(sourcevar)

    elif type(sourcevar) is pd.core.series.Series:
        in_names = sourcevar

    else:

        raise TypeError('sourcevar must be string, list, or pandas series')


    # Create dictionary for replacement
    dictionary = dict(zip(data[origin], data[destination]))

    # Prepare output vector
    destination_vector = pd.Series([None] * len(in_names))

    # All but regex-based operations
    if origin != 'regex':

        for k in dictionary.keys():
            destination_vector[in_names.str.match(unicode(k))] = dictionary[k]

    else:

        # Keep track of duplicate matches
        dup_matches = {}

        # For each regex in the dictionary, find matches
        for k in dictionary.keys():
            matches = in_names.str.match(k, as_indexer=True)
            destination_vector[matches] = dictionary[k]

            # Keep track of keys matched more than once
            if sum(matches) > 1:
                dup_matches[k] = list(in_names[matches])
            # end if
        # end for

    # Handle the warnings
    if warn:
        nomatch = in_names[pd.isnull(destination_vector)]
        if len(nomatch) > 0:
            warnings.warn('Some values were not matched:\n' +
                              '; '.join(s.encode('utf-8') for s in nomatch.values))

        if origin == 'regex':
            dup_text = '\n'.join('{} = {}'.format(key, val) for (key, val) in dup_matches.items())
            warnings.warn('Some regex patterns matched more than one value:\n' +
                              dup_text)
    # end if warn

    if type(sourcevar) == list:
        destination_vector = destination_vector.tolist()
    elif type(sourcevar) == str:
        destination_vector = destination_vector[0]

    return destination_vector
