import os
import re
from datetime import date, datetime, time
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


def _parse_int(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _parse_tags(raw_tags) -> list[str]:
    """Normaliza una lista de etiquetas o una cadena separada por comas."""
    if not raw_tags:
        return []
    if isinstance(raw_tags, str):
        return [t.strip() for t in raw_tags.split(",") if t.strip()]
    if isinstance(raw_tags, (list, tuple, set)):
        parsed = []
        for item in raw_tags:
            if isinstance(item, str):
                parsed.extend(t.strip() for t in item.split(",") if t.strip())
            elif item is not None:
                parsed.append(str(item).strip())
        return [t for t in parsed if t]
    return []


def _parse_date_boundary(value, end_of_day: bool = False) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.max if end_of_day else time.min)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
            return datetime.combine(parsed_date, time.max if end_of_day else time.min)
        except ValueError:
            try:
                return datetime.fromisoformat(cleaned)
            except ValueError:
                return None
    return None


def _author_matches_term(authors, term: str, field_name: str | None = None) -> bool:
    norm_term = _norm(term)
    if not norm_term:
        return True

    for author in authors or []:
        if field_name:
            raw_values = [getattr(author, field_name, "") or ""]
        else:
            raw_values = [
                getattr(author, "name", "") or "",
                getattr(author, "affiliation", "") or "",
                getattr(author, "orcid", "") or "",
            ]
        for val in raw_values:
            if norm_term in _norm(val):
                return True
    return False


def _extract_dataset_attr(dataset: DataSet, *attr_names: str) -> str:
    for target in (dataset, getattr(dataset, "ds_meta_data", None)):
        if target is None:
            continue
        for attr in attr_names:
            val = getattr(target, attr, None)
            if val is not None and str(val).strip():
                return str(val).strip()
    return ""


def _resolve_dataset_csv_paths(dataset: DataSet) -> list[Path]:
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
    return csv_paths


def _extract_dataset_teams(dataset: DataSet) -> list[str]:
    teams: list[str] = []
    for target in (dataset, getattr(dataset, "ds_meta_data", None)):
        if target is None:
            continue
        raw_teams = getattr(target, "teams", None) or getattr(target, "equipos", None)
        if isinstance(raw_teams, str):
            teams.extend(t.strip() for t in raw_teams.split(",") if t.strip())
        elif isinstance(raw_teams, (list, tuple, set)):
            teams.extend(str(t).strip() for t in raw_teams if str(t).strip())

    for csv_path in _resolve_dataset_csv_paths(dataset):
        validation = validate_results_csv(csv_path)
        teams.extend(validation.teams)

    return teams


