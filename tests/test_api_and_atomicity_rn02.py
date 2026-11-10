"""Testes de contrato HTTP da API REST e prova de atomicidade transacional no SQLite (RN-02)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import OrderItem, Upload
from tests.conftest import SyncASGIClient

CSV_HEADER = (
    "order_id,timestamp,item_name,category,quantity,unit_price,"
    "discount,prep_time_minutes,status,channel"
)


def test_api_health_endpoint_returns_200_ok(client: SyncASGIClient) -> None:
    """Prova o contrato de `GET /api/v1/health` retornando 200 OK e `{'status': 'ok'}`."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rn02_upload_without_file_or_empty_filename_returns_400_bad_request(
    client: SyncASGIClient,
    db_session: Session,
) -> None:
    """
    Prova que `POST /api/v1/uploads` sem arquivo ou com nome de arquivo vazio
    retorna `400 Bad Request` no formato padrão `{'detail': ..., 'errors': []}` e não grava no SQLite.
    """
    resp_no_file = client.post("/api/v1/uploads")
    assert resp_no_file.status_code == 400
    body_no_file = resp_no_file.json()
    assert "detail" in body_no_file
    assert body_no_file["errors"] == []

    resp_empty_name = client.post(
        "/api/v1/uploads",
        files={"file": ("   ", b"conteudo", "text/csv")},
    )
    assert resp_empty_name.status_code == 400
    body_empty_name = resp_empty_name.json()
    assert "detail" in body_empty_name
    assert body_empty_name["errors"] == []

    assert len(list(db_session.scalars(select(Upload)).all())) == 0
    assert len(list(db_session.scalars(select(OrderItem)).all())) == 0


def test_rn02_atomicity_rejects_mixed_valid_and_invalid_csv_without_partial_sqlite_writes(
    client: SyncASGIClient,
    db_session: Session,
) -> None:
    """
    Prova a regra crítica RN-02 (Atomicidade Transacional):
    Um CSV com 2 linhas perfeitamente válidas e 1 linha inválida (linha 4 com unit_price negativo)
    retorna `422 Unprocessable Entity` e deixa ZERO registros em `uploads` e `order_items`.
    """
    mixed_csv = (
        f"{CSV_HEADER}\n"
        "ORD-001,2026-11-01T18:10:00Z,Combo Burger,Combos,1,80.00,0.00,20.0,completed,delivery\n"
        "ORD-002,2026-11-01T18:15:00Z,Smash Burger,Burgers,2,40.00,5.00,18.0,completed,app\n"
        "ORD-003,2026-11-01T18:20:00Z,Batata Rustica,Porcoes,1,-15.00,0.00,12.0,completed,balcao\n"
    ).encode("utf-8")

    response = client.post(
        "/api/v1/uploads",
        files={"file": ("lote_corrompido.csv", mixed_csv, "text/csv")},
    )

    assert response.status_code == 422
    payload = response.json()
    assert "detail" in payload
    assert len(payload["errors"]) == 1
    assert payload["errors"][0]["row"] == 4
    assert payload["errors"][0]["column"] == "unit_price"

    # Verificação direta no banco SQLite: zero lotes e zero itens gravados
    uploads_in_db = list(db_session.scalars(select(Upload)).all())
    items_in_db = list(db_session.scalars(select(OrderItem)).all())
    assert len(uploads_in_db) == 0
    assert len(items_in_db) == 0

    # Verificação via endpoint público de listagem
    list_resp = client.get("/api/v1/uploads")
    assert list_resp.status_code == 200
    assert list_resp.json() == {"items": [], "total": 0}


def test_rn02_valid_upload_persists_atomically_and_serves_metrics_end_to_end(
    client: SyncASGIClient,
    db_session: Session,
    sample_csv_bytes: bytes,
) -> None:
    """
    Prova o fluxo ponta a ponta de upload válido (`POST /api/v1/uploads` -> `201 Created`),
    persistência integral no SQLite (`1` lote e `82` itens), listagem (`GET /api/v1/uploads`)
    e leitura do relatório analítico completo (`GET /api/v1/uploads/{upload_id}/metrics`).
    """
    post_resp = client.post(
        "/api/v1/uploads",
        files={"file": ("sample_orders.csv", sample_csv_bytes, "text/csv")},
    )
    assert post_resp.status_code == 201
    created = post_resp.json()

    upload_id = created["upload_id"]
    assert isinstance(upload_id, str) and len(upload_id) == 36
    assert created["filename"] == "sample_orders.csv"
    assert created["total_rows"] == 82
    assert created["valid_orders_count"] == 50
    assert created["canceled_orders_count"] == 5
    assert created["summary_metrics"] == {
        "gross_revenue": 5000.0,
        "discount_total": 250.0,
        "net_revenue": 4750.0,
        "average_ticket_gross": 100.0,
        "average_ticket_net": 95.0,
        "canceled_revenue_loss": 514.0,
        "top_abc_item": "Combo Burger Duplo Artesanal",
    }

    # Confirma persistência física no SQLite
    uploads_in_db = list(db_session.scalars(select(Upload)).all())
    items_in_db = list(db_session.scalars(select(OrderItem)).all())
    assert len(uploads_in_db) == 1
    assert len(items_in_db) == 82

    # Confirma listagem em GET /api/v1/uploads
    list_resp = client.get("/api/v1/uploads")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["upload_id"] == upload_id

    # Confirma métricas detalhadas em GET /api/v1/uploads/{upload_id}/metrics
    metrics_resp = client.get(f"/api/v1/uploads/{upload_id}/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()

    assert metrics["upload_id"] == upload_id
    assert metrics["filename"] == "sample_orders.csv"
    assert metrics["total_rows"] == 82
    assert metrics["financials"] == {
        "gross_revenue": 5000.0,
        "discount_total": 250.0,
        "net_revenue": 4750.0,
        "valid_orders_count": 50,
        "canceled_orders_count": 5,
        "canceled_revenue_loss": 514.0,
        "average_ticket_gross": 100.0,
        "average_ticket_net": 95.0,
    }
    assert len(metrics["abc_curve"]) == 8
    assert metrics["abc_curve"][-1]["cumulative_share_pct"] == 100.0
    assert metrics["bottlenecks"]["delayed_orders_count"] == 5
    assert metrics["bottlenecks"]["delayed_items_count"] == 6
    assert len(metrics["by_channel"]) == 3
    assert len(metrics["by_category"]) == 5


def test_api_get_metrics_for_nonexistent_upload_returns_404_not_found(
    client: SyncASGIClient,
) -> None:
    """Prova que consultar métricas de um `upload_id` inexistente retorna `404 Not Found`."""
    resp = client.get("/api/v1/uploads/id-inexistente/metrics")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Upload 'id-inexistente' não encontrado."}
