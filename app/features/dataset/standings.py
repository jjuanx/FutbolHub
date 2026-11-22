"""Servicio de cálculo automático de clasificación y estadísticas por equipo para FutbolHub.

Implementa las reglas del Acta Fundacional (Sección 2) y la issue #19:
- 3 puntos por victoria, 1 punto por empate, 0 puntos por derrota.
- Desempate por diferencia de goles (DG = GF - GC) y después por goles a favor (GF).
- Estadísticas por equipo: jugados, ganados, empatados, perdidos, goles a favor y goles en contra.
- Soporte para uno o varios ficheros CSV por dataset, listas de MatchRecord/diccionarios o instancias de DataSet.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, TextIO, Union

from app.features.dataset.csv_validator import (
    CSVValidationResult,
    MatchRecord,
    validate_results_csv,
)

CSVSource = Union[str, bytes, Path, TextIO, BinaryIO, CSVValidationResult]


@dataclass
class TeamStats:
    """Estadísticas acumuladas y posición en la clasificación de un equipo."""

    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    position: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.won * 3 + self.drawn

    # Alias en español para plantillas y consumidores del dominio
    @property
    def equipo(self) -> str:
        return self.team

    @property
    def posicion(self) -> int:
        return self.position

    @property
    def jugados(self) -> int:
        return self.played

    @property
    def ganados(self) -> int:
        return self.won

    @property
    def empatados(self) -> int:
        return self.drawn

    @property
    def perdidos(self) -> int:
        return self.lost

    @property
    def goles_favor(self) -> int:
        return self.goals_for

    @property
    def goles_contra(self) -> int:
        return self.goals_against

    @property
    def diferencia_goles(self) -> int:
        return self.goal_difference

    @property
    def puntos(self) -> int:
        return self.points

    def record_match(self, scored: int, conceded: int) -> None:
        """Actualiza las estadísticas del equipo tras disputar un partido."""
        if scored < 0 or conceded < 0:
            raise ValueError("Los goles de un partido no pueden ser negativos.")
        self.played += 1
        self.goals_for += scored
        self.goals_against += conceded
        if scored > conceded:
            self.won += 1
        elif scored == conceded:
            self.drawn += 1
        else:
            self.lost += 1

    def to_dict(self) -> dict[str, Any]:
        """Representación serializable a JSON con claves estándar y en español."""
        return {
            "position": self.position,
            "team": self.team,
            "played": self.played,
            "won": self.won,
            "drawn": self.drawn,
            "lost": self.lost,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "goal_difference": self.goal_difference,
            "points": self.points,
            "posicion": self.position,
            "equipo": self.team,
            "jugados": self.played,
            "ganados": self.won,
            "empatados": self.drawn,
            "perdidos": self.lost,
            "goles_favor": self.goals_for,
            "goles_contra": self.goals_against,
            "diferencia_goles": self.goal_difference,
            "puntos": self.points,
        }


def _coerce_match_tuple(item: Any) -> tuple[str, str, int, int]:
    """Extrae (local, visitante, goles_local, goles_visitante) de un MatchRecord, dict u objeto."""
    if isinstance(item, MatchRecord):
        return item.local.strip(), item.visitante.strip(), int(item.goles_local), int(item.goles_visitante)

    if isinstance(item, dict):
        local = str(item.get("local") or item.get("home") or "").strip()
        visitante = str(item.get("visitante") or item.get("away") or "").strip()
        if not local or not visitante:
            raise ValueError("El diccionario de partido debe incluir 'local' y 'visitante'.")
        goles_local = int(item["goles_local"] if "goles_local" in item else item["home_goals"])
        goles_visitante = int(item["goles_visitante"] if "goles_visitante" in item else item["away_goals"])
        return local, visitante, goles_local, goles_visitante

    if all(hasattr(item, attr) for attr in ("local", "visitante", "goles_local", "goles_visitante")):
        return (
            str(item.local).strip(),
            str(item.visitante).strip(),
            int(item.goles_local),
            int(item.goles_visitante),
        )

    raise TypeError(f"Tipo de registro de partido no soportado: {type(item)!r}")


def _resolve_dataset_csv_paths(dataset: Any) -> list[Path]:
    """Obtiene todas las rutas a ficheros CSV asociados a un dataset."""
    paths: list[Path] = []
    working_dir = os.getenv("WORKING_DIR", "")
    user_id = getattr(dataset, "user_id", None)
    dataset_id = getattr(dataset, "id", None)

    base_upload_dir: Path | None = None
    if user_id is not None and dataset_id is not None:
        base_upload_dir = Path(working_dir) / "uploads" / f"user_{user_id}" / f"dataset_{dataset_id}"

    file_objs: list[Any] = []
    if hasattr(dataset, "files") and callable(dataset.files):
        file_objs.extend(dataset.files() or [])
    elif hasattr(dataset, "result_files"):
        file_objs.extend(getattr(dataset, "result_files") or [])
    elif hasattr(dataset, "csv_files"):
        file_objs.extend(getattr(dataset, "csv_files") or [])

    for file_obj in file_objs:
        if isinstance(file_obj, (str, Path)):
            candidate = Path(file_obj)
            if candidate.is_file():
                paths.append(candidate)
            elif base_upload_dir is not None and (base_upload_dir / candidate.name).is_file():
                paths.append(base_upload_dir / candidate.name)
            continue

        file_path_attr = getattr(file_obj, "file_path", None) or getattr(file_obj, "path", None)
        if file_path_attr and Path(str(file_path_attr)).is_file():
            paths.append(Path(str(file_path_attr)))
            continue

        name_attr = getattr(file_obj, "name", None) or getattr(file_obj, "filename", None)
        if name_attr and base_upload_dir is not None:
            candidate = base_upload_dir / str(name_attr)
            if candidate.is_file():
                paths.append(candidate)

    if not paths and base_upload_dir is not None and base_upload_dir.is_dir():
        paths.extend(sorted(base_upload_dir.glob("*.csv")))

    return paths


def extract_matches_from_sources(
    sources: Union[CSVSource, Iterable[Any], Any],
) -> list[MatchRecord]:
    """Extrae una lista unificada de partidos a partir de una o varias fuentes CSV o de un dataset.

    Lanza `ValueError` si algún fichero CSV contiene errores de validación.
    """
    if sources is None:
        return []

    if isinstance(sources, CSVValidationResult):
        if not sources.is_valid:
            raise ValueError(f"CSV inválido: {'; '.join(sources.errors)}")
        return list(sources.matches)

    if isinstance(sources, (str, bytes, Path)) or hasattr(sources, "read"):
        if isinstance(sources, Path) and sources.is_dir():
            csv_files = sorted(sources.glob("*.csv"))
            return extract_matches_from_sources(csv_files)
        validation = validate_results_csv(sources)
        if not validation.is_valid:
            raise ValueError(f"CSV inválido: {'; '.join(validation.errors)}")
        return list(validation.matches)

    # Objeto de modelo DataSet / FootballDataset
    if hasattr(sources, "files") or hasattr(sources, "feature_models") or hasattr(sources, "result_files"):
        if hasattr(sources, "matches") and getattr(sources, "matches"):
            raw_matches = getattr(sources, "matches")
            if callable(raw_matches):
                raw_matches = raw_matches()
            return list(raw_matches)
        csv_paths = _resolve_dataset_csv_paths(sources)
        return extract_matches_from_sources(csv_paths)

    if isinstance(sources, Iterable):
        collected: list[MatchRecord] = []
        for item in sources:
            if isinstance(item, MatchRecord):
                collected.append(item)
            elif isinstance(item, dict) or all(
                hasattr(item, attr) for attr in ("local", "visitante", "goles_local", "goles_visitante")
            ):
                local, visitante, gl, gv = _coerce_match_tuple(item)
                collected.append(
                    MatchRecord(
                        row=int(getattr(item, "row", 0) if not isinstance(item, dict) else item.get("row", 0)),
                        jornada=int(
                            getattr(item, "jornada", 1) if not isinstance(item, dict) else item.get("jornada", 1)
                        ),
                        fecha=getattr(item, "fecha", None) if not isinstance(item, dict) else item.get("fecha"),
                        local=local,
                        visitante=visitante,
                        goles_local=gl,
                        goles_visitante=gv,
                    )
                )
            else:
                collected.extend(extract_matches_from_sources(item))
        return collected

    raise TypeError(f"Fuente de partidos no soportada: {type(sources)!r}")


def calculate_standings(
    sources: Union[CSVSource, Iterable[Any], Any],
) -> list[TeamStats]:
    """Calcula la tabla de clasificación ordenada a partir de partidos, uno o varios CSVs o un dataset.

    Criterios de ordenación (Acta Fundacional, Sección 2):
        1. Mayor número de puntos (3 por victoria, 1 por empate).
        2. Mayor diferencia de goles (goles_favor - goles_contra).
        3. Mayor número de goles a favor.
        4. Orden alfabético del nombre del equipo (desempate determinista final).
    """
    matches = extract_matches_from_sources(sources)
    if not matches:
        return []

    stats_by_key: dict[str, TeamStats] = {}

    for match in matches:
        local, visitante, goles_local, goles_visitante = _coerce_match_tuple(match)
        local_key = local.casefold()
        visitante_key = visitante.casefold()

        if local_key not in stats_by_key:
            stats_by_key[local_key] = TeamStats(team=local)
        if visitante_key not in stats_by_key:
            stats_by_key[visitante_key] = TeamStats(team=visitante)

        stats_by_key[local_key].record_match(scored=goles_local, conceded=goles_visitante)
        stats_by_key[visitante_key].record_match(scored=goles_visitante, conceded=goles_local)

    sorted_table = sorted(
        stats_by_key.values(),
        key=lambda t: (-t.points, -t.goal_difference, -t.goals_for, t.team.casefold()),
    )

    for idx, team_stats in enumerate(sorted_table, start=1):
        team_stats.position = idx

    return sorted_table


class StandingsService:
    """Servicio de dominio para obtener la clasificación y estadísticas por equipo."""

    def calculate(self, sources: Union[CSVSource, Iterable[Any], Any]) -> list[TeamStats]:
        """Devuelve la clasificación ordenada como lista de `TeamStats`."""
        return calculate_standings(sources)

    def calculate_as_dicts(self, sources: Union[CSVSource, Iterable[Any], Any]) -> list[dict[str, Any]]:
        """Devuelve la clasificación ordenada como lista de diccionarios serializables a JSON."""
        return [row.to_dict() for row in calculate_standings(sources)]

    def get_team_stats(
        self,
        sources: Union[CSVSource, Iterable[Any], Any],
        team_name: str,
    ) -> TeamStats | None:
        """Obtiene las estadísticas y posición de un equipo concreto (insensible a mayúsculas)."""
        target = team_name.strip().casefold()
        if not target:
            return None
        for row in calculate_standings(sources):
            if row.team.casefold() == target:
                return row
        return None

    def get_all_team_stats_by_name(
        self,
        sources: Union[CSVSource, Iterable[Any], Any],
    ) -> dict[str, TeamStats]:
        """Devuelve un diccionario `{nombre_equipo: TeamStats}` en orden de clasificación."""
        return {row.team: row for row in calculate_standings(sources)}
