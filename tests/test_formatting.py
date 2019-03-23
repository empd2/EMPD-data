# Test the formatting of the data
import pytest

def test_trailing_spaces(meta_row):
    meta_row = meta_row.astype(str)
    assert (meta_row.str.strip() == meta_row).all()


def test_newline_chars(meta_row):
    meta_row = meta_row.astype(str)
    assert (meta_row.str.replace('\n', ' ').str.replace('\r', ' ') ==
            meta_row).all()


@pytest.mark.parametrize('doi_field', ['DOI1', 'DOI2', 'DOI3', 'DOI4', 'DOI5'])
def test_doi(meta_row, doi_field):
    if meta_row.notnull()[doi_field]:
        doi = meta_row.copy(True)[doi_field]

        for patt in ['https://doi.org/', 'http://dx.doi.org/', 'doi: ',
                     'doi.org/', 'DOI: ', 'DOI ', 'doi:', ' ',
                     'https://link.springer.com/article/']:
            doi = doi.replace(patt, '')
        assert doi == meta_row.loc[doi_field]
    else:
        pytest.skip("%s field empty specified" % doi_field)
