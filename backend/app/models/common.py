from enum import StrEnum


class ProjectStatus(StrEnum):
    QUEUED = "queued"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class AnalysisKind(StrEnum):
    MOCK = "mock"
    BEST_EFFORT = "best_effort"
    REAL = "real"
