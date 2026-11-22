"""Validador de ficheros CSV de resultados de partidos de fútbol para FutbolHub.

Sustituye la validación de flamapy (UVL) por la validación de resultados de fútbol
según las especificaciones del Acta Fundacional (Sección 2) y la issue #17.

Formato requerido:
    CSV en UTF-8 con cabecera obligatoria y una fila por partido:
    jornada,fecha,local,visitante,goles_local,goles_visitante

Reglas de validación:
    1. Cabecera y columnas requeridas exactas.
    2. Celdas no vacías y con los tipos requeridos (jornada y goles enteros, fecha AAAA-MM-DD).
    3. Goles no negativos (goles >= 0).
    4. Un equipo no puede jugar contra sí mismo (local != visitante).
    5. Un equipo no puede jugar más de una vez en la misma jornada.
    6. No puede haber partidos duplicados.
    7. Las fechas deben pertenecer a la temporada declarada (si se especifica).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import BinaryIO, TextIO, Union

EXPECTED_COLUMNS = [
    "jornada",
    "fecha",
    "local",
    "visitante",
    "goles_local",
    "goles_visitante",
]


@dataclass
class CSVValidationError:
    """Representa un error específico de validación en una fila."""

    row: int
    message: str
    column: str | None = None

    def __str__(self) -> str:
        if self.column:
            return f"Fila {self.row} (columna '{self.column}'): {self.message}"
        return f"Fila {self.row}: {self.message}"


@dataclass
class MatchRecord:
    """Registro tipado de un partido válido extraído del CSV."""

    row: int
    jornada: int
    fecha: date
    local: str
    visitante: str
    goles_local: int
    goles_visitante: int

    @property
    def is_draw(self) -> bool:
        return self.goles_local == self.goles_visitante

    @property
    def winner(self) -> str | None:
        if self.goles_local > self.goles_visitante:
            return self.local
        if self.goles_visitante > self.goles_local:
            return self.visitante
        return None


@dataclass
class CSVValidationResult:
    """Resultado completo de la validación de un archivo CSV de fútbol."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    detailed_errors: list[CSVValidationError] = field(default_factory=list)
    total_rows: int = 0
    valid_rows: int = 0
    matches: list[MatchRecord] = field(default_factory=list)
    teams: list[str] = field(default_factory=list)
    jornadas: list[int] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid

    def add_error(self, row: int, message: str, column: str | None = None) -> None:
        err = CSVValidationError(row=row, message=message, column=column)
        self.detailed_errors.append(err)
        self.errors.append(str(err))
        self.is_valid = False


