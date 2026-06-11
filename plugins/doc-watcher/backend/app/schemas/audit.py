from typing import Literal

from pydantic import BaseModel


class CommitCounterRunRequest(BaseModel):
    config_path: str | None = None
    state_dir: str | None = None


class GenerateReportRunRequest(BaseModel):
    config_path: str | None = None
    state_dir: str | None = None
    mode: Literal["all", "commit-dependent"] = "all"
    mark_audited: bool = False
    digest: bool = False
    print_report: bool = False


class RepoAuditRunRequest(BaseModel):
    config_path: str | None = None
    state_dir: str | None = None
    print_report: bool = False
