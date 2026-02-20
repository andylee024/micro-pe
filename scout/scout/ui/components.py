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

def _kv(t: Text, label: str, value: str, note: str = "") -> None:
    t.append(f"    {label:<18}", style="dim white")
    t.append(f"{value}", style="white")
    if note:
        t.append(f"  ({note})", style="dim white")
    t.append("\n")


def _stars(rating: float) -> str:
    full = int(round(float(rating)))
    empty = 5 - full
    return "★" * full + "☆" * empty


# ─────────────────────────────────────────────────────────────────────────────
# Pane 1 — Market Overview (top-left)
# ─────────────────────────────────────────────────────────────────────────────

def create_market_overview_panel(market_data: Dict) -> Panel:
    """Market size, financial benchmarks, quality metrics, trends, outlook."""
    t = Text()

    if not market_data:
        t.append("\n  No market data loaded.\n", style="dim white")
        t.append("  Run a search to populate this pane.\n", style="dim white")
        return Panel(
            t,
            title="[dim white]market overview[/dim white]",
            border_style="white",
            padding=(0, 0),
        )

    fin = market_data.get("financial", {})
    quality = market_data.get("quality", {})
    trends = market_data.get("trends", {})
    outlook = market_data.get("outlook", {})
    fdd_count = fin.get("fdd_count", 0)
    grade = outlook.get("grade", "—")

    total = market_data.get("total_businesses", 0)
    density = market_data.get("market_density", "—")
    est_value = market_data.get("est_market_value", "")

    t.append(f"\n  {total:,} businesses", style="bold white")
    t.append(f"  ·  {density}", style="dim white")
    if est_value:
        t.append(f"  ·  {est_value} total\n\n", style="dim white")
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
    _kv(t, "Avg rating", f"{_stars(rating)}  {rating}")
    _kv(t, "Sentiment", f"{pos_pct}% positive")
    _kv(t, "Review vol.", quality.get("review_volume", "—"))
    t.append("\n")

    # Trends
    t.append("  TRENDS  ", style="bold white")
    t.append("30 days\n", style="dim white")
    _kv(t, "Job postings", trends.get("job_postings", "—"))
    _kv(t, "New entrants", trends.get("new_entrants", "—"))
    _kv(t, "Search vol.", trends.get("search_volume", "—"))
    t.append("\n")

    # Outlook
    note = outlook.get("note", "")
    t.append("  OUTLOOK  ", style="bold white")
    t.append(f"Grade {grade}", style="bold white")
    if note:
        t.append(f"  ·  {note}\n", style="dim white")
    else:
        t.append("\n")

    return Panel(
        t,
        title="[dim white]market overview[/dim white]",
        subtitle=f"[dim white]{grade} market · {fdd_count} fdds[/dim white]",
        border_style="white",
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
) -> Panel:
    """Ranked, scrollable business list with cursor highlight."""
    t = Text()

    if not businesses:
        t.append("\n  No results yet — searching...\n", style="dim white")
        return Panel(
            t,
            title="[dim white]target list[/dim white]",
            border_style="white",
            padding=(0, 0),
        )

    t.append("  sorted by acquisition score\n\n", style="dim white")

    end_idx = min(offset + limit, len(businesses))

    for abs_idx, biz in enumerate(businesses[offset:end_idx], start=offset):
        is_selected = abs_idx == selected_index
        rank = abs_idx + 1
        name = biz.get("name", "—")
        score = biz.get("score")
        revenue = biz.get("revenue") or biz.get("est_revenue") or ""
        rating = biz.get("rating")
        phone = biz.get("phone") or ""
        signals = biz.get("signals") or []

        # Line 1: cursor, rank, name, score, revenue, rating
        if is_selected:
            t.append(f"  ▶ {rank:<3}", style="bold white")
            t.append(f"{name:<24}", style="bold white underline")
        else:
            t.append(f"    {rank:<3}", style="dim white")
            t.append(f"{name:<24}", style="white")

        if score is not None:
            t.append(f"  {score:>3}", style="bold white" if is_selected else "white")
        if revenue:
            t.append(f"  {revenue:<7}", style="white" if is_selected else "dim white")
        if rating is not None:
            t.append(f"  {rating}★", style="white" if is_selected else "dim white")
        t.append("\n")

        # Line 2: phone + first two signals
        phone_part = phone if phone else "—"
        signal_part = "  ·  " + "  |  ".join(signals[:2]) if signals else ""
        t.append(f"      {phone_part}{signal_part}\n", style="dim white")

    subtitle = f"{offset + 1}–{end_idx} of {len(businesses)}"
    return Panel(
        t,
        title="[dim white]target list[/dim white]",
        subtitle=f"[dim white]{subtitle}[/dim white]",
        border_style="white",
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
    t.append(f"    {address}\n\n", style="dim white")

    # Financials
    rev = business.get("revenue") or business.get("est_revenue") or ""
    rev_vs = business.get("revenue_vs_median") or ""
    ebitda = business.get("ebitda") or ""
    ebitda_vs = business.get("ebitda_vs_median") or ""
    valuation = business.get("valuation") or ""

    if rev or ebitda or valuation:
        t.append("  FINANCIALS\n", style="bold white")
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
    subtitle_str = f"score {score}" if score is not None else ""

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

def create_market_pulse_panel(pulse_data: Dict) -> Panel:
    """Reddit sentiment, market trends, operator insights, flags."""
    t = Text()

    if not pulse_data:
        t.append("\n  No market pulse data loaded.\n", style="dim white")
        return Panel(
            t,
            title="[dim white]market pulse[/dim white]",
            border_style="white",
            padding=(0, 0),
        )

    reddit = pulse_data.get("reddit", {})
    trends = pulse_data.get("trends", {})
    insights = pulse_data.get("insights", [])
    green_flags = pulse_data.get("green_flags", [])
    red_flags = pulse_data.get("red_flags", [])

    threads = reddit.get("thread_count", 0)
    overall = reddit.get("overall", "Mixed")
    emoji = reddit.get("overall_emoji", "😐")
    pos_pct = reddit.get("positive_pct", 0)

    t.append("\n  REDDIT  ", style="bold white")
    t.append(f"{threads} threads  ·  {overall} {emoji}\n", style="dim white")

    bar_len = int(pos_pct / 10)
    bar = "█" * bar_len + "░" * (10 - bar_len)
    t.append(f"    {pos_pct}% positive  ", style="white")
    t.append(f"{bar}\n", style="dim white")

    top_thread = reddit.get("top_thread", {})
    if top_thread:
        title_txt = top_thread.get("title", "")[:36]
        sub = top_thread.get("subreddit", "")
        ups = top_thread.get("upvotes", 0)
        cmts = top_thread.get("comments", 0)
        t.append(f"    \"{title_txt}\"\n", style="dim white")
        t.append(f"    r/{sub}  ·  {ups}↑  ·  {cmts}💬\n", style="dim white")
    t.append("\n")

    for p in reddit.get("key_points_pos", [])[:2]:
        t.append(f"  ✓ {p}\n", style="dim white")
    for p in reddit.get("key_points_neg", [])[:2]:
        t.append(f"  ⚠ {p}\n", style="dim white")
    t.append("\n")

    if insights:
        t.append("  OPERATOR INSIGHTS\n", style="bold white")
        for insight in insights[:2]:
            wrapped = insight if len(insight) <= 42 else insight[:42] + "…"
            t.append(f"    {wrapped}\n", style="dim white")
        t.append("\n")

    jobs = trends.get("job_postings", "—")
    entrants = trends.get("new_entrants", "—")
    t.append("  TRENDS  ", style="bold white")
    t.append(f"Jobs {jobs}  ·  New entrants {entrants}\n\n", style="dim white")

    t.append("  GREEN FLAGS           ", style="bold white")
    t.append("RED FLAGS\n", style="bold white")
    count = max(len(green_flags), len(red_flags))
    for i in range(min(count, 3)):
        gf = green_flags[i] if i < len(green_flags) else ""
        rf = red_flags[i] if i < len(red_flags) else ""
        t.append(f"  ✓ {gf:<20}", style="dim white")
        t.append(f"✗ {rf}\n", style="dim white")

    subtitle = f"{threads} threads · 30d"
    return Panel(
        t,
        title="[dim white]market pulse[/dim white]",
        subtitle=f"[dim white]{subtitle}[/dim white]",
        border_style="white",
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
) -> Text:
    t = Text()
    t.append("  SCOUT  ", style="bold white")
    t.append(industry, style="white")
    if location:
        t.append(f"  ·  {location}", style="dim white")
    if count:
        t.append(f"    {count:,} results", style="dim white")
        t.append("  ·  ", style="dim white")
        t.append("cached" if cached else "live", style="dim yellow" if cached else "dim green")
    t.append(f"  ·  {status.lower()}", style="dim white")
    return t


def create_footer_text(has_selection: bool = False, show_help: bool = False) -> Text:
    t = Text()
    t.append("  ")
    if show_help:
        t.append("H", style="dim white")
        t.append(" close help  ", style="dim white")
        t.append("Q", style="dim white")
        t.append(" quit", style="dim white")
    elif has_selection:
        t.append("↑↓/j/k", style="dim white")
        t.append(" navigate  ", style="dim white")
        t.append("B", style="dim white")
        t.append("/", style="dim white")
        t.append("Esc", style="dim white")
        t.append(" back  ", style="dim white")
        t.append("E", style="dim white")
        t.append(" export  ", style="dim white")
        t.append("Q", style="dim white")
        t.append(" quit", style="dim white")
    else:
        t.append("↑↓/j/k", style="dim white")
        t.append(" navigate  ", style="dim white")
        t.append("Enter", style="dim white")
        t.append(" open  ", style="dim white")
        t.append("gg/G", style="dim white")
        t.append(" top/bottom  ", style="dim white")
        t.append("E", style="dim white")
        t.append(" export  ", style="dim white")
        t.append("R", style="dim white")
        t.append(" refresh  ", style="dim white")
        t.append("H", style="dim white")
        t.append(" help  ", style="dim white")
        t.append("Q", style="dim white")
        t.append(" quit", style="dim white")
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────

def create_main_layout() -> Layout:
    """4-pane Bloomberg layout with thin header + footer."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=1),
        Layout(name="body"),
        Layout(name="footer", size=1),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=3),
    )
    layout["left"].split_column(
        Layout(name="market_overview"),
        Layout(name="business_profile"),
    )
    layout["right"].split_column(
        Layout(name="target_list", ratio=3),
        Layout(name="market_pulse", ratio=2),
    )
    return layout


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
        ("E",        "Export to CSV"),
        ("R",        "Refresh data"),
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
