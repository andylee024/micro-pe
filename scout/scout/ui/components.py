"""UI components for Rich terminal display — 4-pane Bloomberg layout"""

from typing import Dict, List, Optional

import rich.box
from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _kv(t: Text, label: str, value: str, note: str = "", value_style: str = "white") -> None:
    t.append(f"    {label:<18}", style="dim white")
    t.append(f"{value}", style=value_style)
    if note:
        t.append(f"  ({note})", style="dim white")
    t.append("\n")


def _stars(rating: float) -> str:
    full = int(round(float(rating)))
    empty = 5 - full
    return "★" * full + "☆" * empty


def _grade_style(grade: str) -> str:
    """Return Rich style for an outlook grade."""
    g = (grade or "").strip().upper()
    if g.startswith("A"):
        return "bold green"
    if g.startswith("B"):
        return "green"
    if g.startswith("C"):
        return "yellow"
    if g and g != "—":
        return "red"
    return "dim white"


def _trend_style(value: str) -> str:
    """Return Rich style based on trend direction indicator."""
    if "↑" in value or "+" in value:
        return "green"
    if "↓" in value or "▼" in value:
        return "red"
    return "white"


# ─────────────────────────────────────────────────────────────────────────────
# Pane 1 — Market Overview (top-left)
# ─────────────────────────────────────────────────────────────────────────────

