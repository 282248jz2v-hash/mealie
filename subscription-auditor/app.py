import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

# ── Persistence ────────────────────────────────────────────────────────────────

DATA_FILE = Path(__file__).parent / "subscriptions.json"

def load() -> list[dict]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save(subs: list[dict]):
    DATA_FILE.write_text(json.dumps(subs, indent=2, default=str))

# ── Session state bootstrap ────────────────────────────────────────────────────

if "subs" not in st.session_state:
    st.session_state.subs = load()
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "delete_id" not in st.session_state:
    st.session_state.delete_id = None
if "show_form" not in st.session_state:
    st.session_state.show_form = False

# ── Helpers ────────────────────────────────────────────────────────────────────

CATEGORIES = ["AI Tools", "Gaming", "Streaming", "Software", "Other"]
CYCLES     = ["weekly", "monthly", "yearly"]
CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "CNY"]

CAT_EMOJI = {
    "AI Tools":  "🤖",
    "Gaming":    "🎮",
    "Streaming": "📺",
    "Software":  "💻",
    "Other":     "🏷️",
}

CURRENCY_SYMBOLS = {
    "USD": "$", "EUR": "€", "GBP": "£", "CAD": "CA$",
    "AUD": "A$", "JPY": "¥", "CHF": "CHF", "CNY": "¥",
}

def fmt(amount: float, currency: str = "USD") -> str:
    sym = CURRENCY_SYMBOLS.get(currency, currency + " ")
    return f"{sym}{amount:,.2f}"

def to_monthly(sub: dict) -> float:
    if not sub.get("active", True):
        return 0.0
    c = sub["cost"]
    cycle = sub["billing_cycle"]
    if cycle == "monthly": return c
    if cycle == "yearly":  return c / 12
    if cycle == "weekly":  return c * 4.33
    return c

def to_yearly(sub: dict) -> float:
    if not sub.get("active", True):
        return 0.0
    c = sub["cost"]
    cycle = sub["billing_cycle"]
    if cycle == "monthly": return c * 12
    if cycle == "yearly":  return c
    if cycle == "weekly":  return c * 52
    return c

def days_until(sub: dict) -> int:
    renewal = datetime.strptime(sub["next_renewal"], "%Y-%m-%d").date()
    return (renewal - date.today()).days

def renewal_label(sub: dict) -> str:
    d = days_until(sub)
    if d < 0:  return f"⚠️ overdue by {abs(d)}d"
    if d == 0: return "🔴 today"
    if d == 1: return "🟠 tomorrow"
    if d <= 7: return f"🟡 in {d} days"
    return f"in {d} days"

def upsert(form: dict):
    subs = st.session_state.subs
    if form["id"]:
        st.session_state.subs = [
            {**s, **{k: v for k, v in form.items() if k != "id"}} if s["id"] == form["id"] else s
            for s in subs
        ]
    else:
        new = {k: v for k, v in form.items() if k != "id"}
        new["id"] = str(uuid.uuid4())
        new["created_at"] = date.today().isoformat()
        st.session_state.subs.append(new)
    save(st.session_state.subs)

