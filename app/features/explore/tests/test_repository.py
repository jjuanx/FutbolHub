"""Repository-level tests for explore — the dataset search query against the DB."""

from datetime import datetime

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
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
    author_affiliation="Some University",
    author_orcid="0000-0000-0000-0000",
    tags="",
    created_at=None,
    publication_type=PublicationType.JOURNAL_ARTICLE,
    dataset_doi="10.1234/default",
    with_feature_model=True,
):
    ds_meta_data = DSMetaData(
        title=title,
        description=description,
        publication_type=publication_type,
        dataset_doi=dataset_doi,
        tags=tags,
    )
    db.session.add(ds_meta_data)
    db.session.flush()
    db.session.add(
        Author(
            name=author_name,
            affiliation=author_affiliation,
            orcid=author_orcid,
            ds_meta_data_id=ds_meta_data.id,
        )
    )
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
        author_affiliation="Universidad de Sevilla",
        author_orcid="0000-0001-2345-6789",
        tags="iot,home",
        created_at=datetime(2024, 1, 15, 10, 30),
        publication_type=PublicationType.JOURNAL_ARTICLE,
    )
    _make_dataset(
        title="Car Configurator",
        description="vehicle variability",
        author_name="Bob Roe",
        author_affiliation="MIT",
        author_orcid="0000-0002-9876-5432",
        tags="automotive",
        created_at=datetime(2024, 2, 10, 14, 0),
        publication_type=PublicationType.BOOK,
    )
    _make_dataset(
        title="Home Banking",
        description="finance product line",
        author_name="Carol Poe",
        author_affiliation="Universidad de Málaga",
        author_orcid="0000-0003-1111-2222",
        tags="finance",
        created_at=datetime(2024, 3, 20, 18, 45),
        publication_type=PublicationType.JOURNAL_ARTICLE,
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


def test_filter_by_author_matches_name_affiliation_and_orcid(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        # Por nombre de autor
        assert _titles(repository.filter("", author="Alice")) == ["Smart Home"]
        # Por afiliación (incluyendo coincidencia sin tilde: "Malaga" -> "Universidad de Málaga")
        assert _titles(repository.filter("", author="Sevilla")) == ["Smart Home"]
        assert _titles(repository.filter("", author="Malaga")) == ["Home Banking"]
        assert _titles(repository.filter("", author="Universidad")) == ["Home Banking", "Smart Home"]
        # Por ORCID
        assert _titles(repository.filter("", author="0000-0002-9876-5432")) == ["Car Configurator"]
        # Sin coincidencias
        assert _titles(repository.filter("", author="Inexistente")) == []


def test_filter_by_specific_author_fields(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", author_name="Carol")) == ["Home Banking"]
        assert _titles(repository.filter("", author_affiliation="MIT")) == ["Car Configurator"]
        assert _titles(repository.filter("", author_orcid="0000-0001-2345-6789")) == ["Smart Home"]
        assert _titles(repository.filter("", author_name="Carol", author_affiliation="MIT")) == []


def test_filter_by_date_range_boundaries_and_empty_ranges(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        # Límite exacto del día (incluye horas dentro del día límite)
        assert _titles(repository.filter("", date_from="2024-01-15", date_to="2024-02-10")) == [
            "Car Configurator",
            "Smart Home",
        ]
        # Un día después del primero y un día antes del tercero
        assert _titles(repository.filter("", date_from="2024-01-16", date_to="2024-03-19")) == [
            "Car Configurator",
        ]
        # Solo límite inferior (date_from)
        assert _titles(repository.filter("", date_from="2024-02-10")) == [
            "Home Banking",
            "Car Configurator",
        ]
        # Solo límite superior (date_to)
        assert _titles(repository.filter("", date_to="2024-02-10")) == [
            "Car Configurator",
            "Smart Home",
        ]
        # Rango vacío (sin datasets en ese intervalo)
        assert _titles(repository.filter("", date_from="2025-01-01", date_to="2025-12-31")) == []
        # Rango invertido (date_from > date_to) devuelve lista vacía
        assert _titles(repository.filter("", date_from="2024-03-20", date_to="2024-01-15")) == []
        # Fechas vacías o con formato inválido se ignoran sin lanzar error
        assert len(repository.filter("", date_from="", date_to="fecha-invalida")) == 3
