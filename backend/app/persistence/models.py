from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import FeatureRequestStatus
from app.domain.validation import TITLE_MAX
from app.persistence.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FeatureRequest(Base):
    __tablename__ = "feature_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(TITLE_MAX), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=FeatureRequestStatus.SUBMITTED.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    support_signals: Mapped[list[SupportSignal]] = relationship(
        back_populates="feature_request",
        cascade="all, delete-orphan",
    )
    feature_analysis: Mapped[Optional[FeatureAnalysis]] = relationship(
        back_populates="feature_request",
        cascade="all, delete-orphan",
        uselist=False,
    )


class SupportSignal(Base):
    __tablename__ = "support_signals"
    __table_args__ = (
        UniqueConstraint("feature_request_id", "supporter_key", name="uq_support_per_supporter"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("feature_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    supporter_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    feature_request: Mapped[FeatureRequest] = relationship(back_populates="support_signals")


class FeatureAnalysis(Base):
    __tablename__ = "feature_analyses"
    __table_args__ = (UniqueConstraint("feature_request_id", name="uq_feature_analysis_request"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("feature_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    underlying_need: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    theme: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    customer_impact: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    urgency: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    confidence: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_state: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    used_fallback: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    feature_request: Mapped[FeatureRequest] = relationship(back_populates="feature_analysis")


class AIExecution(Base):
    __tablename__ = "ai_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[Optional[int]] = mapped_column(nullable=True)
    input_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
