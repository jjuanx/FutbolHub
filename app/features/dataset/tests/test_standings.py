"""Pruebas unitarias del servicio de clasificación automática y estadísticas por equipo (Issue #19).

Diseñadas siguiendo la guía de CONTRIBUTING.md:
- Particiones de equivalencia: victoria local, victoria visitante, empate, temporada vacía,
  un solo fichero CSV, múltiples ficheros CSV por dataset, objetos DataSet/MatchRecord/dict.
- Valores límite: empate a puntos deshecho por diferencia de goles (DG), empate a puntos y DG
  deshecho por goles a favor (GF), empate total deshecho alfabéticamente, partidos 0-0.
"""

from __future__ import annotations

from datetime import date
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.features.dataset.csv_validator import MatchRecord, validate_results_csv
from app.features.dataset.services import DataSetService
from app.features.dataset.standings import (
    StandingsService,
    TeamStats,
    calculate_standings,
    extract_matches_from_sources,
)

pytestmark = pytest.mark.unit

EXAMPLES_DIR = Path(__file__).parent / "csv_examples"


# ---------------------------------------------------------------------------
# 1. Temporada sin partidos (valores límite vacíos)
# ---------------------------------------------------------------------------


def test_temporada_sin_partidos_lista_vacia_devuelve_clasificacion_vacia():
    assert calculate_standings([]) == []
    assert calculate_standings(None) == []


def test_temporada_sin_partidos_csv_solo_cabecera_devuelve_clasificacion_vacia():
    csv_header_only = "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
    assert calculate_standings(csv_header_only) == []


def test_temporada_sin_partidos_directorio_vacio_devuelve_clasificacion_vacia(tmp_path):
    assert calculate_standings(tmp_path) == []


# ---------------------------------------------------------------------------
# 2. Puntuación (3 victoria, 1 empate, 0 derrota) y estadísticas por equipo
# ---------------------------------------------------------------------------


def test_calcula_estadisticas_completas_victoria_local_visitante_y_empate():
    csv_content = (
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "1,2024-08-15,Sevilla FC,Real Betis,2,1\n"
        "1,2024-08-16,Real Madrid,Valencia CF,0,0\n"
        "2,2024-08-23,Real Betis,Real Madrid,1,3\n"
        "2,2024-08-24,Valencia CF,Sevilla FC,2,2\n"
    )
    table = calculate_standings(csv_content)

    assert [row.team for row in table] == [
        "Real Madrid",
        "Sevilla FC",
        "Valencia CF",
        "Real Betis",
    ]
    assert [row.position for row in table] == [1, 2, 3, 4]

    rm = table[0]
    assert rm.played == 2
    assert rm.won == 1
    assert rm.drawn == 1
    assert rm.lost == 0
    assert rm.goals_for == 3
    assert rm.goals_against == 1
    assert rm.goal_difference == 2
    assert rm.points == 4

    sev = table[1]
    assert (sev.played, sev.won, sev.drawn, sev.lost) == (2, 1, 1, 0)
    assert (sev.goals_for, sev.goals_against, sev.goal_difference, sev.points) == (4, 3, 1, 4)

    val = table[2]
    assert (val.played, val.won, val.drawn, val.lost) == (2, 0, 2, 0)
    assert (val.goals_for, val.goals_against, val.goal_difference, val.points) == (2, 2, 0, 2)

    bet = table[3]
    assert (bet.played, bet.won, bet.drawn, bet.lost) == (2, 0, 0, 2)
    assert (bet.goals_for, bet.goals_against, bet.goal_difference, bet.points) == (2, 5, -3, 0)


def test_propiedades_en_espanol_y_serializacion_to_dict():
    stats = TeamStats(team="Sevilla FC")
    stats.record_match(scored=3, conceded=1)
    stats.record_match(scored=1, conceded=1)
    stats.position = 1

    assert stats.equipo == "Sevilla FC"
    assert stats.posicion == 1
    assert stats.jugados == 2
    assert stats.ganados == 1
    assert stats.empatados == 1
    assert stats.perdidos == 0
    assert stats.goles_favor == 4
    assert stats.goles_contra == 2
    assert stats.diferencia_goles == 2
    assert stats.puntos == 4

    as_dict = stats.to_dict()
    assert as_dict["team"] == "Sevilla FC"
    assert as_dict["equipo"] == "Sevilla FC"
    assert as_dict["points"] == 4
    assert as_dict["puntos"] == 4
    assert as_dict["goal_difference"] == 2
    assert as_dict["diferencia_goles"] == 2


def test_record_match_rechaza_goles_negativos():
    stats = TeamStats(team="Sevilla FC")
    with pytest.raises(ValueError, match="negativos"):
        stats.record_match(scored=-1, conceded=0)
    with pytest.raises(ValueError, match="negativos"):
        stats.record_match(scored=0, conceded=-2)


