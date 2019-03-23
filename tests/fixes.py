# Module for fixing errors in the meta data
from latlon_utils import get_country, get_climate
import requests
from itertools import starmap
import pandas as pd
import pytest


def get_elevation(points):
    query = ('https://api.open-elevation.com/api/v1/lookup?locations=' +
             '|'.join(starmap('{},{}'.format, points)))
    r = requests.get(query).json()
    # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values
    return elevation


@pytest.mark.dbfix
def fix_country(meta, meta_row, meta_file, commit_fixes, local_repo,
                skip_ci):
    country = get_country(meta_row.Latitude, meta_row.Longitude)
    current = getattr(meta_row, 'Country', '')
    if country != current:
        message = "Changed country from %s to %s" % (current, country)
        print(message)
        meta.loc[meta_row.name, 'Country'] = country
        meta.to_csv(str(meta_file), sep='\t')
        if commit_fixes:
            local_repo.index.add([meta_file.name])
            local_repo.index.commit(
                ("[%s]: %s" % (meta_row.name, message)) +
                ('\n\n[skip ci]' if skip_ci else ''))


@pytest.mark.dbfix
def fix_elevation(meta, meta_file, commit_fixes, local_repo, skip_ci):
    try:
        samples = meta[meta.Elevation.isnull()].index.values
    except AttributeError:
        samples = meta.index.values
    if len(samples):
        message = "Set elevation for %s" % samples
        print(message)
        points = meta.loc[samples, ['Latitude', 'Longitude']].values
        elev = get_elevation(points)
        meta.loc[samples, 'Elevation'] = elev
        meta.to_csv(str(meta_file), sep='\t')
        if commit_fixes:
            local_repo.index.add([meta_file.name])
            local_repo.index.commit(
                message + ('\n\n[skip ci]' if skip_ci else ''))
    else:
        pytest.skip("All elevations already specified")


@pytest.mark.dbfix
def fix_temperature(meta, meta_file, commit_fixes, local_repo, skip_ci):
    try:
        samples = meta[meta.Temperature.isnull()].index.values
    except AttributeError:
        samples = meta.index.values
    if len(samples):
        message = "Set temperature from WorldClim v2 for %s" % samples
        print(message)
        temperature = get_climate(
            *meta.loc[samples, ['Latitude', 'Longitude']].values.T,
            variables=['tavg'])
        meta.loc[samples, 'Temperature'] = list(map(
            ','.join, temperature.values.astype(str)))
        meta.to_csv(str(meta_file), sep='\t')
        if commit_fixes:
            local_repo.index.add([meta_file.name])
            local_repo.index.commit(
                message + ('\n\n[skip ci]' if skip_ci else ''))


@pytest.mark.dbfix
def fix_precipitation(meta, meta_file, commit_fixes, local_repo, skip_ci):
    try:
        samples = meta[meta.Precipitation.isnull()].index.values
    except AttributeError:
        samples = meta.index.values
    if len(samples):
        message = "Set temperature from WorldClim v2 for %s" % samples
        print(message)
        precip = get_climate(
            *meta.loc[samples, ['Latitude', 'Longitude']].values.T,
            variables=['prec'])
        meta.loc[samples, 'Precipitation'] = list(map(
            ','.join, precip.values.astype(str)))
        meta.to_csv(str(meta_file), sep='\t')
        if commit_fixes:
            local_repo.index.add([meta_file.name])
            local_repo.index.commit(
                message + ('\n\n[skip ci]' if skip_ci else ''))