def delete(sub_id: str):
    st.session_state.subs = [s for s in st.session_state.subs if s["id"] != sub_id]
    save(st.session_state.subs)

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Subscription Auditor",
    page_icon="🔔",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  /* tighten top padding */
  .block-container { padding-top: 1.5rem; }
  /* stat card style */
  .stat-card {
    background: var(--secondary-background-color);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
  }
  .stat-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: .05em; opacity: .65; }
  .stat-value { font-size: 1.45rem; font-weight: 700; margin-top: 2px; }
  /* sub card */
  .sub-card {
    border-radius: 12px;
    border: 1px solid var(--secondary-background-color);
    padding: 14px 16px 10px;
    margin-bottom: 10px;
    background: var(--secondary-background-color);
  }
  .sub-name  { font-size: 1.05rem; font-weight: 700; }
  .sub-meta  { font-size: 0.8rem; opacity: .7; }
  .sub-cost  { font-size: 1.15rem; font-weight: 700; }
  /* alert */
  .renewal-alert {
    background: #fff3cd; color: #856404;
    border-left: 4px solid #ffc107;
    border-radius: 8px; padding: 10px 14px;
    margin-bottom: 8px; font-size: 0.9rem;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.markdown("## 🔔 Subscription Auditor")
    st.caption("Track recurring costs · get alerted before renewals hit")
with col_btn:
    st.write("")  # vertical alignment nudge
    if st.button("➕ Add", use_container_width=True, type="primary"):
        st.session_state.show_form = True
        st.session_state.edit_id   = None

# ── Add / Edit form ────────────────────────────────────────────────────────────

editing = next((s for s in st.session_state.subs if s["id"] == st.session_state.edit_id), None)

if st.session_state.show_form or editing:
    title = "✏️ Edit Subscription" if editing else "➕ Add Subscription"
    with st.expander(title, expanded=True):
        with st.form("sub_form", clear_on_submit=True):
            name = st.text_input(
                "Service name *",
                value=editing["name"] if editing else "",
                placeholder="e.g. ChatGPT Plus, Netflix, Xbox Game Pass",
            )
            c1, c2 = st.columns(2)
            category = c1.selectbox(
                "Category",
                CATEGORIES,
                index=CATEGORIES.index(editing["category"]) if editing else 0,
            )
            billing_cycle = c2.selectbox(
                "Billing cycle",
                CYCLES,
                index=CYCLES.index(editing["billing_cycle"]) if editing else 1,
            )

            c3, c4 = st.columns([2, 1])
            cost = c3.number_input(
                "Cost *",
                min_value=0.0, step=0.01, format="%.2f",
                value=float(editing["cost"]) if editing else 0.0,
            )
            currency = c4.selectbox(
                "Currency",
                CURRENCIES,
                index=CURRENCIES.index(editing["currency"]) if editing else 0,
            )

            default_renewal = (
                datetime.strptime(editing["next_renewal"], "%Y-%m-%d").date()
                if editing else date.today() + timedelta(days=30)
            )
            next_renewal = st.date_input("Next renewal date *", value=default_renewal)

            notes  = st.text_area("Notes (optional)", value=editing.get("notes", "") if editing else "", height=80)
            active = st.toggle("Active subscription", value=editing.get("active", True) if editing else True)

            submitted = st.form_submit_button(
                "💾 Save Changes" if editing else "✅ Add Subscription",
                use_container_width=True,
                type="primary",
            )

            if submitted:
                if not name.strip():
                    st.error("Service name is required.")
                else:
                    upsert({
                        "id":           editing["id"] if editing else None,
                        "name":         name.strip(),
                        "category":     category,
                        "cost":         cost,
                        "currency":     currency,
                        "billing_cycle": billing_cycle,
                        "next_renewal": next_renewal.isoformat(),
                        "notes":        notes.strip(),
                        "active":       active,
                    })
                    st.session_state.show_form = False
                    st.session_state.edit_id   = None
                    st.rerun()

        if st.button("Cancel", use_container_width=True):
            st.session_state.show_form = False
            st.session_state.edit_id   = None
            st.rerun()

st.divider()

subs = st.session_state.subs

# ── Upcoming renewal alerts ────────────────────────────────────────────────────

upcoming = sorted(
    [s for s in subs if s.get("active", True) and 0 <= days_until(s) <= 7],
    key=days_until,
)
for s in upcoming:
    d = days_until(s)
    when = "today" if d == 0 else ("tomorrow" if d == 1 else f"in {d} days")
    st.markdown(
        f'<div class="renewal-alert">⚠️ <b>{s["name"]}</b> renews <b>{when}</b> '
        f'— {fmt(s["cost"], s["currency"])} / {s["billing_cycle"]}</div>',
        unsafe_allow_html=True,
    )

# ── Stats ──────────────────────────────────────────────────────────────────────

monthly = sum(to_monthly(s) for s in subs)
yearly  = sum(to_yearly(s)  for s in subs)
active_count = sum(1 for s in subs if s.get("active", True))

c1, c2, c3, c4 = st.columns(4)
for col, label, value in [
    (c1, "Monthly",      fmt(monthly)),
    (c2, "Yearly",       fmt(yearly)),
    (c3, "Renewing soon", str(len(upcoming))),
    (c4, "Active subs",  str(active_count)),
]:
    col.markdown(
        f'<div class="stat-card"><div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ── Filter / sort bar ─────────────────────────────────────────────────────────

fc, sc = st.columns([3, 2])
with fc:
    cat_filter = st.selectbox(
        "Filter by category",
        ["All"] + CATEGORIES,
        label_visibility="collapsed",
    )
with sc:
    sort_by = st.selectbox(
        "Sort by",
        ["Renewal date", "Cost (high→low)", "Name"],
        label_visibility="collapsed",
    )

# ── Subscription list ──────────────────────────────────────────────────────────

filtered = [s for s in subs if cat_filter == "All" or s["category"] == cat_filter]

if sort_by == "Renewal date":
    filtered.sort(key=lambda s: s["next_renewal"])
elif sort_by == "Cost (high→low)":
    filtered.sort(key=lambda s: to_monthly(s), reverse=True)
else:
    filtered.sort(key=lambda s: s["name"].lower())

if not subs:
    st.info("No subscriptions yet — hit **➕ Add** to track your first one.")
elif not filtered:
    st.info("No subscriptions match this filter.")
else:
    for s in filtered:
        emoji  = CAT_EMOJI.get(s["category"], "🏷️")
        status = "🟢 Active" if s.get("active", True) else "⏸️ Paused"
        mo_str = f"  ·  {fmt(to_monthly(s), s['currency'])}/mo" if s["billing_cycle"] != "monthly" else ""
        d      = days_until(s)
        urg    = "🔴" if d < 0 else ("🔴" if d <= 3 else ("🟡" if d <= 7 else ""))

        with st.container():
            st.markdown(
                f'<div class="sub-card">'
                f'<span class="sub-name">{emoji} {s["name"]}</span>&nbsp;&nbsp;'
                f'<span class="sub-meta">{s["category"]} · {status}</span><br>'
                f'<span class="sub-cost">{fmt(s["cost"], s["currency"])}</span>'
                f'<span class="sub-meta"> / {s["billing_cycle"]}{mo_str}</span><br>'
                f'<span class="sub-meta">{urg} Renews {renewal_label(s)} '
                f'({datetime.strptime(s["next_renewal"], "%Y-%m-%d").strftime("%b %d, %Y")})</span>'
                + (f'<br><span class="sub-meta" style="opacity:.55">{s["notes"]}</span>' if s.get("notes") else "")
                + "</div>",
                unsafe_allow_html=True,
            )
            ec, dc, _ = st.columns([1, 1, 4])
            if ec.button("✏️ Edit", key=f"edit_{s['id']}", use_container_width=True):
                st.session_state.edit_id   = s["id"]
                st.session_state.show_form = False
                st.rerun()
            if dc.button("🗑️ Delete", key=f"del_{s['id']}", use_container_width=True):
                st.session_state.delete_id = s["id"]
                st.rerun()

# ── Delete confirmation ────────────────────────────────────────────────────────

if st.session_state.delete_id:
    target = next((s for s in subs if s["id"] == st.session_state.delete_id), None)
    if target:
        st.warning(f"Delete **{target['name']}**? This cannot be undone.")
        y, n, _ = st.columns([1, 1, 4])
        if y.button("Yes, delete", type="primary", use_container_width=True):
            delete(st.session_state.delete_id)
            st.session_state.delete_id = None
            st.rerun()
        if n.button("Cancel", use_container_width=True):
            st.session_state.delete_id = None
            st.rerun()