def _extract_dataset_metrics(dataset: DataSet) -> tuple[int | None, int | None]:
    """Devuelve `(number_of_matches, number_of_teams)` del dataset."""
    meta = getattr(dataset, "ds_meta_data", None)
    metrics = getattr(meta, "ds_metrics", None) if meta is not None else None

    num_matches: int | None = None
    num_teams: int | None = None

    for source in (dataset, meta, metrics):
        if source is None:
            continue
        if num_matches is None:
            for attr in ("number_of_matches", "num_matches", "number_of_models"):
                parsed = _parse_int(getattr(source, attr, None))
                if parsed is not None:
                    num_matches = parsed
                    break
        if num_teams is None:
            for attr in ("number_of_teams", "num_teams", "number_of_features"):
                parsed = _parse_int(getattr(source, attr, None))
                if parsed is not None:
                    num_teams = parsed
                    break

    if num_teams is None:
        teams = _extract_dataset_teams(dataset)
        if teams:
            num_teams = len({t.casefold() for t in teams})

    if num_matches is None:
        csv_paths = _resolve_dataset_csv_paths(dataset)
        if csv_paths:
            num_matches = sum(validate_results_csv(p).valid_rows for p in csv_paths)

    return num_matches, num_teams


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(
        self,
        query="",
        sorting="newest",
        publication_type="any",
        tags=[],
        author="",
        date_from=None,
        date_to=None,
        competition="",
        season="",
        country="",
        team="",
        min_matches=None,
        max_matches=None,
        min_teams=None,
        max_teams=None,
        **kwargs,
    ):
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
            .filter(DSMetaData.dataset_doi.isnot(None))
        )

        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        parsed_tags = _parse_tags(tags)
        if parsed_tags:
            datasets = datasets.filter(or_(*(DSMetaData.tags.ilike(f"%{tag}%") for tag in parsed_tags)))

        start_dt = _parse_date_boundary(
            date_from if date_from is not None else kwargs.get("start_date"),
            end_of_day=False,
        )
        end_dt = _parse_date_boundary(
            date_to if date_to is not None else kwargs.get("end_date"),
            end_of_day=True,
        )
        if start_dt is not None:
            datasets = datasets.filter(self.model.created_at >= start_dt)
        if end_dt is not None:
            datasets = datasets.filter(self.model.created_at <= end_dt)

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

        author_term = (author or "").strip()
        author_name = (kwargs.get("author_name") or "").strip()
        author_affiliation = (kwargs.get("author_affiliation") or "").strip()
        author_orcid = (kwargs.get("author_orcid") or "").strip()

        comp_filter = _norm(competition or kwargs.get("competicion"))
        season_filter = _norm(season or kwargs.get("temporada"))
        country_filter = _norm(country or kwargs.get("pais"))
        team_filter = _norm(team or kwargs.get("equipo"))

        min_m = _parse_int(min_matches if min_matches is not None else kwargs.get("number_of_matches"))
        max_m = _parse_int(max_matches if max_matches is not None else kwargs.get("number_of_matches"))
        min_t = _parse_int(min_teams if min_teams is not None else kwargs.get("number_of_teams"))
        max_t = _parse_int(max_teams if max_teams is not None else kwargs.get("number_of_teams"))

        needs_post_filter = any(
            [
                author_term,
                author_name,
                author_affiliation,
                author_orcid,
                comp_filter,
                season_filter,
                country_filter,
                team_filter,
                min_m is not None,
                max_m is not None,
                min_t is not None,
                max_t is not None,
            ]
        )

        if needs_post_filter:
            filtered = []
            for ds in unique_results:
                if author_term or author_name or author_affiliation or author_orcid:
                    ds_authors = list(ds.ds_meta_data.authors or [])
                    for fm in ds.feature_models or []:
                        if fm.fm_meta_data and fm.fm_meta_data.authors:
                            ds_authors.extend(fm.fm_meta_data.authors)
                    if author_term and not _author_matches_term(ds_authors, author_term):
                        continue
                    if author_name and not _author_matches_term(ds_authors, author_name, "name"):
                        continue
                    if author_affiliation and not _author_matches_term(ds_authors, author_affiliation, "affiliation"):
                        continue
                    if author_orcid and not _author_matches_term(ds_authors, author_orcid, "orcid"):
                        continue

                if comp_filter and comp_filter not in _norm(_extract_dataset_attr(ds, "competition", "competicion")):
                    continue
                if season_filter and season_filter not in _norm(_extract_dataset_attr(ds, "season", "temporada")):
                    continue
                if country_filter and country_filter not in _norm(_extract_dataset_attr(ds, "country", "pais")):
                    continue
                if team_filter:
                    ds_teams = [_norm(t) for t in _extract_dataset_teams(ds)]
                    if not any(team_filter in t for t in ds_teams):
                        continue

                if min_m is not None or max_m is not None or min_t is not None or max_t is not None:
                    ds_matches, ds_teams_count = _extract_dataset_metrics(ds)
                    if min_m is not None and (ds_matches is None or ds_matches < min_m):
                        continue
                    if max_m is not None and (ds_matches is None or ds_matches > max_m):
                        continue
                    if min_t is not None and (ds_teams_count is None or ds_teams_count < min_t):
                        continue
                    if max_t is not None and (ds_teams_count is None or ds_teams_count > max_t):
                        continue

                filtered.append(ds)
            unique_results = filtered

        return unique_results
