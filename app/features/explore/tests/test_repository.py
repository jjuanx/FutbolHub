"""Repository-level tests for explore — the dataset search query against the DB."""

from datetime import datetime

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import Author, DataSet, DSMetaData, DSMetrics, PublicationType
from app.features.explore.repositories import ExploreRepository
from app.features.featuremodel.models import FeatureModel, FMMetaData

pytestmark = pytest.mark.repository


def _owner():
    user = User.query.filter_by(email="owner@example.com").first()
    if user is None:
        user = User(email="owner@example.com")
        user.set_password("ownerpass")
        db.session.add(user)
        db.session.flush()
    return user


def _make_dataset(
    title,
    description="a description",
    author_name="Anonymous Author",
    tags="",
    created_at=None,
    publication_type=PublicationType.JOURNAL_ARTICLE,
    dataset_doi="10.1234/default",
    with_feature_model=True,
    competition=None,
    season=None,
    country=None,
    teams=None,
    number_of_matches=None,
    number_of_teams=None,
):
    ds_metrics = None
    if number_of_matches is not None or number_of_teams is not None:
        ds_metrics = DSMetrics(
            number_of_matches=number_of_matches,
            number_of_teams=number_of_teams,
        )
        db.session.add(ds_metrics)
        db.session.flush()

    ds_meta_data = DSMetaData(
        title=title,
        description=description,
        publication_type=publication_type,
        dataset_doi=dataset_doi,
        tags=tags,
        ds_metrics_id=ds_metrics.id if ds_metrics else None,
        competition=competition,
        season=season,
        country=country,
        teams=teams,
        number_of_matches=number_of_matches,
        number_of_teams=number_of_teams,
    )
    db.session.add(ds_meta_data)
    db.session.flush()
    db.session.add(Author(name=author_name, affiliation="Some University", ds_meta_data_id=ds_meta_data.id))
    dataset = DataSet(
        user_id=_owner().id,
        ds_meta_data_id=ds_meta_data.id,
        created_at=created_at or datetime(2024, 1, 1),
    )
    db.session.add(dataset)
    db.session.flush()
    if with_feature_model:
        fm_meta_data = FMMetaData(
            uvl_filename=f"{title.lower().replace(' ', '_')}.uvl",
            title=title,
            description=description,
            publication_type=publication_type,
            tags=tags,
        )
        db.session.add(fm_meta_data)
        db.session.flush()
        db.session.add(FeatureModel(data_set_id=dataset.id, fm_meta_data_id=fm_meta_data.id))
    db.session.commit()
    return dataset


def _seed_corpus():
    """Three searchable datasets plus two the query is expected to drop."""
    _make_dataset(
        title="Smart Home",
        description="home automation product line",
        author_name="Alice Doe",
        tags="iot,home",
        created_at=datetime(2024, 1, 1),
        publication_type=PublicationType.JOURNAL_ARTICLE,
        competition="LaLiga",
        season="2024-25",
        country="España",
        teams=["Sevilla FC", "Real Betis"],
        number_of_matches=380,
        number_of_teams=20,
    )
    _make_dataset(
        title="Car Configurator",
        description="vehicle variability",
        author_name="Bob Roe",
        tags="automotive",
        created_at=datetime(2024, 2, 1),
        publication_type=PublicationType.BOOK,
        competition="Bundesliga",
        season="2024-25",
        country="Germany",
        teams=["Bayern Munich", "Borussia Dortmund"],
        number_of_matches=306,
        number_of_teams=18,
    )
    _make_dataset(
        title="Home Banking",
        description="finance product line",
        author_name="Carol Poe",
        tags="finance",
        created_at=datetime(2024, 3, 1),
        publication_type=PublicationType.JOURNAL_ARTICLE,
        competition="Segunda División",
        season="2024-25",
        country="España",
        teams=["Málaga CF", "Cádiz CF"],
        number_of_matches=462,
        number_of_teams=22,
    )
    # Never returned: the query requires a non-null dataset_doi.
    _make_dataset(title="Draft Home", dataset_doi=None, created_at=datetime(2024, 4, 1))
    # Never returned: the query inner-joins feature models.
    _make_dataset(title="Modelless Home", with_feature_model=False, created_at=datetime(2024, 5, 1))


