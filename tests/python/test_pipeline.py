import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch

# Tilføj rod-mappen til sys.path så vi kan importere scripts.pipeline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.pipeline import calculate_qpr, load_data_from_db, run_pipeline

def test_calculate_qpr():
    # Test for standard QPR calculation
    row = {'points': 90, 'price': 100}
    assert calculate_qpr(row) == 0.9000

    # Test for bonus QPR calculation (>93 points)
    row_bonus = {'points': 95, 'price': 100}
    assert calculate_qpr(row_bonus) == 1.9000

    # Test for Edge case: Zero price (skal undgås i data extraction, men funktionelt check)
    with pytest.raises(ZeroDivisionError):
        calculate_qpr({'points': 90, 'price': 0})


@patch('scripts.pipeline.DB_PATH', 'data/retailers_wine_aggregator.db')
def test_load_data_from_db():
    # Dette kræver at mock-databasen eksisterer
    if not os.path.exists('data/retailers_wine_aggregator.db'):
        pytest.skip("Test database findes ikke lokalt. Denne test springes over.")
        
    df = load_data_from_db()
    
    assert not df.empty, "Dataframe bør ikke være tom"
    assert 'id' in df.columns
    assert 'price' in df.columns
    assert 'points' in df.columns
    assert 'vibe_category' in df.columns
    
    # Test at pris aldrig er NaN eller 0 (baseret på query)
    assert not df['price'].isnull().any()
    assert (df['price'] > 0).all()


@patch('scripts.pipeline.OUTPUT_DIR', 'tests/python/tmp_mdx')
def test_run_pipeline_integration():
    if not os.path.exists('data/retailers_wine_aggregator.db'):
        pytest.skip("Test database findes ikke lokalt. Denne test springes over.")
        
    # Kør pipelinen med en mock OUTPUT_DIR
    os.makedirs('tests/python/tmp_mdx', exist_ok=True)
    
    try:
        run_pipeline()
        
        # Verificer at filer blev oprettet
        files = os.listdir('tests/python/tmp_mdx')
        assert len(files) > 0, "Ingen MDX filer blev genereret."
        
        # Tjek indholdet af en tilfældig fil
        with open(os.path.join('tests/python/tmp_mdx', files[0]), 'r', encoding='utf-8') as f:
            content = f.read()
            assert '---' in content, "MDX mangler frontmatter"
            assert 'qpr:' in content
            assert 'price:' in content
            
    finally:
        # Oprydning
        for f in os.listdir('tests/python/tmp_mdx'):
            os.remove(os.path.join('tests/python/tmp_mdx', f))
        os.rmdir('tests/python/tmp_mdx')
