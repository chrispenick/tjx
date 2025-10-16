from tjx_style_demo.catalog import load_or_buildCatalog

def test_catalog():
    c=load_or_buildCatalog()
    assert isinstance(c,list) and c