# ---------------------------------------------------------------------------
# 3. Criterios de desempate: Puntos -> Diferencia de Goles (DG) -> Goles a Favor (GF)
# ---------------------------------------------------------------------------


def test_desempate_a_puntos_por_diferencia_de_goles():
    """Tres equipos empatados a 3 puntos con DG +3, +1 y -4 se ordenan por DG descendente."""
    matches = [
        MatchRecord(
            row=2,
            jornada=1,
            fecha=date(2024, 8, 15),
            local="Equipo A",
            visitante="Equipo C",
            goles_local=4,
            goles_visitante=0,
        ),
        MatchRecord(
            row=3,
            jornada=2,
            fecha=date(2024, 8, 22),
            local="Equipo B",
            visitante="Equipo A",
            goles_local=2,
            goles_visitante=1,
        ),
        MatchRecord(
            row=4,
            jornada=3,
            fecha=date(2024, 8, 29),
            local="Equipo C",
            visitante="Equipo B",
            goles_local=1,
            goles_visitante=0,
        ),
    ]
    table = calculate_standings(matches)

    # Todos tienen 1 victoria y 1 derrota = 3 puntos
    assert [row.points for row in table] == [3, 3, 3]
    # Equipo A: GF=5, GC=2 -> DG=+3
    # Equipo B: GF=2, GC=2 -> DG=0
    # Equipo C: GF=1, GC=4 -> DG=-3
    assert [row.team for row in table] == ["Equipo A", "Equipo B", "Equipo C"]
    assert [row.goal_difference for row in table] == [3, 0, -3]
    assert [row.position for row in table] == [1, 2, 3]


def test_desempate_a_puntos_e_igual_diferencia_de_goles_por_goles_a_favor():
    """Dos equipos con mismos puntos (4 pts) y misma DG (+2) se desempatan por mayor GF."""
    csv_content = (
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        # Villarreal gana 2-0 (GF=2, GC=0, DG=+2) y empata 0-0 -> 4 pts, DG=+2, GF=2
        "1,2024-08-15,Villarreal CF,Getafe CF,2,0\n"
        "2,2024-08-22,Villarreal CF,CA Osasuna,0,0\n"
        # Athletic gana 4-2 (GF=4, GC=2, DG=+2) y empata 1-1 -> 4 pts, DG=+2, GF=5
        "1,2024-08-15,Athletic Club,RC Celta,4,2\n"
        "2,2024-08-22,Athletic Club,Girona FC,1,1\n"
    )
    table = calculate_standings(csv_content)

    top_two = table[:2]
    assert [row.team for row in top_two] == ["Athletic Club", "Villarreal CF"]
    assert top_two[0].points == top_two[1].points == 4
    assert top_two[0].goal_difference == top_two[1].goal_difference == 2
    assert top_two[0].goals_for == 5
    assert top_two[1].goals_for == 2


def test_desempate_total_puntos_dg_y_gf_iguales_ordena_alfabeticamente():
    """Si empatan en puntos, DG y GF, el orden es determinista por nombre de equipo."""
    csv_content = (
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "1,2024-08-15,Real Sociedad,Alavés,0,0\n"
        "1,2024-08-16,Betis,Mallorca,0,0\n"
    )
    table = calculate_standings(csv_content)
    assert [row.team for row in table] == ["Alavés", "Betis", "Mallorca", "Real Sociedad"]
    assert all(row.points == 1 and row.goal_difference == 0 and row.goals_for == 0 for row in table)


# ---------------------------------------------------------------------------
# 4. Uno o varios ficheros CSV por dataset
# ---------------------------------------------------------------------------


def test_funciona_con_un_unico_fichero_csv_de_ejemplo():
    csv_path = EXAMPLES_DIR / "valid_season_2024_25.csv"
    table = calculate_standings(csv_path)

    assert len(table) == 20
    # FC Barcelona, RC Celta y Rayo Vallecano ganan 2-1 (3 pts, DG=+1, GF=2)
    assert [r.team for r in table[:3]] == ["FC Barcelona", "Rayo Vallecano", "RC Celta"]
    assert all(r.points == 3 and r.goal_difference == 1 and r.goals_for == 2 for r in table[:3])
    # Real Valladolid gana 1-0 (3 pts, DG=+1, GF=1) -> 4º por menor GF a igualdad de puntos y DG
    assert table[3].team == "Real Valladolid"
    assert (table[3].points, table[3].goal_difference, table[3].goals_for) == (3, 1, 1)