def create_market_overview_panel(
    market_data: Dict,
    focused: bool = False,
    show_sources: bool = False,
) -> Panel:
    """Market size, financial benchmarks, quality metrics, trends, outlook."""
    border = "cyan" if focused else "dim white"
    t = Text()

    if not market_data:
        t.append("\n  No market data loaded.\n", style="dim white")
        t.append("  Run a search to populate this pane.\n", style="dim white")
        return Panel(
            t,
            title="[dim white]market overview[/dim white]",
            border_style=border,
            padding=(0, 0),
        )

    fin = market_data.get("financial", {})
    quality = market_data.get("quality", {})
    trends = market_data.get("trends", {})
    outlook = market_data.get("outlook", {})
    fdd_count = fin.get("fdd_count", 0)
    grade = outlook.get("grade", "—")

    if show_sources:
        sources = market_data.get("sources", {})
        fdd_filings = sources.get("fdd_filings", [])
        bbs = sources.get("bizbuysell", {})
        t.append("\n  FDD FILINGS  ", style="bold white")
        t.append(f"({len(fdd_filings)} filings · NASAA/state portals)\n\n", style="dim white")
        for f in fdd_filings:
            t.append(f"    {f['name']:<32}", style="white")
            t.append(f"{f['year']}  ", style="dim white")
            t.append(f"{f['avg_unit_revenue']} avg\n", style="white")
        t.append("\n  BIZBUYSELL  ", style="bold white")
        t.append(f"({bbs.get('listing_count', 0)} listings · {bbs.get('period', '')})\n\n", style="dim white")
        _kv(t, "Median ask", bbs.get("median_ask", "—"))
        _kv(t, "Revenue range", bbs.get("revenue_range", "—"))
        _kv(t, "Cash flow range", bbs.get("cashflow_range", "—"))
        _kv(t, "Avg days listed", str(bbs.get("avg_days_listed", "—")))
        t.append("\n  ")
        t.append("Esc", style="dim cyan")
        t.append("  back to summary\n", style="dim white")
        return Panel(
            t,
            title="[dim white]market overview[/dim white]",
            subtitle="[dim white]sources[/dim white]",
            border_style=border,
            padding=(0, 0),
        )

    total = market_data.get("total_businesses", 0)
    density = market_data.get("market_density", "—")
    est_value = market_data.get("est_market_value", "")

    t.append(f"\n  {total:,} businesses", style="bold white")
    t.append(f"  ·  {density}", style="dim white")
    if est_value:
        t.append(f"  ·  {est_value}\n\n", style="dim white")
    else:
        t.append("\n\n")

    # Financials
    conf = fin.get("confidence", "—").lower()
    t.append("  FINANCIALS  ", style="bold white")
    t.append(f"{fdd_count} FDDs · {conf}\n", style="dim white")
    _kv(t, "Median revenue", fin.get("median_revenue", "—"), fin.get("revenue_range", ""))
    _kv(t, "EBITDA margin", fin.get("ebitda_margin", "—"), fin.get("margin_range", ""))
    _kv(t, "Typical acq.", fin.get("typical_acquisition", "—"))
    t.append("\n")

    # Quality
    rating = quality.get("avg_rating", 0.0)
    pos_pct = quality.get("sentiment_positive", 0)
    t.append("  QUALITY\n", style="bold white")
    t.append(f"    {'Avg rating':<18}", style="dim white")
    t.append(_stars(rating), style="yellow")
    t.append(f"  {rating}\n", style="white")
    t.append(f"    {'Sentiment':<18}", style="dim white")
    sentiment_style = "green" if pos_pct >= 60 else "yellow" if pos_pct >= 40 else "red"
    t.append(f"{pos_pct}%", style=sentiment_style)
    t.append(" positive\n", style="dim white")
    vol = quality.get("review_volume", 0)
    vol_str = f"{int(vol):,}" if isinstance(vol, (int, float)) and vol else "—"
    _kv(t, "Review vol.", vol_str)
    t.append("\n")

    # Trends
    t.append("  TRENDS  ", style="bold white")
    t.append("30 days\n", style="dim white")
    for label, key in [("Job postings", "job_postings"), ("New entrants", "new_entrants"), ("Search vol.", "search_volume")]:
        val = trends.get(key, "—")
        _kv(t, label, str(val), value_style=_trend_style(str(val)))
    t.append("\n")

    # Outlook
    note = outlook.get("note", "")
    t.append("  OUTLOOK  ", style="bold white")
    t.append(f"Grade ", style="bold white")
    t.append(grade, style=_grade_style(grade))
    if note:
        t.append(f"  ·  {note}\n", style="dim white")
    else:
        t.append("\n")

    hint = r"  \[s] sources" if focused else ""
    return Panel(
        t,
        title="[dim white]market overview[/dim white]",
        subtitle=f"[dim white]{grade} market · {fdd_count} fdds{hint}[/dim white]",
        border_style=border,
        padding=(0, 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pane 2 — Target List (top-right)
# ─────────────────────────────────────────────────────────────────────────────

def create_target_list_panel(
    businesses: List[Dict],
    offset: int = 0,
    limit: int = 8,
    selected_index: int = 0,
    focused: bool = False,
) -> Panel:
    """Scrollable business list with cursor highlight."""
    t = Text()

    if not businesses:
        t.append("\n  No results yet — searching...\n", style="dim white")
        return Panel(
            t,
            title="[dim white]target list[/dim white]",
            border_style="cyan" if focused else "dim white",
            padding=(0, 0),
        )

    t.append("\n")

    end_idx = min(offset + limit, len(businesses))

    for abs_idx, biz in enumerate(businesses[offset:end_idx], start=offset):
        is_selected = abs_idx == selected_index
        rank = abs_idx + 1
        name = biz.get("name", "—")
        rating = biz.get("rating")
        reviews = biz.get("reviews") or 0

        # Line 1: cursor, rank, name
        if is_selected:
            t.append(f"  ▶ {rank:<3}", style="bold white")
            t.append(f"{name}\n", style="bold white underline")
        else:
            t.append(f"    {rank:<3}", style="dim white")
            t.append(f"{name}\n", style="white")

        # Line 2: rating (yellow stars) + reviews [+ confidence if selected]
        t.append("       ")
        if rating is not None:
            t.append(_stars(rating), style="yellow")
            t.append(f"  {rating}", style="white" if is_selected else "dim white")
            if reviews:
                t.append("  ", style="")
        if reviews:
            t.append(f"{reviews:,} reviews", style="white" if is_selected else "dim white")
        if rating is None and not reviews:
            t.append("—", style="dim white")
        # Confidence badge on selected row
        if is_selected:
            conf = biz.get("confidence", "")
            if conf:
                conf_style = "green" if conf == "high" else "yellow" if conf == "medium" else "dim white"
                t.append(f"  · {conf}", style=conf_style)
        t.append("\n")

        t.append("\n")

    subtitle = f"{offset + 1}–{end_idx} of {len(businesses)}"
    return Panel(
        t,
        title="[dim white]target list[/dim white]",
        subtitle=f"[dim white]{subtitle}[/dim white]",
        border_style="cyan" if focused else "dim white",
        padding=(0, 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pane 3 — Business Profile (bottom-left)
# ─────────────────────────────────────────────────────────────────────────────

def create_business_profile_panel(
    business: Optional[Dict] = None,
    market_data: Optional[Dict] = None,
) -> Panel:
    """Deep-dive profile for a selected business target."""
    if not business:
        t = Text()
        t.append("\n  Select a business from the target list\n", style="dim white")
        t.append("  to view its detailed profile here.\n\n", style="dim white")
        t.append("  [↑↓] navigate   [Enter] open\n", style="dim white")
        return Panel(
            t,
            title="[dim white]business profile[/dim white]",
            border_style="white",
            padding=(0, 0),
        )

    t = Text()
    name = business.get("name", "—")
    score = business.get("score")
    location = business.get("location") or ""

    t.append(f"\n  {name}\n", style="bold white")
    if location:
        t.append(f"  {location}\n", style="dim white")
    t.append("\n")

    # Contact
    phone = business.get("phone") or "—"
    website = business.get("website") or ""
    address = business.get("address") or "—"
    t.append("  CONTACT\n", style="bold white")
    t.append(f"    {phone}", style="white")
    if website:
        t.append(f"  ·  {website}", style="dim white")
    t.append("\n")
    t.append("    [W] website  [R] reviews\n", style="dim white")
    t.append(f"    {address}\n\n", style="dim white")

    # Financials
    rev = business.get("revenue") or business.get("est_revenue") or ""
    rev_vs = business.get("revenue_vs_median") or ""
    ebitda = business.get("ebitda") or ""
    ebitda_vs = business.get("ebitda_vs_median") or ""
    valuation = business.get("valuation") or ""

    if rev or ebitda or valuation:
        confidence = business.get("confidence", "")
        conf_label = f"  (estimated · {confidence} confidence)" if confidence else "  (estimated)"
        t.append("  FINANCIALS", style="bold white")
        t.append(conf_label + "\n", style="dim white")
        if rev:
            t.append(f"    Revenue    {rev:<14}", style="white")
            if rev_vs:
                t.append(rev_vs, style="dim white")
            t.append("\n")
        if ebitda:
            t.append(f"    EBITDA     {ebitda:<14}", style="white")
            if ebitda_vs:
                t.append(ebitda_vs, style="dim white")
            t.append("\n")
        if valuation:
            t.append(f"    Value      {valuation}\n", style="white")
        t.append("\n")
    else:
        t.append("  FINANCIALS\n", style="bold white")
        t.append("    Financial estimates: not available\n", style="dim white")
        t.append("\n")

    # Reviews
    rating = business.get("rating")
    review_count = business.get("reviews") or 0
    if rating:
        t.append("  REVIEWS  ", style="bold white")
        t.append(f"{_stars(rating)} {rating}", style="white")
        t.append(f"  ({review_count} reviews)\n", style="dim white")
        themes = business.get("review_themes_pos") or []
        if themes:
            theme_str = "  ·  ".join(f'"{kw}"' for kw, _ in themes[:3])
            t.append(f"    {theme_str}\n", style="dim white")
        t.append("\n")

    # Next steps
    next_steps = business.get("next_steps") or []
    if next_steps:
        t.append("  NEXT STEPS\n", style="bold white")
        for i, step in enumerate(next_steps[:4], 1):
            t.append(f"    {i}. {step}\n", style="dim white")

    title_str = name[:22].lower()
    confidence = business.get("confidence", "")
    subtitle_str = f"· {confidence}" if confidence else ""

    return Panel(
        t,
        title=f"[dim white]{title_str}[/dim white]",
        subtitle=f"[dim white]{subtitle_str}[/dim white]",
        border_style="white",
        padding=(0, 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pane 4 — Market Pulse (bottom-right)
# ─────────────────────────────────────────────────────────────────────────────

def create_market_pulse_panel(
    pulse_data: Dict,
    focused: bool = False,
    show_sources: bool = False,
) -> Panel:
    """Compact qualitative pulse: business model, operating models, opportunities, risks."""
    border = "cyan" if focused else "dim white"
    t = Text()

    if not pulse_data:
        t.append("\n  No market pulse data loaded.\n", style="dim white")
        return Panel(
            t,
            title="[dim white]market pulse[/dim white]",
            border_style=border,
            padding=(0, 0),
        )

    business_model = pulse_data.get("business_model", {})
    operating_models = pulse_data.get("operating_models", [])
    opportunities = pulse_data.get("opportunities", [])
    risks = pulse_data.get("risks", [])
    sources = pulse_data.get("sources", {})

    if show_sources:
        reddit_threads = sources.get("reddit_threads", [])
        report_list = sources.get("report_list", [])
        t.append("\n  REDDIT  ", style="bold white")
        total = sources.get('reddit', len(reddit_threads))
        shown = len(reddit_threads)
        count_str = f"({shown} shown of {total} total)\n\n" if total > shown else f"({shown} threads)\n\n"
        t.append(count_str, style="dim white")
        for thread in reddit_threads:
            t.append(f"    {thread.get('title', '')}\n", style="white")
            t.append(f"    {thread.get('sub', '')}  ", style="dim white")
            t.append(f'"{thread.get("excerpt", "")}"\n\n', style="dim white")
        t.append("  REPORTS  ", style="bold white")
        t.append(f"({len(report_list)} sources)\n\n", style="dim white")
        for report in report_list:
            t.append(f"    • {report}\n", style="dim white")
        t.append("\n  ")
        t.append("Esc", style="dim cyan")
        t.append("  back to summary\n", style="dim white")
        return Panel(
            t,
            title="[dim white]market pulse[/dim white]",
            subtitle="[dim white]sources[/dim white]",
            border_style=border,
            padding=(0, 0),
        )

    t.append("\n  BUSINESS MODEL\n", style="bold white")
    customers = business_model.get("customers", "—")
    revenue = business_model.get("revenue", "—")
    t.append(f"    Customers: {customers}\n", style="dim white")
    t.append(f"    Revenue: {revenue}\n\n", style="dim white")

    t.append("  OPERATING MODELS\n", style="bold white")
    if operating_models:
        for model in operating_models[:4]:
            t.append(f"    • {model}\n", style="dim white")
    else:
        t.append("    —\n", style="dim white")
    t.append("\n")

    t.append("  OPPORTUNITIES\n", style="bold white")
    for op in opportunities[:3]:
        t.append("    ▲ ", style="green")
        t.append(f"{op}\n", style="dim white")
    if not opportunities:
        t.append("    —\n", style="dim white")
    t.append("\n")

    t.append("  RISKS\n", style="bold white")
    for risk in risks[:3]:
        t.append("    ▼ ", style="red")
        t.append(f"{risk}\n", style="dim white")
    if not risks:
        t.append("    —\n", style="dim white")
    t.append("\n")

    reddit_count = sources.get("reddit", "—")
    reviews_count = sources.get("reviews", "—")
    reports_count = sources.get("reports", "—")
    listings_count = sources.get("listings", "—")
    t.append("  SOURCES\n", style="bold white")
    t.append(
        f"    Reddit[{reddit_count}] · Reviews[{reviews_count}] · Reports[{reports_count}] · Listings[{listings_count}]\n",
        style="dim white",
    )

    hint = r"  \[s] sources" if focused else ""
    subtitle = f"{sources.get('reddit', '—')} threads"
    return Panel(
        t,
        title="[dim white]market pulse[/dim white]",
        subtitle=f"[dim white]{subtitle}{hint}[/dim white]",
        border_style=border,
        padding=(0, 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Header + Footer
# ─────────────────────────────────────────────────────────────────────────────

def create_header_text(
    industry: str,
    location: str,
    count: int = 0,
    cached: bool = False,
    status: str = "ready",
    grade: str = "",
) -> Text:
    t = Text()
    t.append("  SCOUT  ", style="bold white")
    if industry:
        t.append(f"{industry} businesses", style="white")
    if location:
        t.append(f"  ·  {location}", style="dim white")
    if count:
        t.append(f"    {count:,} targets", style="dim white")
    if grade:
        t.append("  ·  ", style="dim white")
        t.append(grade, style=_grade_style(grade))
    t.append("  ·  ", style="dim white")
    t.append("cached" if cached else "live", style="yellow" if cached else "green")
    t.append(f"  ·  {status.lower()}", style="dim white")
    return t


def _fkey(t: Text, key: str, label: str, sep: str = "  ") -> None:
    """Append a key + description pair to a footer Text."""
    t.append(key, style="dim cyan")
    t.append(f" {label}{sep}", style="dim white")


def create_footer_text(
    has_selection: bool = False,
    show_help: bool = False,
    focused_pane: str = "target_list",
    show_sources: bool = False,
) -> Text:
    t = Text()
    t.append("  ")
    if show_help:
        _fkey(t, "H", "close help")
        _fkey(t, "Q", "quit", sep="")
    elif show_sources:
        _fkey(t, "Esc", "back")
        _fkey(t, "Tab", "pane")
        _fkey(t, "Q", "quit", sep="")
    elif has_selection:
        _fkey(t, "↑↓/j/k", "navigate")
        _fkey(t, "Esc/B", "back")
        _fkey(t, "W", "website")
        _fkey(t, "R", "reviews")
        _fkey(t, "E", "export")
        _fkey(t, "Tab", "pane")
        _fkey(t, "Q", "quit", sep="")
    elif focused_pane == "scout_assistant":
        _fkey(t, "Tab", "pane")
        _fkey(t, "/", "chat")
        _fkey(t, "E", "export")
        _fkey(t, "Q", "quit", sep="")
    elif focused_pane in ("market_overview", "market_pulse"):
        _fkey(t, "Tab", "pane")
        _fkey(t, "s", "sources")
        _fkey(t, "E", "export")
        _fkey(t, "H", "help")
        _fkey(t, "Q", "quit", sep="")
    else:
        _fkey(t, "↑↓/j/k", "navigate")
        _fkey(t, "Enter", "open")
        _fkey(t, "Tab", "pane")
        _fkey(t, "/", "chat")
        _fkey(t, "E", "export")
        _fkey(t, "Shift+R", "refresh")
        _fkey(t, "H", "help")
        _fkey(t, "Q", "quit", sep="")
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────

def create_main_layout() -> Layout:
    """Context row on top (overview + pulse), work row on bottom (targets + assistant)."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=1),
        Layout(name="body"),
        Layout(name="footer", size=1),
    )
    layout["body"].split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=3),
    )
    layout["top"].split_row(
        Layout(name="market_overview"),
        Layout(name="market_pulse"),
    )
    layout["bottom"].split_row(
        Layout(name="target_list"),
        Layout(name="scout_assistant"),
    )
    return layout


def create_scout_assistant_panel(
    chat_history: List[Dict],
    chat_input: str = "",
    chat_mode: bool = False,
    scope_count: int = 0,
    active_filter: str = "",
    focused: bool = False,
    chat_scroll_offset: int = 0,
) -> Panel:
    """Chat interface pane for the scout assistant."""
    from datetime import date
    t = Text()

    today = date.today().strftime("%b %-d").lower()
    t.append(f"\n  ─ ─ ─ ─  {today}  ─ ─ ─ ─\n\n", style="dim white")

    if not chat_history:
        t.append("  Ask anything about this market.\n\n", style="dim white")
        t.append("  e.g.  Which businesses have 150+ reviews?\n", style="dim white")
        t.append("         Summarize the key risks.\n", style="dim white")
        t.append("         Show businesses near Pasadena.\n", style="dim white")
    else:
        if chat_scroll_offset > 0:
            t.append(f"\n  ↑ {chat_scroll_offset} earlier message(s) — k to scroll up\n\n", style="dim white")
        visible_history = chat_history[chat_scroll_offset:]
        for entry in visible_history:
            q = entry.get("q", "")
            a = entry.get("a", "")
            t.append("  you  ", style="dim white")
            t.append(f"{q}\n", style="white")
            a_lines = a.split("\n")
            t.append("   ◆   ", style="cyan")
            t.append(f"{a_lines[0]}\n", style="dim white")
            for line in a_lines[1:]:
                if line:
                    if line.strip().startswith("["):
                        t.append(f"       {line}\n", style="cyan")
                    else:
                        t.append(f"       {line}\n", style="dim white")
            t.append("\n")

    # Input line
    if chat_mode:
        t.append("\n  > ", style="bold white")
        t.append(chat_input, style="white")
        t.append("▌\n", style="green")
    else:
        scope_str = f"{scope_count} in scope" if scope_count else "no data"
        filter_str = f"· {active_filter}" if active_filter else "· no filter"
        t.append("\n  ", style="")
        t.append("[/]", style="cyan")
        t.append(f" > _   {scope_str}  {filter_str}\n", style="dim white")

    border = "white" if chat_mode else "cyan" if focused else "dim white"
    return Panel(
        t,
        title="[dim white]scout assistant[/dim white]",
        subtitle="[dim white]claude sonnet[/dim white]",
        border_style=border,
        padding=(0, 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Legacy helpers — kept for test compatibility
# ─────────────────────────────────────────────────────────────────────────────

def create_header(
    query: str,
    industry: str = "",
    location: str = "",
    num_businesses: int = 0,
    cached: bool = False,
    status_message: str = "Ready",
) -> Panel:
    display_query = f"{industry} in {location}" if industry and location else query
    line1 = Text()
    line1.append("SCOUT", style="bold white")
    if display_query:
        line1.append(f"  {display_query}", style="dim white")
    sep = Rule(style="dim white")
    line3 = Text()
    if num_businesses:
        line3.append(f"{num_businesses} results", style="white")
    else:
        line3.append("searching...", style="dim white")
    line3.append("  ·  ", style="dim white")
    line3.append("cached" if cached else "live data", style="dim yellow" if cached else "dim green")
    line3.append(f"  ·  {status_message.lower()}", style="dim white")
    return Panel(Group(line1, sep, line3), border_style="white", padding=(0, 1))


def create_business_table(
    businesses: List[Dict],
    offset: int = 0,
    limit: int = 20,
    selected_index: int = 0,
) -> Table:
    table = Table(
        box=rich.box.SIMPLE_HEAD,
        show_header=True,
        header_style="dim white",
        show_edge=False,
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#", style="dim white", width=5, no_wrap=True)
    table.add_column("NAME", style="white", no_wrap=False, min_width=20)
    table.add_column("PHONE", style="white", width=16, no_wrap=True)
    table.add_column("RATING", style="white", width=8, no_wrap=True)
    table.add_column("ADDRESS", style="dim white", no_wrap=False)
    end_idx = min(offset + limit, len(businesses))
    for abs_idx, biz in enumerate(businesses[offset:end_idx], start=offset):
        is_selected = abs_idx == selected_index
        rating_val = biz.get("rating")
        rating_str = f"★ {rating_val}" if rating_val else "—"
        table.add_row(
            str(abs_idx + 1),
            biz.get("name", "—"),
            biz.get("phone", "—"),
            rating_str,
            biz.get("address", "—"),
            style="bold underline" if is_selected else None,
        )
    if businesses:
        start = offset + 1
        end_shown = min(offset + limit, len(businesses))
        table.caption = f"[dim white]{start}–{end_shown} of {len(businesses)}[/dim white]"
    return table


def create_footer(
    offset: int = 0,
    total: int = 0,
    limit: int = 20,
    view_mode: str = "list",
) -> Text:
    return create_footer_text(has_selection=(view_mode == "detail"))


def create_detail_panel(business: Dict) -> Panel:
    return create_business_profile_panel(business)


def create_status_bar(
    num_businesses: int,
    cached: bool = False,
    status_message: str = "Ready",
) -> Panel:
    status_text = Text()
    status_text.append("Status: ", style="dim white")
    status_text.append(status_message, style="green")
    status_text.append(f" • {num_businesses} businesses found • ", style="dim white")
    status_text.append(
        "Cached for 90 days" if cached else "Fresh data",
        style="yellow" if cached else "green",
    )
    return Panel(status_text, style="dim white on black", border_style="dim white")


def create_progress_panel(message: str, spinner: bool = True) -> Panel:
    progress_text = Text()
    if spinner:
        progress_text.append("⠋ ", style="dim white")
    progress_text.append(message, style="white")
    return Panel(
        Align.center(progress_text, vertical="middle"),
        border_style="dim white",
        padding=(1, 2),
    )


def create_help_panel() -> Panel:
    help_text = Text()
    help_text.append("keyboard shortcuts\n\n", style="dim white")
    shortcuts = [
        ("↑ / ↓",    "Navigate through businesses"),
        ("j / k",    "Navigate (vim)"),
        ("gg / G",   "Jump to top / bottom"),
        ("Enter",    "Open business profile"),
        ("Esc / B",  "Back / deselect"),
        ("PgUp/Dn",  "Scroll by page"),
        ("Ctrl+U/D", "Scroll by half page"),
        ("Home/End", "Jump to top / bottom"),
        ("W",        "Open website"),
        ("R",        "Open reviews"),
        ("E",        "Export to CSV"),
        ("Shift+R",  "Refresh data"),
        ("H",        "Show / hide help"),
        ("Q",        "Quit"),
    ]
    for key, description in shortcuts:
        help_text.append(f"  {key:<14}", style="bold white")
        help_text.append(f" {description}\n", style="dim white")
    return Panel(
        help_text,
        title="[dim white]help[/dim white]",
        title_align="left",
        border_style="white",
        padding=(1, 2),
    )


def create_footer_instructions() -> Panel:
    instructions = Text()
    instructions.append("[↑↓]", style="bold white")
    instructions.append(" Navigate  ", style="dim white")
    instructions.append("[E]", style="bold white")
    instructions.append("xport CSV  ", style="dim white")
    instructions.append("[Q]", style="bold white")
    instructions.append("uit  ", style="dim white")
    instructions.append("[H]", style="bold white")
    instructions.append("elp", style="dim white")
    return Panel(Align.center(instructions), style="dim white on black", border_style="dim white")
