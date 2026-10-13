from typing import Optional

from sqlalchemy.orm import Session

from app.persistence.models import AIExecution


class AIExecutionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def record(
        self,
        *,
        feature_request_id: str,
        operation: str,
        status: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        prompt_version: Optional[str] = None,
        latency_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
    ) -> AIExecution:
        row = AIExecution(
            feature_request_id=feature_request_id,
            operation=operation,
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            status=status,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        self._session.add(row)
        self._session.commit()
        return row
