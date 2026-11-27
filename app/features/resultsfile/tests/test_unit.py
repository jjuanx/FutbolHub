"""Unit tests for the resultsfile feature — pure logic, no Flask app, no database."""

import pytest

from app.features.hubfile.models import Hubfile
from app.features.resultsfile.models import ResultsFile

pytestmark = pytest.mark.unit


def test_results_file_repr_uses_its_id():
    assert repr(ResultsFile(id=3, data_set_id=1)) == "ResultsFile<3>"


def test_results_file_keeps_its_number_of_matches():
    assert ResultsFile(number_of_matches=190).number_of_matches == 190


def test_results_file_matches_are_unknown_until_computed():
    assert ResultsFile().number_of_matches is None


def test_results_file_holds_its_hubfiles():
    hubfile = Hubfile(name="jornadas.csv", checksum="abc", size=10)
    results_file = ResultsFile(files=[hubfile])
    assert results_file.files == [hubfile]
    assert hubfile.results_file is results_file
