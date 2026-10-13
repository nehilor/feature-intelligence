import uuid
from datetime import datetime, timezone

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

    support_signals: Mapped[list["SupportSignal"]] = relationship(
        back_populates="feature_request",
        cascade="all, delete-orphan",
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
