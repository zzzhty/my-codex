from fastapi import APIRouter, HTTPException, Query

from app.schemas.audit import CommitCounterRunRequest, GenerateReportRunRequest, RepoAuditRunRequest
from app.services.audit_read_model import AuditReadError, AuditReadModel
from app.services.audit_runner import AuditCommandRunner

router = APIRouter()


def _model(
    config_path: str | None,
    state_dir: str | None,
) -> AuditReadModel:
    return AuditReadModel(config_path=config_path, state_dir=state_dir)


def _handle_error(exc: AuditReadError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/status")
def audit_status(
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return _model(config_path, state_dir).overview()
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/repos")
def list_audit_repos(
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return _model(config_path, state_dir).repo_list()
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/repos/{repo_name}")
def get_audit_repo(
    repo_name: str,
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return _model(config_path, state_dir).repo_detail(repo_name)
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/reports")
def list_audit_reports(
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return _model(config_path, state_dir).report_list()
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/reports/{report_id}")
def get_audit_report(
    report_id: str,
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return _model(config_path, state_dir).report_detail(report_id)
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/last-run")
def get_last_audit_run(
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return _model(config_path, state_dir).last_run()
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/runs")
def list_command_runs(
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return AuditCommandRunner(config_path=config_path, state_dir=state_dir).list_runs()
    except AuditReadError as exc:
        _handle_error(exc)


@router.get("/runs/{run_id}")
def get_command_run(
    run_id: str,
    config_path: str | None = Query(default=None),
    state_dir: str | None = Query(default=None),
):
    try:
        return AuditCommandRunner(config_path=config_path, state_dir=state_dir).get_run(run_id)
    except AuditReadError as exc:
        _handle_error(exc)


@router.post("/runs/commit-counter")
def run_commit_counter(request: CommitCounterRunRequest):
    try:
        return AuditCommandRunner(
            config_path=request.config_path,
            state_dir=request.state_dir,
        ).run_commit_counter()
    except AuditReadError as exc:
        _handle_error(exc)


@router.post("/runs/generate-report")
def run_generate_report(request: GenerateReportRunRequest):
    try:
        return AuditCommandRunner(
            config_path=request.config_path,
            state_dir=request.state_dir,
        ).run_generate_report(
            mode=request.mode,
            mark_audited=request.mark_audited,
            digest=request.digest,
            print_report=request.print_report,
        )
    except AuditReadError as exc:
        _handle_error(exc)


@router.post("/repos/{repo_name}/runs/audit")
def run_repo_audit(repo_name: str, request: RepoAuditRunRequest):
    try:
        return AuditCommandRunner(
            config_path=request.config_path,
            state_dir=request.state_dir,
        ).run_repo_audit(repo_name=repo_name, print_report=request.print_report)
    except AuditReadError as exc:
        _handle_error(exc)
