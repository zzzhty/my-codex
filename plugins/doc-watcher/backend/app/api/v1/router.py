from fastapi import APIRouter

from app.api.v1 import audit


def build_router(*, include_legacy_routes: bool = False) -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    router.include_router(audit.router, prefix="/audit", tags=["audit"])
    if include_legacy_routes:
        from app.api.v1 import changes, dashboard, doc_prs, docs, impacts, patches, projects, webhooks

        router.include_router(projects.router, prefix="/projects", tags=["projects"])
        router.include_router(changes.router, prefix="/projects", tags=["changes"])
        router.include_router(impacts.router, prefix="/projects", tags=["impacts"])
        router.include_router(patches.router, prefix="/projects", tags=["patches"])
        router.include_router(doc_prs.router, prefix="/projects", tags=["doc-prs"])
        router.include_router(docs.router, prefix="/projects", tags=["docs"])
        router.include_router(dashboard.router, prefix="/dashboard/projects", tags=["dashboard"])
        router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    return router


router = build_router()
