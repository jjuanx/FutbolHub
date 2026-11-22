import re
from datetime import date, datetime, time

import unidecode
from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import or_

from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.features.featuremodel.models import FeatureModel, FMMetaData


def _parse_date_boundary(value, end_of_day: bool = False) -> datetime | None:
    """Convierte una fecha (str 'AAAA-MM-DD', date o datetime) en un límite datetime."""
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
    """Comprueba si algún autor coincide con el término (insensible a mayúsculas y tildes)."""
    norm_term = unidecode.unidecode(term.strip()).lower()
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
            if norm_term in unidecode.unidecode(str(val)).lower():
                return True
    return False


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

        # Order by created_at
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        else:
            datasets = datasets.order_by(self.model.created_at.desc())

        results = datasets.all()

        # Deduplicate while preserving query order
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

        if author_term or author_name or author_affiliation or author_orcid:
            filtered_by_author = []
            for ds in unique_results:
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
                filtered_by_author.append(ds)
            unique_results = filtered_by_author

        return unique_results
