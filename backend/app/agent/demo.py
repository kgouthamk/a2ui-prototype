"""Offline demo payload — lets the app run with NO API key (A2UI_DEMO=1).
Exercises every widget in the catalog so the renderer can be seen end-to-end.
"""
from app.schema.a2ui import A2UINode, EnrichResult, WidgetType as W

DEMO = EnrichResult(
    markdown=(
        "# Deployment Guide\n\n"
        "## Steps\n"
        "1. Build the image\n2. Push to the registry\n3. Roll out\n\n"
        "> **Warning:** never deploy on Friday.\n\n"
        "## Environments\n\n"
        "| Env | Region | Replicas |\n|---|---|---|\n"
        "| staging | us-west-2 | 1 |\n| prod | us-west-2 | 3 |\n\n"
        "**Tags:** infra, kubernetes, prod\n"
    ),
    a2ui=A2UINode(
        type=W.CARD,
        children=[
            A2UINode(type=W.HEADING, props={"text": "Deployment Guide", "level": 4}),
            A2UINode(type=W.ALERT, props={"severity": "warning", "text": "Never deploy on Friday."}),
            A2UINode(
                type=W.SECTION,
                props={"title": "Steps"},
                children=[
                    A2UINode(
                        type=W.STEPPER,
                        props={"steps": [
                            {"label": "Build the image", "detail": "docker build -t app ."},
                            {"label": "Push to the registry", "detail": "docker push app"},
                            {"label": "Roll out", "detail": "kubectl rollout restart deploy/app"},
                        ]},
                    )
                ],
            ),
            A2UINode(
                type=W.SECTION,
                props={"title": "Environments"},
                children=[
                    A2UINode(type=W.TABLE, props={
                        "columns": ["Env", "Region", "Replicas"],
                        "rows": [["staging", "us-west-2", "1"], ["prod", "us-west-2", "3"]],
                    })
                ],
            ),
            A2UINode(
                type=W.SECTION,
                props={"title": "Specs"},
                children=[
                    A2UINode(type=W.KEY_VALUE_LIST, props={"items": [
                        {"key": "Region", "value": "us-west-2"},
                        {"key": "Port", "value": "8080"},
                        {"key": "Tier", "value": "prod"},
                    ]})
                ],
            ),
            A2UINode(type=W.DIVIDER),
            A2UINode(type=W.CHIP_GROUP, props={"chips": ["infra", "kubernetes", "prod"]}),
            A2UINode(type=W.ACCORDION, props={"panels": [
                {"summary": "Is rollback automatic?", "detail": "Yes, on failed health checks."},
                {"summary": "Who approves prod?", "detail": "On-call lead via the deploy channel."},
            ]}),
            A2UINode(type=W.LIST, props={"items": ["Runbook linked in wiki", "Alerts route to #oncall"]}),
        ],
    ),
)
