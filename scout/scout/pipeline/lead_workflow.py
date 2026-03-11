"""Lead workflow queue + handler execution service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from scout.pipeline.data_store.sqlite import SQLiteDataStore, normalize_workflow_action
from scout.pipeline.models.lead import Lead


@dataclass(frozen=True)
class WorkflowExecutionResult:
    run_id: int
    lead_id: str
    action: str
    status: str
    summary: str = ""
    artifact_id: int | None = None
    error: str = ""


class LeadWorkflowService:
    """Queues and executes lead-scoped workflow handlers."""

    def __init__(
        self,
        *,
        db_path: str = "outputs/pipeline/canonical.db",
        data_store: SQLiteDataStore | None = None,
    ) -> None:
        self._owns_store = data_store is None
        self.store = data_store or SQLiteDataStore(db_path=db_path)

    def close(self) -> None:
        if self._owns_store:
            self.store.close()

    def trigger(
        self,
        *,
        lead_id: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> int:
        normalized_action = normalize_workflow_action(action)
        lead = self.store.get_lead(lead_id)
        if lead is None:
            raise ValueError(f"lead_id not found: {lead_id}")
        return self.store.queue_workflow_action(
            lead_id=lead.lead_id,
            action=normalized_action,
            payload=payload,
        )

    def run_next(self) -> WorkflowExecutionResult | None:
        run = self.store.claim_next_workflow_action()
        if run is None:
            return None

        run_id = int(run["id"])
        lead_id = str(run["lead_id"])
        action = str(run["action"])
        lead = self.store.get_lead(lead_id)
        if lead is None:
            error = f"lead_id not found: {lead_id}"
            self.store.fail_workflow_action(run_id=run_id, error=error)
            return WorkflowExecutionResult(
                run_id=run_id,
                lead_id=lead_id,
                action=action,
                status="failed",
                error=error,
            )

        try:
            summary, content = self._execute_handler(action=action, lead=lead)
            artifact_id = self.store.save_workflow_artifact(
                lead_id=lead.lead_id,
                action=action,
                summary=summary,
                content=content,
            )
            self.store.complete_workflow_action(
                run_id=run_id,
                summary=summary,
                artifact_id=artifact_id,
            )
            return WorkflowExecutionResult(
                run_id=run_id,
                lead_id=lead.lead_id,
                action=action,
                status="completed",
                summary=summary,
                artifact_id=artifact_id,
            )
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            self.store.fail_workflow_action(run_id=run_id, error=error)
            return WorkflowExecutionResult(
                run_id=run_id,
                lead_id=lead.lead_id,
                action=action,
                status="failed",
                error=error,
            )

    def run_batch(self, *, max_jobs: int = 25) -> list[WorkflowExecutionResult]:
        if max_jobs < 1:
            raise ValueError("max_jobs must be >= 1")
        results: list[WorkflowExecutionResult] = []
        for _ in range(max_jobs):
            result = self.run_next()
            if result is None:
                break
            results.append(result)
        return results

    def run_until_empty(self, *, max_jobs: int = 25) -> int:
        return len(self.run_batch(max_jobs=max_jobs))

    def list_runs(
        self,
        *,
        lead_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.store.list_workflow_runs(lead_id=lead_id, status=status, limit=limit)

    def list_artifacts(
        self,
        *,
        lead_id: str,
        action: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        return self.store.list_workflow_artifacts(lead_id=lead_id, action=action, limit=limit)

    def _execute_handler(self, *, action: str, lead: Lead) -> tuple[str, dict[str, Any]]:
        normalized_action = normalize_workflow_action(action)
        if normalized_action == "research":
            return self._handle_research(lead)
        if normalized_action == "enrich":
            return self._handle_enrich(lead)
        if normalized_action == "prepare-call":
            return self._handle_prepare_call(lead)
        if normalized_action == "draft-email":
            return self._handle_draft_email(lead)
        raise ValueError(f"unsupported workflow action: {normalized_action}")

    def _handle_research(self, lead: Lead) -> tuple[str, dict[str, Any]]:
        highlights = [
            f"Lead source: {lead.source}.",
            f"Lead type: {lead.lead_type}.",
        ]
        if lead.industry:
            highlights.append(f"Industry focus: {lead.industry}.")
        if lead.location:
            highlights.append(f"Market location: {lead.location}.")
        if lead.rating is not None and lead.reviews is not None:
            highlights.append(
                f"Reputation signal: rating {lead.rating:.1f} from {lead.reviews} reviews."
            )
        elif lead.reviews is not None:
            highlights.append(f"Review volume signal: {lead.reviews} reviews.")
        if lead.asking_price is not None:
            highlights.append(f"Asking price observed: {self._fmt_currency(lead.asking_price)}.")
        if lead.annual_revenue is not None:
            highlights.append(
                f"Annual revenue observed: {self._fmt_currency(lead.annual_revenue)}."
            )
        if lead.cash_flow is not None:
            highlights.append(f"Cash flow observed: {self._fmt_currency(lead.cash_flow)}.")

        risks: list[str] = []
        if not lead.phone and not lead.website and not lead.url:
            risks.append("No direct contact channel is stored yet.")
        if lead.reviews is not None and lead.reviews < 20:
            risks.append("Limited review history may reduce confidence.")
        if lead.cash_flow and lead.asking_price and lead.cash_flow > 0:
            multiple = lead.asking_price / lead.cash_flow
            if multiple > 6:
                risks.append("Implied asking multiple is high relative to SMB norms.")

        summary = f"Research brief ready for {lead.name}."
        content = {
            "lead": lead.to_dict(),
            "highlights": highlights,
            "risks": risks,
            "next_step": "run enrich, then prepare-call and draft-email",
        }
        return summary, content

    def _handle_enrich(self, lead: Lead) -> tuple[str, dict[str, Any]]:
        source_url = lead.website or lead.url
        domain = self._extract_domain(source_url)

        contact_channels: list[str] = []
        if lead.phone:
            contact_channels.append("phone")
        if lead.website:
            contact_channels.append("website")
        elif lead.url:
            contact_channels.append("listing_url")

        implied_multiple = None
        if lead.asking_price and lead.cash_flow and lead.cash_flow > 0:
            implied_multiple = round(lead.asking_price / lead.cash_flow, 2)

        summary = (
            f"Enrichment profile ready for {lead.name} "
            f"with {len(contact_channels)} contact channel(s)."
        )
        content = {
            "lead": lead.to_dict(),
            "domain": domain,
            "contact_channels": contact_channels,
            "has_phone": bool(lead.phone),
            "has_website": bool(lead.website),
            "implied_multiple": implied_multiple,
        }
        return summary, content

    def _handle_prepare_call(self, lead: Lead) -> tuple[str, dict[str, Any]]:
        research = self.store.get_latest_workflow_artifact(lead_id=lead.lead_id, action="research")
        enrich = self.store.get_latest_workflow_artifact(lead_id=lead.lead_id, action="enrich")

        agenda = [
            f"Confirm owner goals and timing for {lead.name}.",
            "Validate service mix, customer concentration, and retention profile.",
            "Clarify financial quality (normalization adjustments and capex expectations).",
        ]
        if research is not None:
            agenda.append(f"Review prior research brief: {research['summary']}")
        if enrich is not None:
            channels = enrich["content"].get("contact_channels", [])
            if channels:
                agenda.append(f"Use known contact channels: {', '.join(channels)}.")

        questions = [
            "What percent of revenue is recurring vs one-off?",
            "Which customer segments drive the highest gross margin?",
            "What owner tasks can transition in the first 90 days?",
        ]
        opening = f"Thanks for taking time to speak today about {lead.name}."
        summary = f"Call prep brief ready for {lead.name}."
        content = {
            "lead": lead.to_dict(),
            "opening": opening,
            "agenda": agenda,
            "questions": questions,
        }
        return summary, content

    def _handle_draft_email(self, lead: Lead) -> tuple[str, dict[str, Any]]:
        research = self.store.get_latest_workflow_artifact(lead_id=lead.lead_id, action="research")
        enrich = self.store.get_latest_workflow_artifact(lead_id=lead.lead_id, action="enrich")

        industry_phrase = lead.industry or "your business"
        location_phrase = f" in {lead.location}" if lead.location else ""
        subject = f"Intro regarding {lead.name}"

        lines = [
            f"Hi {lead.name} team,",
            "",
            f"I'm reaching out while researching {industry_phrase} operators{location_phrase}.",
        ]
        if research is not None:
            lines.append(f"Current research note: {research['summary']}")
        if enrich is not None:
            channel_count = len(enrich["content"].get("contact_channels", []))
            lines.append(f"We currently have {channel_count} known contact channel(s) on file.")
        lines.extend(
            [
                "",
                "If this is relevant, I can share a short diligence agenda and compare notes.",
                "Would you be open to a 20-minute introductory call next week?",
                "",
                "Best regards,",
                "Scout Operator",
            ]
        )
        body = "\n".join(lines)

        summary = f"Intro email draft ready for {lead.name}."
        content = {
            "lead": lead.to_dict(),
            "subject": subject,
            "body": body,
        }
        return summary, content

    def _extract_domain(self, value: str) -> str:
        if not value:
            return ""
        candidate = value.strip()
        if "://" not in candidate:
            candidate = f"https://{candidate}"
        parsed = urlparse(candidate)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain

    def _fmt_currency(self, value: float) -> str:
        return f"${value:,.0f}"
