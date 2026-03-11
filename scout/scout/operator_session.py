"""Operator-focused terminal session state and key handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from scout.pipeline.models.lead import Lead


class LeadStateStore(Protocol):
    """Persistence surface needed by the operator loop."""

    def set_lead_saved(self, lead_id: str, is_saved: bool) -> Lead: ...


@dataclass(frozen=True)
class SelectedBusinessDetail:
    """Core factual context shown in the selected-business pane."""

    lead_id: str
    name: str
    source: str
    category: str
    location: str
    address: str
    phone: str
    website: str
    rating: float | None
    reviews: int | None
    is_saved: bool


class OperatorSession:
    """Dense-universe scanning loop with stable selection semantics."""

    def __init__(
        self,
        leads: list[Lead],
        *,
        page_size: int = 12,
        lead_store: LeadStateStore | None = None,
    ) -> None:
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        self.page_size = page_size
        self.lead_store = lead_store
        self._all_leads = list(leads)
        self._filtered_leads = list(leads)
        self.filter_text = ""

        self.selected_index = 0
        self.scroll_offset = 0
        self.detail_open = False
        self._pending_g = False

    @property
    def total(self) -> int:
        return len(self._filtered_leads)

    @property
    def selected_lead(self) -> Lead | None:
        if not self._filtered_leads:
            return None
        return self._filtered_leads[self.selected_index]

    @property
    def visible_leads(self) -> list[Lead]:
        end = self.scroll_offset + self.page_size
        return self._filtered_leads[self.scroll_offset : end]

    def move_up(self) -> None:
        if self.selected_index <= 0:
            return
        self.selected_index -= 1
        self._ensure_selected_visible()

    def move_down(self) -> None:
        if self.selected_index >= self.total - 1:
            return
        self.selected_index += 1
        self._ensure_selected_visible()

    def page_up(self) -> None:
        if self.total == 0:
            return
        self.selected_index = max(0, self.selected_index - self.page_size)
        self._ensure_selected_visible()

    def page_down(self) -> None:
        if self.total == 0:
            return
        self.selected_index = min(self.total - 1, self.selected_index + self.page_size)
        self._ensure_selected_visible()

    def move_to_top(self) -> None:
        if self.total == 0:
            return
        self.selected_index = 0
        self.scroll_offset = 0

    def move_to_bottom(self) -> None:
        if self.total == 0:
            return
        self.selected_index = self.total - 1
        self.scroll_offset = max(0, self.total - self.page_size)

    def apply_filter(self, filter_text: str) -> None:
        selected_lead_id = self.selected_lead.lead_id if self.selected_lead else None
        self.filter_text = filter_text.strip()
        if not self.filter_text:
            self._filtered_leads = list(self._all_leads)
            self._restore_selection(selected_lead_id)
            return

        tokens = [token for token in self.filter_text.lower().split() if token]
        self._filtered_leads = [
            lead for lead in self._all_leads if _matches_tokens(lead=lead, tokens=tokens)
        ]
        self._restore_selection(selected_lead_id)

    def clear_filter(self) -> None:
        self.apply_filter("")

    def open_selected_detail(self) -> bool:
        if self.selected_lead is None:
            return False
        self.detail_open = True
        return True

    def close_detail(self) -> bool:
        if not self.detail_open:
            return False
        self.detail_open = False
        return True

    def save_selected(self) -> Lead | None:
        return self._set_selected_saved(is_saved=True)

    def remove_selected(self) -> Lead | None:
        return self._set_selected_saved(is_saved=False)

    def toggle_selected_saved(self) -> Lead | None:
        lead = self.selected_lead
        if lead is None:
            return None
        return self._set_selected_saved(is_saved=not lead.is_saved)

    def selected_business_detail(self) -> SelectedBusinessDetail | None:
        lead = self.selected_lead
        if lead is None:
            return None
        return SelectedBusinessDetail(
            lead_id=lead.lead_id,
            name=lead.name,
            source=lead.source,
            category=lead.category,
            location=lead.location,
            address=lead.address,
            phone=lead.phone,
            website=lead.website,
            rating=lead.rating,
            reviews=lead.reviews,
            is_saved=lead.is_saved,
        )

    def handle_key(self, key: str) -> bool:
        normalized = key.strip()
        if not normalized:
            return False

        lowered = normalized.lower()
        if lowered != "g":
            self._pending_g = False

        if lowered in {"up", "arrow_up", "k"}:
            self.move_up()
            return True
        if lowered in {"down", "arrow_down", "j"}:
            self.move_down()
            return True
        if lowered in {"page_up", "pgup", "ctrl+u", "ctrl-u"}:
            self.page_up()
            return True
        if lowered in {"page_down", "pgdn", "ctrl+d", "ctrl-d"}:
            self.page_down()
            return True
        if lowered in {"home"}:
            self.move_to_top()
            return True
        if lowered in {"end"} or normalized == "G":
            self.move_to_bottom()
            return True
        if lowered == "g":
            if self._pending_g:
                self.move_to_top()
                self._pending_g = False
            else:
                self._pending_g = True
            return True
        if lowered in {"enter", "return"}:
            return self.open_selected_detail()
        if lowered in {"esc", "escape"}:
            return self.close_detail()
        if lowered in {"s"}:
            self.save_selected()
            return True
        if lowered in {"x", "delete", "backspace"}:
            self.remove_selected()
            return True
        return False

    def render_dense_list(self) -> str:
        if self.total == 0:
            return "universe: empty"

        start = self.scroll_offset + 1
        end = min(self.total, self.scroll_offset + len(self.visible_leads))
        filter_text = self.filter_text if self.filter_text else "-"
        lines = [f"universe: {start}-{end} of {self.total} filter={filter_text}"]
        for idx, lead in enumerate(self.visible_leads, start=self.scroll_offset):
            marker = ">" if idx == self.selected_index else " "
            saved = "saved" if lead.is_saved else "open"
            reviews = lead.reviews if lead.reviews is not None else 0
            lines.append(
                f"{marker} {idx + 1:>4} {lead.name} | {reviews} reviews | {lead.location} | {saved}"
            )
        return "\n".join(lines)

    def render_selected_business_pane(self) -> str:
        detail = self.selected_business_detail()
        if detail is None:
            return "selected_business: none"

        rating = f"{detail.rating:.1f}" if detail.rating is not None else "-"
        reviews = str(detail.reviews) if detail.reviews is not None else "0"
        saved = "yes" if detail.is_saved else "no"
        lines = [
            f"selected_business: {detail.name}",
            f"lead_id: {detail.lead_id}",
            f"saved: {saved}",
            f"source: {detail.source}",
            f"category: {detail.category or '-'}",
            f"location: {detail.location or '-'}",
            f"address: {detail.address or '-'}",
            f"phone: {detail.phone or '-'}",
            f"website: {detail.website or '-'}",
            f"rating: {rating}",
            f"reviews: {reviews}",
        ]
        return "\n".join(lines)

    def _set_selected_saved(self, *, is_saved: bool) -> Lead | None:
        lead = self.selected_lead
        if lead is None:
            return None

        if self.lead_store is None:
            updated = Lead(
                lead_id=lead.lead_id,
                source=lead.source,
                name=lead.name,
                address=lead.address,
                phone=lead.phone,
                website=lead.website,
                category=lead.category,
                location=lead.location,
                state=lead.state,
                rating=lead.rating,
                reviews=lead.reviews,
                is_saved=is_saved,
                saved_at=lead.saved_at,
                updated_at=lead.updated_at,
            )
        else:
            updated = self.lead_store.set_lead_saved(lead.lead_id, is_saved=is_saved)
        self._replace_lead(updated)
        return updated

    def _replace_lead(self, updated_lead: Lead) -> None:
        self._all_leads = [
            updated_lead if lead.lead_id == updated_lead.lead_id else lead
            for lead in self._all_leads
        ]
        self._filtered_leads = [
            updated_lead if lead.lead_id == updated_lead.lead_id else lead
            for lead in self._filtered_leads
        ]

    def _restore_selection(self, lead_id: str | None) -> None:
        if self.total == 0:
            self.selected_index = 0
            self.scroll_offset = 0
            self.detail_open = False
            return

        if lead_id:
            for idx, lead in enumerate(self._filtered_leads):
                if lead.lead_id == lead_id:
                    self.selected_index = idx
                    break
            else:
                self.selected_index = min(self.selected_index, self.total - 1)
        else:
            self.selected_index = min(self.selected_index, self.total - 1)

        self._ensure_selected_visible()

    def _ensure_selected_visible(self) -> None:
        if self.total == 0:
            self.selected_index = 0
            self.scroll_offset = 0
            return

        self.selected_index = min(max(0, self.selected_index), self.total - 1)
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.page_size:
            self.scroll_offset = self.selected_index - self.page_size + 1

        max_offset = max(0, self.total - self.page_size)
        self.scroll_offset = min(max(0, self.scroll_offset), max_offset)


def _matches_tokens(*, lead: Lead, tokens: list[str]) -> bool:
    haystack = " ".join(
        [
            lead.name.lower(),
            lead.category.lower(),
            lead.location.lower(),
            lead.state.lower(),
            lead.address.lower(),
        ]
    )
    return all(token in haystack for token in tokens)