def parse_season_range(
    season: str | None = None,
    season_start: date | str | None = None,
    season_end: date | str | None = None,
) -> tuple[date | None, date | None]:
    """Determina las fechas de inicio y fin de una temporada declarada.

    Formatos admitidos para `season`:
        - '2024-25', '2024-2025', '2024/25', '2024/2025' -> Julio año 1 a Junio año 2
        - '2024' -> 1 de enero a 31 de diciembre
    """
    start_d: date | None = None
    end_d: date | None = None

    if isinstance(season_start, str):
        start_d = datetime.strptime(season_start, "%Y-%m-%d").date()
    elif isinstance(season_start, date):
        start_d = season_start

    if isinstance(season_end, str):
        end_d = datetime.strptime(season_end, "%Y-%m-%d").date()
    elif isinstance(season_end, date):
        end_d = season_end

    if start_d is not None and end_d is not None:
        return start_d, end_d

    if not season:
        return start_d, end_d

    s = season.strip()
    # Formato '2024-25' o '2024/25' o '2024-2025' o '2024/2025'
    match_split = re.match(r"^(\d{4})[-/](\d{2,4})$", s)
    if match_split:
        y1 = int(match_split.group(1))
        y2_str = match_split.group(2)
        if len(y2_str) == 2:
            century = (y1 // 100) * 100
            y2 = century + int(y2_str)
            if y2 < y1:
                y2 += 100
        else:
            y2 = int(y2_str)

        computed_start = date(y1, 7, 1)
        computed_end = date(y2, 6, 30)
        return start_d or computed_start, end_d or computed_end

    # Formato año natural '2024'
    match_year = re.match(r"^(\d{4})$", s)
    if match_year:
        y = int(match_year.group(1))
        return start_d or date(y, 1, 1), end_d or date(y, 12, 31)

    return start_d, end_d


class ResultsCSVValidator:
    """Validador de ficheros CSV de resultados de partidos de fútbol."""

    def __init__(
        self,
        season: str | None = None,
        season_start: date | str | None = None,
        season_end: date | str | None = None,
    ):
        self.season = season
        self.season_start, self.season_end = parse_season_range(
            season=season,
            season_start=season_start,
            season_end=season_end,
        )

    def validate(
        self,
        source: Union[str, bytes, Path, TextIO, BinaryIO],
    ) -> CSVValidationResult:
        """Valida una fuente CSV (ruta, string, bytes o stream de texto/binario)."""
        result = CSVValidationResult(is_valid=True)

        text_content, read_error = self._read_text(source)
        if read_error:
            result.add_error(row=1, message=read_error)
            return result

        if not text_content or not text_content.strip():
            result.add_error(row=1, message="El fichero CSV está vacío.")
            return result

        lines = text_content.splitlines()
        reader = csv.reader(lines)

        try:
            raw_header = next(reader, None)
        except Exception as exc:
            result.add_error(row=1, message=f"Error al procesar el formato CSV: {exc}")
            return result

        if raw_header is None:
            result.add_error(row=1, message="El fichero CSV está vacío.")
            return result

        cleaned_header = [c.strip().lower() for c in raw_header]
        # Eliminar posible BOM de UTF-8 en primera columna
        if cleaned_header and cleaned_header[0].startswith("\ufeff"):
            cleaned_header[0] = cleaned_header[0].replace("\ufeff", "")

        if cleaned_header != EXPECTED_COLUMNS:
            expected_str = ",".join(EXPECTED_COLUMNS)
            found_str = ",".join(cleaned_header)
            result.add_error(
                row=1,
                message=(
                    f"Cabecera incorrecta. Columnas esperadas: '{expected_str}'. "
                    f"Columnas encontradas: '{found_str}'."
                ),
            )
            return result

        # Control de duplicados e integridad del torneo
        matches_seen: dict[tuple[str, str], int] = {}
        teams_in_jornada: dict[int, dict[str, int]] = {}
        all_teams: set[str] = set()
        all_jornadas: set[int] = set()

        row_num = 1  # 1 es la cabecera
        for row in reader:
            row_num += 1
            if not row or all(not str(cell).strip() for cell in row):
                # Ignorar filas totalmente vacías al final del archivo si no contienen datos
                continue

            result.total_rows += 1

            if len(row) != len(EXPECTED_COLUMNS):
                result.add_error(
                    row=row_num,
                    message=(
                        f"Número incorrecto de columnas: se esperaban {len(EXPECTED_COLUMNS)}, "
                        f"pero se encontraron {len(row)}."
                    ),
                )
                continue

            row_data = dict(zip(EXPECTED_COLUMNS, [c.strip() for c in row]))
            row_errors_before = len(result.detailed_errors)

            # 1. Comprobar celdas vacías
            for col_name in EXPECTED_COLUMNS:
                if not row_data[col_name]:
                    result.add_error(
                        row=row_num,
                        column=col_name,
                        message=f"La celda '{col_name}' no puede estar vacía.",
                    )

            if len(result.detailed_errors) > row_errors_before:
                continue

            # 2. Validar tipos: jornada
            jornada_val: int | None = None
            try:
                jornada_val = int(row_data["jornada"])
                if jornada_val <= 0:
                    result.add_error(
                        row=row_num,
                        column="jornada",
                        message=f"La jornada debe ser un número entero positivo (se obtuvo '{row_data['jornada']}').",
                    )
                    jornada_val = None
            except ValueError:
                result.add_error(
                    row=row_num,
                    column="jornada",
                    message=f"La jornada debe ser un número entero (se obtuvo '{row_data['jornada']}').",
                )

            # 3. Validar tipos y formato: fecha
            match_date: date | None = None
            raw_fecha = row_data["fecha"]
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", raw_fecha):
                result.add_error(
                    row=row_num,
                    column="fecha",
                    message=f"La fecha '{raw_fecha}' no tiene el formato requerido AAAA-MM-DD.",
                )
            else:
                try:
                    match_date = datetime.strptime(raw_fecha, "%Y-%m-%d").date()
                except ValueError:
                    result.add_error(
                        row=row_num,
                        column="fecha",
                        message=f"La fecha '{raw_fecha}' no es una fecha válida del calendario.",
                    )

            # 4. Validar tipos y rango: goles_local y goles_visitante
            goles_local_val: int | None = None
            try:
                goles_local_val = int(row_data["goles_local"])
                if goles_local_val < 0:
                    result.add_error(
                        row=row_num,
                        column="goles_local",
                        message=f"Los goles locales no pueden ser negativos ({goles_local_val}).",
                    )
                    goles_local_val = None
            except ValueError:
                result.add_error(
                    row=row_num,
                    column="goles_local",
                    message=f"Los goles locales deben ser un número entero (se obtuvo '{row_data['goles_local']}').",
                )

            goles_visitante_val: int | None = None
            try:
                goles_visitante_val = int(row_data["goles_visitante"])
                if goles_visitante_val < 0:
                    result.add_error(
                        row=row_num,
                        column="goles_visitante",
                        message=f"Los goles visitantes no pueden ser negativos ({goles_visitante_val}).",
                    )
                    goles_visitante_val = None
            except ValueError:
                val = row_data["goles_visitante"]
                result.add_error(
                    row=row_num,
                    column="goles_visitante",
                    message=f"Los goles visitantes deben ser un número entero (se obtuvo '{val}').",
                )

            # Si hubo errores de tipo básicos en la fila, no comprobamos reglas de negocio complejas
            if len(result.detailed_errors) > row_errors_before:
                continue

            local = row_data["local"]
            visitante = row_data["visitante"]

            # 5. Un equipo no puede jugar contra sí mismo
            if local.casefold() == visitante.casefold():
                result.add_error(
                    row=row_num,
                    message=f"Un equipo no puede jugar contra sí mismo ('{local}').",
                )

            # 6. Partidos duplicados
            match_key = (local.casefold(), visitante.casefold())
            if match_key in matches_seen:
                prev_row = matches_seen[match_key]
                result.add_error(
                    row=row_num,
                    message=(f"Partido duplicado: '{local}' vs '{visitante}' " f"ya se jugó en la fila {prev_row}."),
                )
            else:
                matches_seen[match_key] = row_num

            # 7. Un equipo no puede jugar dos veces en la misma jornada
            if jornada_val is not None:
                all_jornadas.add(jornada_val)
                teams_in_jornada.setdefault(jornada_val, {})
                for team in (local, visitante):
                    t_key = team.casefold()
                    if t_key in teams_in_jornada[jornada_val]:
                        prev_row = teams_in_jornada[jornada_val][t_key]
                        result.add_error(
                            row=row_num,
                            message=(
                                f"El equipo '{team}' juega más de una vez en la jornada {jornada_val} "
                                f"(visto previamente en la fila {prev_row})."
                            ),
                        )
                    else:
                        teams_in_jornada[jornada_val][t_key] = row_num

            # 8. Fechas fuera de la temporada declarada
            if match_date is not None:
                if self.season_start and match_date < self.season_start:
                    desc_season = f"temporada {self.season}" if self.season else f"inicio ({self.season_start})"
                    result.add_error(
                        row=row_num,
                        column="fecha",
                        message=(
                            f"La fecha '{raw_fecha}' es anterior a la fecha de inicio declarada "
                            f"({self.season_start.isoformat()}) para la {desc_season}."
                        ),
                    )
                elif self.season_end and match_date > self.season_end:
                    desc_season = f"temporada {self.season}" if self.season else f"fin ({self.season_end})"
                    result.add_error(
                        row=row_num,
                        column="fecha",
                        message=(
                            f"La fecha '{raw_fecha}' es posterior a la fecha de fin declarada "
                            f"({self.season_end.isoformat()}) para la {desc_season}."
                        ),
                    )

            # Si no hubo errores en esta fila, registrar el partido válido
            if len(result.detailed_errors) == row_errors_before:
                result.valid_rows += 1
                all_teams.add(local)
                all_teams.add(visitante)
                assert jornada_val is not None
                assert match_date is not None
                assert goles_local_val is not None
                assert goles_visitante_val is not None
                result.matches.append(
                    MatchRecord(
                        row=row_num,
                        jornada=jornada_val,
                        fecha=match_date,
                        local=local,
                        visitante=visitante,
                        goles_local=goles_local_val,
                        goles_visitante=goles_visitante_val,
                    )
                )

        result.teams = sorted(all_teams)
        result.jornadas = sorted(all_jornadas)
        return result

    @staticmethod
    def _read_text(
        source: Union[str, bytes, Path, TextIO, BinaryIO],
    ) -> tuple[str | None, str | None]:
        """Extrae el contenido de texto en UTF-8 o retorna un mensaje de error."""
        try:
            if isinstance(source, (str, Path)) and (
                isinstance(source, Path) or (len(str(source)) < 4096 and Path(str(source)).is_file())
            ):
                path = Path(source)
                try:
                    return path.read_text(encoding="utf-8"), None
                except UnicodeDecodeError:
                    return None, "El fichero no tiene una codificación UTF-8 válida."

            if isinstance(source, str):
                return source, None

            if isinstance(source, bytes):
                try:
                    return source.decode("utf-8"), None
                except UnicodeDecodeError:
                    return None, "El fichero no tiene una codificación UTF-8 válida."

            if hasattr(source, "read"):
                raw = source.read()
                if isinstance(raw, str):
                    return raw, None
                if isinstance(raw, bytes):
                    try:
                        return raw.decode("utf-8"), None
                    except UnicodeDecodeError:
                        return None, "El fichero no tiene una codificación UTF-8 válida."

            return None, "Tipo de fuente no soportado para lectura de CSV."
        except Exception as exc:
            return None, f"Error al leer el archivo: {exc}"


def validate_results_csv(
    source: Union[str, bytes, Path, TextIO, BinaryIO],
    season: str | None = None,
    season_start: date | str | None = None,
    season_end: date | str | None = None,
) -> CSVValidationResult:
    """Función de conveniencia para validar un archivo CSV de resultados."""
    validator = ResultsCSVValidator(
        season=season,
        season_start=season_start,
        season_end=season_end,
    )
    return validator.validate(source)
