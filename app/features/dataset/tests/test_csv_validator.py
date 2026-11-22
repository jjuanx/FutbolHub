"""Pruebas unitarias para el validador de CSV de resultados de fútbol (FutbolHub).

Sigue los criterios de calidad de CONTRIBUTING.md (issue #5), los principios del
Capítulo 4 de los apuntes (particiones de equivalencia y valores límite) y los
requisitos de la issue #17.

Categoría: @pytest.mark.unit (lógica pura, sin app context ni base de datos).
"""

import io
from datetime import date
from pathlib import Path

import pytest

from app.features.dataset.csv_validator import (
    EXPECTED_COLUMNS,
    ResultsCSVValidator,
    parse_season_range,
    validate_results_csv,
)

pytestmark = pytest.mark.unit

EXAMPLES_DIR = Path(__file__).parent / "csv_examples"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PARTICIONES DE EQUIVALENCIA Y VALORES LÍMITE: GOLES
# ═══════════════════════════════════════════════════════════════════════════════


class TestGolesValidation:
    """Valores límite y particiones equivalentes para goles_local y goles_visitante.

    Límite inferior válido: 0
    Primer valor inválido por debajo del límite: -1
    Partición válida: enteros >= 0 (0, 1, 2, 10)
    Partición inválida: negativos (-1, -5) y tipos no enteros ('tres', 2.5)
    """

    @pytest.mark.parametrize("goles_loc,goles_vis", [(0, 0), (1, 0), (0, 1), (5, 3), (12, 0)])
    def test_acepta_goles_validos_incluyendo_cero(self, goles_loc, goles_vis):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"1,2024-08-15,Betis,Sevilla,{goles_loc},{goles_vis}\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.matches) == 1
        assert result.matches[0].goles_local == goles_loc
        assert result.matches[0].goles_visitante == goles_vis

    @pytest.mark.parametrize("goles_negativo", [-1, -2, -10])
    def test_rechaza_goles_locales_negativos_valor_limite(self, goles_negativo):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"1,2024-08-15,Betis,Sevilla,{goles_negativo},1\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("goles locales no pueden ser negativos" in e.lower() for e in result.errors)
        assert any("fila 2" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("goles_negativo", [-1, -3, -99])
    def test_rechaza_goles_visitantes_negativos_valor_limite(self, goles_negativo):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"1,2024-08-15,Betis,Sevilla,2,{goles_negativo}\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("goles visitantes no pueden ser negativos" in e.lower() for e in result.errors)
        assert any("fila 2" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("valor_invalido", ["tres", "2.5", "N/A"])
    def test_rechaza_goles_con_tipo_no_entero(self, valor_invalido):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"1,2024-08-15,Betis,Sevilla,{valor_invalido},1\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("goles locales deben ser un número entero" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("valor_no_estricto", ["1_0", "+1", "2.0"])
    def test_rechaza_goles_no_estrictos_guion_bajo_o_signo_mas(self, valor_no_estricto):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"1,2024-08-15,Betis,Sevilla,{valor_no_estricto},1\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("goles locales deben ser un número entero" in e.lower() for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PARTICIONES DE EQUIVALENCIA Y VALORES LÍMITE: JORNADA
# ═══════════════════════════════════════════════════════════════════════════════


class TestJornadaValidation:
    """Valores límite y tipos de la columna jornada.

    Límite inferior válido: 1
    Primer valor inválido por debajo del límite: 0, -1
    Partición válida: enteros positivos (1, 2, 38)
    Partición inválida: 0, negativos, decimales, texto
    """

    @pytest.mark.parametrize("jornada", [1, 2, 19, 38])
    def test_acepta_jornadas_validas_positivas(self, jornada):
        csv_data = (
            f"jornada,fecha,local,visitante,goles_local,goles_visitante\n{jornada},2024-08-15,Betis,Sevilla,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is True
        assert result.matches[0].jornada == jornada

    @pytest.mark.parametrize("jornada_invalida", [0, -1, -5])
    def test_rechaza_jornada_menor_o_igual_a_cero(self, jornada_invalida):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"{jornada_invalida},2024-08-15,Betis,Sevilla,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("jornada debe ser un número entero positivo" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("tipo_invalido", ["primera", "1.5", "J1"])
    def test_rechaza_jornada_no_entera(self, tipo_invalido):
        csv_data = (
            f"jornada,fecha,local,visitante,goles_local,goles_visitante\n{tipo_invalido},2024-08-15,Betis,Sevilla,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("jornada debe ser un número entero" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("valor_no_estricto", ["1_0", "+1", "1.0"])
    def test_rechaza_jornada_no_estricta_guion_bajo_o_signo_mas(self, valor_no_estricto):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            f"{valor_no_estricto},2024-08-15,Betis,Sevilla,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("jornada debe ser un número entero" in e.lower() for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FORMATO Y VALIDEZ DE FECHAS
# ═══════════════════════════════════════════════════════════════════════════════


class TestFechaValidation:
    """Validación del formato estricto AAAA-MM-DD y fechas de calendario reales."""

    @pytest.mark.parametrize("fecha_valida", ["2024-08-15", "2025-01-01", "2024-02-29"])
    def test_acepta_fechas_formato_correcto(self, fecha_valida):
        csv_data = f"jornada,fecha,local,visitante,goles_local,goles_visitante\n1,{fecha_valida},Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data)
        assert result.is_valid is True

    @pytest.mark.parametrize(
        "formato_invalido",
        [
            "15/08/2024",  # DD/MM/AAAA
            "15-08-2024",  # DD-MM-AAAA
            "2024/08/15",  # barras en lugar de guiones
            "2024-8-15",  # mes con 1 dígito
            "24-08-15",  # año 2 dígitos
        ],
    )
    def test_rechaza_formatos_de_fecha_incorrectos(self, formato_invalido):
        csv_data = (
            f"jornada,fecha,local,visitante,goles_local,goles_visitante\n1,{formato_invalido},Betis,Sevilla,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("no tiene el formato requerido aaaa-mm-dd" in e.lower() for e in result.errors)

    @pytest.mark.parametrize(
        "fecha_inexistente",
        [
            "2024-02-30",  # 30 de febrero nunca existe
            "2023-02-29",  # 2023 no fue bisiesto
            "2024-04-31",  # abril tiene 30 días
            "2024-13-01",  # mes 13 no existe
        ],
    )
    def test_rechaza_fechas_calendario_inexistentes(self, fecha_inexistente):
        csv_data = (
            f"jornada,fecha,local,visitante,goles_local,goles_visitante\n1,{fecha_inexistente},Betis,Sevilla,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("no es una fecha válida del calendario" in e.lower() for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. VALORES LÍMITE: RANGO DE TEMPORADA DECLARADA
# ═══════════════════════════════════════════════════════════════════════════════


class TestSeasonRangeValidation:
    """Valores límite de fechas respecto a la temporada declarada.

    Para temporada 2024-25 (definida del 2024-07-01 al 2025-06-30):
        - 2024-06-30 (1 día antes del inicio) -> INVÁLIDO
        - 2024-07-01 (primer día de la temporada) -> VÁLIDO
        - 2025-06-30 (último día de la temporada) -> VÁLIDO
        - 2025-07-01 (1 día después del fin) -> INVÁLIDO
    """

    def test_limite_inicio_temporada_exacto_es_valido(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-07-01,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data, season="2024-25")
        assert result.is_valid is True

    def test_limite_fin_temporada_exacto_es_valido(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2025-06-30,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data, season="2024-25")
        assert result.is_valid is True

    def test_limite_un_dia_antes_inicio_es_invalido(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-06-30,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data, season="2024-25")
        assert result.is_valid is False
        assert any("anterior a la fecha de inicio declarada" in e.lower() for e in result.errors)

    def test_limite_un_dia_despues_fin_es_invalido(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2025-07-01,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data, season="2024-25")
        assert result.is_valid is False
        assert any("posterior a la fecha de fin declarada" in e.lower() for e in result.errors)

    def test_rango_explicito_personalizado(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,1,0\n"
        result_ok = validate_results_csv(
            csv_data,
            season_start=date(2024, 8, 1),
            season_end=date(2025, 5, 31),
        )
        assert result_ok.is_valid is True

        result_fuera = validate_results_csv(
            csv_data,
            season_start=date(2024, 9, 1),
            season_end=date(2025, 5, 31),
        )
        assert result_fuera.is_valid is False

    def test_rechaza_formato_temporada_no_reconocido(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data, season="temporada 24")
        assert result.is_valid is False
        assert any("formato de temporada no reconocido" in e.lower() for e in result.errors)

    def test_rechaza_season_start_con_formato_erroneo(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data, season_start="15/08/2024")
        assert result.is_valid is False
        assert any("formato de season_start no válido" in e.lower() for e in result.errors)

    def test_instanciacion_directa_validator(self):
        validator = ResultsCSVValidator(season="2024-25")
        assert validator.season_start == date(2024, 7, 1)
        assert validator.season_end == date(2025, 6, 30)

    def test_parse_season_range_lanza_value_error_en_formato_invalido(self):
        with pytest.raises(ValueError, match="Formato de temporada no reconocido"):
            parse_season_range(season="temporada 24")
        with pytest.raises(ValueError, match="Formato de season_start no válido"):
            parse_season_range(season_start="invalido")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. REGLAS DE INTEGRIDAD DEL DOMINIO DE FÚTBOL
# ═══════════════════════════════════════════════════════════════════════════════


class TestFootballDomainRules:
    """Reglas de negocio: equipo contra sí mismo, duplicados en jornada y partidos duplicados."""

    def test_rechaza_equipo_contra_si_mismo(self):
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Sevilla FC,Sevilla FC,1,0\n"
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("un equipo no puede jugar contra sí mismo" in e.lower() for e in result.errors)
        assert any("sevilla fc" in e.lower() for e in result.errors)

    def test_equipo_contra_si_mismo_genera_un_unico_error_sin_duplicado_jornada(self):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n" "1,2024-08-15,Sevilla FC,Sevilla FC,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "no puede jugar contra sí mismo" in result.errors[0]
        assert not any("más de una vez en la jornada" in e for e in result.errors)

    def test_rechaza_equipo_contra_si_mismo_insensible_a_mayusculas(self):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Real Madrid,real madrid,2,2\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("un equipo no puede jugar contra sí mismo" in e.lower() for e in result.errors)

    def test_rechaza_equipo_juega_dos_veces_en_la_misma_jornada_ambas_local(self):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            "1,2024-08-15,Real Madrid,Valencia CF,2,1\n"
            "1,2024-08-16,Real Madrid,Getafe CF,1,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("juega más de una vez en la jornada 1" in e.lower() for e in result.errors)
        assert any("fila 3" in e.lower() for e in result.errors)

    def test_rechaza_equipo_juega_dos_veces_en_la_misma_jornada_local_y_visitante(self):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            "1,2024-08-15,Real Madrid,Valencia CF,2,1\n"
            "1,2024-08-16,Sevilla FC,Real Madrid,1,1\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("real madrid' juega más de una vez en la jornada 1" in e.lower() for e in result.errors)

    def test_permite_mismos_equipos_en_jornadas_distintas(self):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            "1,2024-08-15,Real Madrid,Valencia CF,2,1\n"
            "2,2024-08-22,Valencia CF,Real Madrid,1,1\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is True
        assert len(result.matches) == 2

    def test_rechaza_partido_duplicado_mismo_enfrentamiento(self):
        csv_data = (
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n"
            "1,2024-08-15,Sevilla FC,Real Betis,2,1\n"
            "5,2024-09-20,Sevilla FC,Real Betis,0,0\n"
        )
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("partido duplicado" in e.lower() for e in result.errors)
        assert any("fila 3" in e.lower() for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. ESTRUCTURA CSV: CABECERA, CELDAS VACÍAS, ENCODING Y STREAMS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCSVStructureAndIO:
    """Validación estructural de columnas, filas vacías, encoding UTF-8 y tipos de entrada."""

    def test_rechaza_archivo_vacio(self):
        result = validate_results_csv("")
        assert result.is_valid is False
        assert any("vacío" in e.lower() for e in result.errors)

    def test_rechaza_cabecera_con_columnas_faltantes(self):
        csv_data = "jornada,fecha,local,visitante\n1,2024-08-15,Betis,Sevilla\n"
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("cabecera incorrecta" in e.lower() for e in result.errors)

    def test_rechaza_cabecera_con_nombres_erroneos(self):
        csv_data = "jornada,fecha,equipo1,equipo2,goles1,goles2\n1,2024-08-15,Betis,Sevilla,1,0\n"
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any("cabecera incorrecta" in e.lower() for e in result.errors)

    @pytest.mark.parametrize("columna_vacia", EXPECTED_COLUMNS)
    def test_rechaza_celda_vacia_en_cualquier_columna(self, columna_vacia):
        valores = {
            "jornada": "1",
            "fecha": "2024-08-15",
            "local": "Betis",
            "visitante": "Sevilla",
            "goles_local": "2",
            "goles_visitante": "1",
        }
        valores[columna_vacia] = ""
        csv_data = "jornada,fecha,local,visitante,goles_local,goles_visitante\n" f"{','.join(valores.values())}\n"
        result = validate_results_csv(csv_data)
        assert result.is_valid is False
        assert any(f"la celda '{columna_vacia}' no puede estar vacía" in e.lower() for e in result.errors)

    def test_soporta_entrada_como_bytes_utf8(self):
        content = "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,2,1\n".encode(
            "utf-8"
        )
        result = validate_results_csv(content)
        assert result.is_valid is True

    def test_rechaza_entrada_con_encoding_no_utf8(self):
        # Bytes inválidos en UTF-8
        bad_bytes = b"\xff\xfe\x00\x00jornada,fecha"
        result = validate_results_csv(bad_bytes)
        assert result.is_valid is False
        assert any("utf-8" in e.lower() for e in result.errors)

    def test_soporta_stream_stringio(self):
        stream = io.StringIO(
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,2,1\n"
        )
        result = validate_results_csv(stream)
        assert result.is_valid is True

    def test_soporta_stream_bytesio(self):
        stream = io.BytesIO(
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,2,1\n".encode(
                "utf-8"
            )
        )
        result = validate_results_csv(stream)
        assert result.is_valid is True

    def test_soporta_bom_utf8(self):
        bom_csv = "\ufeffjornada,fecha,local,visitante,goles_local,goles_visitante\n1,2024-08-15,Betis,Sevilla,2,1\n"
        result = validate_results_csv(bom_csv)
        assert result.is_valid is True


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PRUEBAS CON FICHEROS CSV DE EJEMPLO FÍSICOS (csv_examples/)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPhysicalCSVExamples:
    """Verifica el comportamiento contra los ficheros CSV guardados en disco."""

    def test_fichero_valido_laliga_2024_25(self):
        filepath = EXAMPLES_DIR / "valid_season_2024_25.csv"
        assert filepath.exists(), f"No se encuentra {filepath}"
        result = validate_results_csv(filepath, season="2024-25")
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.total_rows == 10
        assert len(result.teams) == 20
        assert result.jornadas == [1]

    def test_fichero_valido_ceros(self):
        filepath = EXAMPLES_DIR / "valid_boundary_zeros.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is True
        assert result.matches[0].goles_local == 0
        assert result.matches[0].goles_visitante == 0
        assert result.matches[0].is_draw is True

    def test_fichero_invalido_goles_negativos(self):
        filepath = EXAMPLES_DIR / "invalid_negative_goals.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False
        assert any("negativo" in e.lower() for e in result.errors)

    def test_fichero_invalido_equipo_contra_si_mismo(self):
        filepath = EXAMPLES_DIR / "invalid_self_match.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False
        assert any("contra sí mismo" in e.lower() for e in result.errors)

    def test_fichero_invalido_partido_duplicado(self):
        filepath = EXAMPLES_DIR / "invalid_duplicate_match.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False
        assert any("duplicado" in e.lower() for e in result.errors)

    def test_fichero_invalido_misma_jornada_repetido(self):
        filepath = EXAMPLES_DIR / "invalid_same_jornada_duplicate_team.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False
        assert any("más de una vez en la jornada 1" in e.lower() for e in result.errors)

    def test_fichero_invalido_celda_vacia(self):
        filepath = EXAMPLES_DIR / "invalid_empty_cell.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False
        assert any("vacía" in e.lower() for e in result.errors)

    def test_fichero_invalido_cabecera(self):
        filepath = EXAMPLES_DIR / "invalid_header.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False
        assert any("cabecera incorrecta" in e.lower() for e in result.errors)

    def test_fichero_invalido_formato_fecha(self):
        filepath = EXAMPLES_DIR / "invalid_date_format.csv"
        result = validate_results_csv(filepath)
        assert result.is_valid is False

    def test_fichero_invalido_fuera_de_temporada(self):
        filepath = EXAMPLES_DIR / "invalid_outside_season.csv"
        result = validate_results_csv(filepath, season="2024-25")
        assert result.is_valid is False
        assert any("anterior" in e.lower() or "posterior" in e.lower() for e in result.errors)
