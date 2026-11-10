"""Modelos ORM (SQLAlchemy 2.x) para lotes de upload, itens de pedido e execuções de recomendações."""

import json
from typing import Any

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Upload(Base):
    """Representa um lote de arquivo CSV importado de forma atômica."""

    __tablename__ = "uploads"

    upload_id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_orders_count: Mapped[int] = mapped_column(Integer, nullable=False)
    canceled_orders_count: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_metrics_json: Mapped[str] = mapped_column(Text, nullable=False)

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="upload",
        cascade="all, delete-orphan",
        order_by="OrderItem.id",
    )

    recommendation_runs: Mapped[list["RecommendationRun"]] = relationship(
        "RecommendationRun",
        back_populates="upload",
        cascade="all, delete-orphan",
        order_by="RecommendationRun.generated_at.desc()",
    )

    @property
    def summary_metrics(self) -> dict[str, Any]:
        """Desserializa o resumo executivo de métricas do lote."""
        return json.loads(self.summary_metrics_json)


class OrderItem(Base):
    """Representa uma linha (item de pedido) validada e vinculada a um Upload."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("uploads.upload_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount: Mapped[float] = mapped_column(Float, nullable=False)
    prep_time_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)

    upload: Mapped["Upload"] = relationship("Upload", back_populates="items")

    def to_record(self) -> dict[str, Any]:
        """Converte a entidade ORM para o formato de dicionário esperado por `calculate_metrics`."""
        return {
            "order_id": self.order_id,
            "timestamp": self.timestamp,
            "item_name": self.item_name,
            "category": self.category,
            "quantity": int(self.quantity),
            "unit_price": float(self.unit_price),
            "discount": float(self.discount),
            "prep_time_minutes": float(self.prep_time_minutes),
            "status": self.status,
            "channel": self.channel,
        }


class RecommendationRun(Base):
    """Persistência de uma rodada de geração de recomendações para um lote (RN-10)."""

    __tablename__ = "recommendation_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    upload_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("uploads.upload_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_at: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    warnings_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    upload: Mapped["Upload"] = relationship("Upload", back_populates="recommendation_runs")

    @property
    def recommendations(self) -> list[dict[str, Any]]:
        """Desserializa a lista de 3 recomendações da execução."""
        return json.loads(self.payload_json)

    @property
    def warnings(self) -> list[str]:
        """Desserializa eventuais avisos da execução."""
        return json.loads(self.warnings_json)