def test_funciona_con_varios_ficheros_csv_por_dataset(tmp_path):
    """Un dataset dividido en varios CSVs (uno por jornada) acumula resultados correctamente."""
    jornada_1 = tmp_path / "jornada_1.csv"
    jornada_2 = tmp_path / "jornada_2.csv"
    jornada_3 = tmp_path / "jornada_3.csv"

    jornada_1.write_text(
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "1,2024-08-15,Sevilla FC,Real Betis,2,0\n"
        "1,2024-08-16,Real Madrid,FC Barcelona,1,1\n",
        encoding="utf-8",
    )
    jornada_2.write_text(
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "2,2024-08-22,FC Barcelona,Sevilla FC,3,1\n"
        "2,2024-08-23,Real Betis,Real Madrid,0,2\n",
        encoding="utf-8",
    )
    jornada_3.write_text(
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "3,2024-08-29,Sevilla FC,Real Madrid,1,0\n"
        "3,2024-08-30,Real Betis,FC Barcelona,2,2\n",
        encoding="utf-8",
    )

    # Pasando lista de ficheros
    table_from_list = calculate_standings([jornada_1, jornada_2, jornada_3])
    # Pasando el directorio del dataset
    table_from_dir = calculate_standings(tmp_path)

    assert [r.to_dict() for r in table_from_list] == [r.to_dict() for r in table_from_dir]

    # Sevilla FC: G2, P1 -> 6 pts (GF=4, GC=3, DG=+1)
    # FC Barcelona: G1, E2 -> 5 pts (GF=6, GC=4, DG=+2)
    # Real Madrid: G1, E1, P1 -> 4 pts (GF=3, GC=2, DG=+1)
    # Real Betis: E1, P2 -> 1 pt (GF=2, GC=6, DG=-4)
    assert [r.team for r in table_from_list] == [
        "Sevilla FC",
        "FC Barcelona",
        "Real Madrid",
        "Real Betis",
    ]
    assert [r.points for r in table_from_list] == [6, 5, 4, 1]
    assert all(r.played == 3 for r in table_from_list)


def test_funciona_con_instancia_dataset_y_multiples_hubfiles(tmp_path, monkeypatch):
    """DataSetService.get_standings(dataset) resuelve los CSVs desde la carpeta del dataset."""
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    dataset_dir = tmp_path / "uploads" / "user_7" / "dataset_42"
    dataset_dir.mkdir(parents=True)

    (dataset_dir / "j1.csv").write_text(
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "1,2024-08-15,Atlético de Madrid,Villarreal CF,2,2\n",
        encoding="utf-8",
    )
    (dataset_dir / "j2.csv").write_text(
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
        "2,2024-08-22,Villarreal CF,Atlético de Madrid,0,3\n",
        encoding="utf-8",
    )

    fake_dataset = SimpleNamespace(
        id=42,
        user_id=7,
        files=lambda: [SimpleNamespace(name="j1.csv"), SimpleNamespace(name="j2.csv")],
    )

    service = DataSetService()
    standings = service.get_standings(fake_dataset)

    assert [r.team for r in standings] == ["Atlético de Madrid", "Villarreal CF"]
    assert [r.points for r in standings] == [4, 1]
    assert standings[0].goals_for == 5
    assert standings[0].goals_against == 2


def test_standings_service_busqueda_por_equipo_y_diccionarios():
    csv_stream = StringIO(
        "jornada,fecha,local,visitante,goles_local,goles_visitante\n" "1,2024-08-15,Sevilla FC,Real Betis,1,0\n"
    )
    validation = validate_results_csv(csv_stream)
    service = StandingsService()

    sev = service.get_team_stats(validation, "sevilla fc")
    assert sev is not None
    assert sev.position == 1
    assert sev.points == 3

    assert service.get_team_stats(validation, "Equipo Inexistente") is None
    assert service.get_team_stats(validation, "   ") is None

    by_name = service.get_all_team_stats_by_name(validation)
    assert set(by_name.keys()) == {"Sevilla FC", "Real Betis"}

    as_dicts = service.calculate_as_dicts(
        [{"local": "Sevilla FC", "visitante": "Real Betis", "goles_local": 1, "goles_visitante": 0}]
    )
    assert len(as_dicts) == 2
    assert as_dicts[0]["team"] == "Sevilla FC"
    assert as_dicts[0]["points"] == 3


def test_rechaza_csv_invalido_al_calcular_clasificacion():
    invalid_csv = EXAMPLES_DIR / "invalid_negative_goals.csv"
    with pytest.raises(ValueError, match="CSV inválido"):
        calculate_standings(invalid_csv)


def test_extract_matches_soporta_objetos_con_atributos_y_rechaza_tipos_invalidos():
    custom_match = SimpleNamespace(
        row=2,
        jornada=1,
        fecha=date(2024, 8, 15),
        local="Cádiz CF",
        visitante="Málaga CF",
        goles_local=2,
        goles_visitante=2,
    )
    matches = extract_matches_from_sources([custom_match])
    assert len(matches) == 1
    assert matches[0].is_draw

    with pytest.raises(TypeError):
        calculate_standings(12345)
