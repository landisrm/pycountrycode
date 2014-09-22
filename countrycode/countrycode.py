import re
import os
import pandas as pd
import copy
from functools import reduce

pkg_dir, pkg_filename = os.path.split(__file__)
data_path = os.path.join(pkg_dir, "data", "countrycode_data.csv")
data = pd.read_csv(data_path)
data.iso2c[data.iso3c == 'NAM'] = 'NA'
data_path = os.path.join(pkg_dir, "data", "cown2014.csv")
cown = pd.read_csv(data_path)
data_path = os.path.join(pkg_dir, "data", "cowc2014.csv")
cowc = pd.read_csv(data_path)


def check_1pattern(string, pattern):
    '''Compares a string and a regex pattern.  
    Returns True if a match is found, False otherwise '''

    # First check to make sure pattern is not nan
    if not pd.isnull(pattern):
        # compare string to pattern
        rx = re.compile(pattern)
        m = rx.match(string)
    else:
        m = None

    return True if m is not None else False
    
def check_1string(string, pattern_list):
    '''Compares a string to a list of regex patterns.  
    Returns True if any patterns match, False otherwise'''
    
    matches = [check_1pattern(string, pat) for pat in pattern_list]

    return True if any(matches) else False

def find_nomatch(string_list, pattern_list):
    '''Compares a list of strings to a list of patterns.
    Returns a boolean pandas Series, of length len(string_list) indicating whether or not a match was found for each string in pattern_list.'''
    
    no_match = pd.Series([not check_1string(s, pattern_list) for s in string_list])

    return no_match

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
        # Make a deep copy.  Note that codes.copy(deep = True) doesn't seem to work.
        # Deep copy is necessary because if we change an element to NaN (see below)
        # we don't want that change reflected in the original series.
        input_codes = pd.Series(data=copy.deepcopy(codes.values.tolist()), 
                                index=codes.index.copy(),
                                name=codes.name)
    else:
        raise TypeError('codes must be string, list, or pandas series')

    # Why is it possible to specify country_name if what you really want is 
    # origin = 'regex'?  Seems like if origin == 'country_name', don't need 
    # to bother with regex.

    if origin == 'country_name':
        origin = 'regex'

    # if origin is 'regex', then test for countries which have no match.
    # replace their names with NaN in a temporary copy of input_codes.
    if origin == 'regex':
        # Replace NaN in regex with pattern that won't match anything
        # See http://stackoverflow.com/questions/1723182/a-regex-that-will-never-be-matched-by-anything?lq=1

        # First change NaNs in the regex patterns to an actual regex.
        nevermatch = r'(?!x)x'
        data.regex[pd.isnull(data.regex)] = nevermatch

        # Make the regexes case insensitive and ignore text before 
        # and after the match
        data['regex'] = '(?i).*'+ data['regex'] + '.*'

        # Find elements of input_codes which don't match any of the regexes
        no_match = find_nomatch(input_codes, data['regex'])
        input_codes[no_match] = None 
        # Prevents pd.Series.replace from returning the unmatched element.  Returns
        # NaN instead.
    
    # What does the first dictionary statement do?  isn't it immediately changed?
    #dictionary = data[[origin, target]].dropna()

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
