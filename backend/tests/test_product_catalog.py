import csv
from pathlib import Path

from app.models import product_catalog as product_catalog_module
from app.models.product_catalog import (
    ProductCatalog,
    _product_catalog_from_row,
    get_program_for_project,
    seed_product_catalogs,
)
from app.models.project import Project


def test_product_catalog_parser_accepts_current_csv_headers():
    csv_path = Path(__file__).parents[1] / "app" / "data" / "products_catalog.csv"

    with csv_path.open(newline="", encoding="utf-8-sig") as csvfile:
        row = next(csv.DictReader(csvfile, delimiter=";"))

    product = _product_catalog_from_row(row)

    assert product.sector_code == 1
    assert product.sector_name == "Congreso De La República"
    assert product.program_code == 101
    assert product.product_code == 101001
    assert product.indicator_code == 10100100
    assert product.product_name == "Documentos normativos"


def test_seed_replaces_catalog_without_valid_sectors(db_session, tmp_path, monkeypatch):
    db_session.add(ProductCatalog(product_name="Registro sin sector"))
    db_session.commit()
    csv_path = tmp_path / "products_catalog.csv"
    csv_path.write_text(
        "Sector;Nombre  Sector;Código Programa;Programa;Código Producto;Producto;"
        "Descripcion;Medido a través de;codigo del indicador ;Indicador de Producto;"
        "Unidad de medida;Indicador Principal;Es Nacional;Es Territorial\n"
        "24;Transporte;2402;Infraestructura;2402001;Vía construida;Descripción;"
        "Kilómetros;240200100;Vías construidas;Kilómetros;Sí;Sí;Sí\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(product_catalog_module, "SessionLocal", lambda: db_session)

    seed_product_catalogs(csv_path)

    products = db_session.query(ProductCatalog).all()
    assert len(products) == 1
    assert products[0].sector_code == 24
    assert products[0].sector_name == "Transporte"


def test_program_lookup_uses_project_sector_and_indicator(db_session):
    project = Project(name="Proyecto", sector="Cultura", indicator_code="330110100")
    db_session.add(project)
    db_session.add(ProductCatalog(sector_code=33, sector_name="Cultura", program_code=3301, program_name="Promoción cultural", product_code=3301101, product_name="Centro musical", indicator_code=330110100))
    db_session.commit()

    result = get_program_for_project(project.id, db_session)

    assert result.program_name == "Promoción cultural"
    assert result.program_code == 3301