import os
import re
from pathlib import Path

import unidecode
from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import or_

from app.features.dataset.csv_validator import validate_results_csv
from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel, FMMetaData


def _norm(value) -> str:
    if value is None:
        return ""
    return unidecode.unidecode(str(value).strip()).lower()


def _extract_dataset_attr(dataset: DataSet, *attr_names: str) -> str:
    """Obtiene un atributo de dominio desde el dataset o sus metadatos."""
    targets = [dataset, getattr(dataset, "ds_meta_data", None)]
    for target in targets:
        if target is None:
            continue
        for attr in attr_names:
            val = getattr(target, attr, None)
            if val is not None and str(val).strip():
                return str(val).strip()
    return ""


def _extract_dataset_teams(dataset: DataSet) -> list[str]:
    """Obtiene todos los equipos que juegan algún partido en el dataset."""
    teams: list[str] = []

    # 1. Equipos explícitos en metadatos o dataset
    for target in (dataset, getattr(dataset, "ds_meta_data", None)):
        if target is None:
            continue
        raw_teams = getattr(target, "teams", None) or getattr(target, "equipos", None)
        if isinstance(raw_teams, str):
            teams.extend(t.strip() for t in raw_teams.split(",") if t.strip())
        elif isinstance(raw_teams, (list, tuple, set)):
            teams.extend(str(t).strip() for t in raw_teams if str(t).strip())

    # 2. Partidos en memoria / relación del modelo nuevo
    raw_matches = getattr(dataset, "matches", None)
    if callable(raw_matches):
        raw_matches = raw_matches()
    for match in raw_matches or []:
        local = getattr(match, "local", None) or (match.get("local") if isinstance(match, dict) else None)
        visitante = getattr(match, "visitante", None) or (match.get("visitante") if isinstance(match, dict) else None)
        if local:
            teams.append(str(local).strip())
        if visitante:
            teams.append(str(visitante).strip())

    # 3. Ficheros CSV asociados al dataset en disco
    working_dir = os.getenv("WORKING_DIR", "")
    user_id = getattr(dataset, "user_id", None)
    dataset_id = getattr(dataset, "id", None)
    base_dir = (
        Path(working_dir) / "uploads" / f"user_{user_id}" / f"dataset_{dataset_id}"
        if user_id is not None and dataset_id is not None
        else None
    )

    csv_paths: list[Path] = []
    files = dataset.files() if hasattr(dataset, "files") and callable(dataset.files) else []
    for f_obj in files or []:
        f_path = getattr(f_obj, "file_path", None) or getattr(f_obj, "path", None)
        if f_path and Path(str(f_path)).is_file():
            csv_paths.append(Path(str(f_path)))
            continue
        f_name = getattr(f_obj, "name", None) or getattr(f_obj, "filename", None)
        if f_name and str(f_name).lower().endswith(".csv") and base_dir is not None:
            candidate = base_dir / str(f_name)
            if candidate.is_file():
                csv_paths.append(candidate)

    if not csv_paths and base_dir is not None and base_dir.is_dir():
        csv_paths.extend(sorted(base_dir.glob("*.csv")))

    for csv_path in csv_paths:
        validation = validate_results_csv(csv_path)
        teams.extend(validation.teams)

    return teams


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(
        self,
        query="",
        sorting="newest",
        publication_type="any",
        tags=[],
        competition="",
        season="",
        country="",
        team="",
        **kwargs,
    ):
        # Normalize and remove unwanted characters
        normalized_query = unidecode.unidecode(query or "").lower()
        cleaned_query = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query)

        filters = []
        for word in cleaned_query.split():
            filters.append(DSMetaData.title.ilike(f"%{word}%"))
            filters.append(DSMetaData.description.ilike(f"%{word}%"))
            filters.append(Author.name.ilike(f"%{word}%"))
            filters.append(Author.affiliation.ilike(f"%{word}%"))
            filters.append(Author.orcid.ilike(f"%{word}%"))
            filters.append(FMMetaData.uvl_filename.ilike(f"%{word}%"))
            filters.append(FMMetaData.title.ilike(f"%{word}%"))
            filters.append(FMMetaData.description.ilike(f"%{word}%"))
            filters.append(FMMetaData.publication_doi.ilike(f"%{word}%"))
            filters.append(FMMetaData.tags.ilike(f"%{word}%"))
            filters.append(DSMetaData.tags.ilike(f"%{word}%"))

        datasets = (
            self.model.query.join(DataSet.ds_meta_data)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .filter(or_(*filters))
            .filter(DSMetaData.dataset_doi.isnot(None))  # Exclude datasets with empty dataset_doi
        )

        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        if tags:
            datasets = datasets.filter(or_(*(DSMetaData.tags.ilike(f"%{tag}%") for tag in tags)))

        # Order by created_at
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        else:
            datasets = datasets.order_by(self.model.created_at.desc())

        results = datasets.all()
        unique_results = []
        seen_ids = set()
        for ds in results:
            if ds.id not in seen_ids:
                seen_ids.add(ds.id)
                unique_results.append(ds)

        comp_filter = _norm(competition or kwargs.get("competicion"))
        season_filter = _norm(season or kwargs.get("temporada"))
        country_filter = _norm(country or kwargs.get("pais"))
        team_filter = _norm(team or kwargs.get("equipo"))

        if comp_filter or season_filter or country_filter or team_filter:
            domain_filtered = []
            for ds in unique_results:
                if comp_filter:
                    ds_comp = _norm(_extract_dataset_attr(ds, "competition", "competicion"))
                    if comp_filter not in ds_comp:
                        continue
                if season_filter:
                    ds_season = _norm(_extract_dataset_attr(ds, "season", "temporada"))
                    if season_filter not in ds_season:
                        continue
                if country_filter:
                    ds_country = _norm(_extract_dataset_attr(ds, "country", "pais"))
                    if country_filter not in ds_country:
                        continue
                if team_filter:
                    ds_teams = [_norm(t) for t in _extract_dataset_teams(ds)]
                    if not any(team_filter in t for t in ds_teams):
                        continue
                domain_filtered.append(ds)
            unique_results = domain_filtered

        return unique_results