def _titles(datasets):
    return [dataset.ds_meta_data.title for dataset in datasets]


def test_blank_query_returns_every_eligible_dataset_newest_first(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        results = ExploreRepository().filter("")
        assert _titles(results) == ["Home Banking", "Car Configurator", "Smart Home"]


def test_whitespace_only_query_behaves_like_a_blank_query(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreRepository().filter("   ")) == ["Home Banking", "Car Configurator", "Smart Home"]


def test_query_narrows_results_to_matching_datasets(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("banking")) == ["Home Banking"]
        assert _titles(repository.filter("home")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("nothingmatchesthis")) == []


def test_query_matches_author_name_case_insensitively(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("alice")) == ["Smart Home"]
        assert _titles(repository.filter("ALICE")) == ["Smart Home"]


def test_query_matches_tags(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreRepository().filter("automotive")) == ["Car Configurator"]


def test_query_is_normalized_for_accents_and_punctuation(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("hóme")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("¿home?!")) == ["Home Banking", "Smart Home"]


def test_multiple_words_are_combined_with_or(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        results = ExploreRepository().filter("banking automotive")
        assert _titles(results) == ["Home Banking", "Car Configurator"]


def test_oldest_sorting_reverses_the_result_order(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("home", sorting="oldest")) == ["Smart Home", "Home Banking"]
        assert _titles(repository.filter("home", sorting="newest")) == ["Home Banking", "Smart Home"]


def test_datasets_without_a_doi_or_a_feature_model_are_never_returned(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("draft")) == []
        assert _titles(repository.filter("modelless")) == []


def test_publication_type_narrows_the_results(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", publication_type="book")) == ["Car Configurator"]
        assert _titles(repository.filter("", publication_type="article")) == ["Home Banking", "Smart Home"]


def test_unknown_publication_type_is_ignored(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", publication_type="any")) == _titles(
            repository.filter("", publication_type="not-a-publication-type")
        )


def test_tags_narrow_the_results(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", tags=["iot"])) == ["Smart Home"]
        assert _titles(repository.filter("", tags=["automotive", "finance"])) == ["Home Banking", "Car Configurator"]
        assert _titles(repository.filter("", tags=["nonexistent"])) == []


def test_tags_combine_with_the_query(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        # "home" alone matches two datasets; the tag narrows them to one.
        assert _titles(repository.filter("home")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("home", tags=["iot"])) == ["Smart Home"]


def test_multi_tags_from_form_string_or_list(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", tags="automotive, finance")) == ["Home Banking", "Car Configurator"]
        assert _titles(repository.filter("", tags=["iot, finance"])) == ["Home Banking", "Smart Home"]


def test_filter_by_dataset_metrics_matches_and_teams(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()

        # Filtro por número de partidos (306, 380, 462)
        assert _titles(repository.filter("", min_matches=380)) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("", max_matches=380)) == ["Car Configurator", "Smart Home"]
        assert _titles(repository.filter("", min_matches=350, max_matches=400)) == ["Smart Home"]
        assert _titles(repository.filter("", min_matches=500)) == []

        # Filtro por número de equipos (18, 20, 22)
        assert _titles(repository.filter("", min_teams=20)) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("", max_teams=20)) == ["Car Configurator", "Smart Home"]
        assert _titles(repository.filter("", min_teams=19, max_teams=21)) == ["Smart Home"]
        assert _titles(repository.filter("", min_teams=24)) == []


def test_tags_and_metrics_combine_with_domain_filters(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()

        # España tiene Smart Home (20 equipos, 380 partidos) y Home Banking (22 equipos, 462 partidos)
        assert _titles(
            repository.filter(
                "",
                country="España",
                tags="iot, finance",
                min_teams=20,
                max_matches=400,
            )
        ) == ["Smart Home"]

        assert _titles(
            repository.filter(
                "",
                country="España",
                min_matches=400,
                team="Málaga CF",
            )
        ) == ["Home Banking"]
