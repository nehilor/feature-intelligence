from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class RequestText(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)


class RelationshipCase(BaseModel):
    case_id: str
    request_a: RequestText
    request_b: RequestText
    expected_relationship: Literal["DUPLICATE", "RELATED", "DISTINCT"]
    brief_gold_rationale: str = Field(..., min_length=10)
    tags: Optional[List[str]] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None


class RelationshipDataset(BaseModel):
    dataset_version: str
    cases: List[RelationshipCase] = Field(..., min_length=1)


class ThemeCase(BaseModel):
    case_id: str
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    expected_theme: str


class ThemeDataset(BaseModel):
    dataset_version: str
    cases: List[ThemeCase] = Field(..., min_length=1)


class UnderlyingNeedCase(BaseModel):
    case_id: str
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    expected_concepts: List[str] = Field(..., min_length=1)
    forbidden_or_irrelevant_concepts: Optional[List[str]] = None


class UnderlyingNeedDataset(BaseModel):
    dataset_version: str
    cases: List[UnderlyingNeedCase] = Field(..., min_length=1)


class RelationshipPrediction(BaseModel):
    case_id: str
    predicted_relationship: Literal["DUPLICATE", "RELATED", "DISTINCT"]
    structured_output_valid: bool = True


class RelationshipPredictionFixture(BaseModel):
    fixture_version: str
    predictions: List[RelationshipPrediction]


class ThemePrediction(BaseModel):
    case_id: str
    predicted_theme: str
    structured_output_valid: bool = True


class ThemePredictionFixture(BaseModel):
    fixture_version: str
    predictions: List[ThemePrediction]


class UnderlyingNeedPrediction(BaseModel):
    case_id: str
    predicted_concepts: List[str]
    structured_output_valid: bool = True


class UnderlyingNeedPredictionFixture(BaseModel):
    fixture_version: str
    predictions: List[UnderlyingNeedPrediction]


class StructuredOutputCase(BaseModel):
    case_id: str
    structured_output_valid: bool


class StructuredOutputFixture(BaseModel):
    fixture_version: str
    cases: List[StructuredOutputCase]


class EvalBaselines(BaseModel):
    baseline_version: str
    relationship_macro_f1_min: float
    relationship_duplicate_precision_min: float
    relationship_duplicate_recall_min: float
    theme_accuracy_min: float
    underlying_need_mean_recall_min: float
    structured_output_success_rate_min: float
