"""Builders shared by the resultsfile tests: persisted football datasets with their results files."""

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import DataSet, DSMetaData, DSMetrics, FootballDataSet, PublicationType
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile
from app.features.resultsfile.models import ResultsFile


def _meta(title):
    meta = DSMetaData(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
        ds_metrics=DSMetrics(),
    )
    db.session.add(meta)
    db.session.flush()
    return meta


@pytest.fixture
def make_user():
    def _make(email="owner@example.com"):
        user = User(email=email, password="secret")
        db.session.add(user)
        db.session.flush()
        return user

    return _make


@pytest.fixture
def make_football_dataset():
    """Persist a football dataset with one results file (one Hubfile each) per entry of ``files``."""

    def _make(user, title="LaLiga 2023-24", files=(("results.csv", 380),)):
        dataset = FootballDataSet(
            user_id=user.id,
            ds_meta_data_id=_meta(title).id,
            competition="LaLiga",
            country="España",
            season="2023-24",
            number_of_teams=20,
            data_source="https://www.football-data.co.uk",
        )
        for name, matches in files:
            dataset.results_files.append(
                ResultsFile(number_of_matches=matches, files=[Hubfile(name=name, checksum=f"sum-{name}", size=1024)])
            )
        db.session.add(dataset)
        db.session.commit()
        return dataset

    return _make


@pytest.fixture
def make_uvl_dataset():
    def _make(user, title="Feature models"):
        dataset = DataSet(user_id=user.id, ds_meta_data_id=_meta(title).id)
        dataset.feature_models.append(FeatureModel(files=[Hubfile(name="model.uvl", checksum="sum-uvl", size=512)]))
        db.session.add(dataset)
        db.session.commit()
        return dataset

    return _make
