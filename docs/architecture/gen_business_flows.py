"""Generate one UML sequence diagram per business flow (draw.io, one page per flow).

Run:  python3 docs/architecture/gen_business_flows.py
Out:  docs/architecture/business_flows.drawio   (pages B1–B6; export PNGs: see plan.md §7A)

Same style as the thesis sequences S1–S7 (docs/diagrams/gen_drawio.py, sequence()):
- one lifeline per participant (user, Nuxt, FastAPI, Redis, MySQL …), left → right in call order;
- steps numbered 1 → n top to bottom; solid arrow = call, dashed open arrow = reply, loop = internal step;
- `opt [condition]` frames mark the branch that only happens under that condition (errors, cache miss …).
Each page names the FR/NFR it implements (plan.md §2A). Edit the FLOWS data and rerun.
"""
from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_aws_diagram import FONT, TEXT, Diagram, mxfile  # noqa: E402

OUT_FILE = Path(__file__).resolve().parent / "business_flows.drawio"

PX = 23          # message text, participant title, frame label (same as thesis S1–S7)
TECH_PX = 20     # technical name under the participant title
COL = 200        # distance between two lifelines
BOX = 180        # participant box width
HEAD = 110       # participant box height
GAP = 72         # vertical distance between two steps
FRAME_PAD = 30   # extra space around an opt frame

LIFELINE = (
    "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;"
    f"collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;size={HEAD};"
    f"fillColor=#FFFFFF;strokeColor=#545B64;fontColor={TEXT};fontSize={PX};spacing=4;" + FONT
)
CALL = (f"html=1;verticalAlign=bottom;endArrow=block;endFill=1;strokeColor=#232F3E;strokeWidth=1.5;"
        f"fontSize={PX};fontColor={TEXT};labelBackgroundColor=#FFFFFF;" + FONT)
REPLY = CALL.replace("endArrow=block;endFill=1;", "endArrow=open;endFill=0;") + "dashed=1;"
SELF = CALL + "edgeStyle=orthogonalEdgeStyle;align=left;labelPosition=right;spacingLeft=48;entryX=0;"
FRAME = (f"shape=umlFrame;whiteSpace=wrap;html=1;width={{w}};height=32;fontSize={PX - 2};fontStyle=1;"
         f"strokeColor=#879196;fontColor={TEXT};" + FONT)


def title(name: str, tech: str) -> str:
    return f'<b>{escape(name)}</b><br><font style="font-size:{TECH_PX}px;color:#545B64">{escape(tech)}</font>'


class Sequence(Diagram):
    def message(self, cid: str, x1: float, x2: float, y: float, text: str, style: str,
                loop: bool = False) -> None:
        target_y = y + 18 if loop else y
        points = (f'<Array as="points"><mxPoint x="{x1 + 40}" y="{y}"/><mxPoint x="{x1 + 40}" y="{target_y}"/></Array>'
                  if loop else "")
        geo = ('<mxGeometry relative="1" as="geometry">'
               f'<mxPoint x="{x1}" y="{y}" as="sourcePoint"/><mxPoint x="{x2}" y="{target_y}" as="targetPoint"/>'
               f"{points}</mxGeometry>")
        cell = f'<mxCell style={quoteattr(style)} edge="1" parent="1">{geo}</mxCell>'
        self.cells.append(f'<object id="{cid}" label={quoteattr(text)}>{cell}</object>')


def sequence(page: str, participants: list[tuple[str, str, str]], steps: list[tuple[str, str, str, str]],
             frames: tuple[tuple[str, int, int, str, str], ...] = ()) -> Sequence:
    """participants: (id, title, tech). steps: (kind, from, to, text), kind = call | reply | self.
    frames: (label, first step, last step, leftmost participant, rightmost participant)."""
    left, top = 20, 20
    starts = {f[1] for f in frames}
    after = {f[2] + 1 for f in frames}
    ys, y = [], top + HEAD + 58
    for n in range(1, len(steps) + 1):
        if n > 1:
            y += GAP + (FRAME_PAD if n in starts or n in after else 0)
        ys.append(y)
    height = ys[-1] + 40
    width = left * 2 + COL * (len(participants) - 1) + BOX + 120   # room for the last loop label
    d = Sequence(page, width, height + 20)

    xs: dict[str, float] = {}
    for i, (pid, name, tech) in enumerate(participants):
        x = left + i * COL
        xs[pid] = x + BOX / 2
        d.vertex(f"ll-{pid}", title(name, tech), LIFELINE, x, top, BOX, height - top)

    for n, (kind, src, dst, text) in enumerate(steps, 1):
        label = f"{n}. {escape(text)}"
        if kind == "self":
            d.message(f"m{n}", xs[src], xs[src] + 1, ys[n - 1], label, SELF, loop=True)
        else:
            d.message(f"m{n}", xs[src], xs[dst], ys[n - 1], label, REPLY if kind == "reply" else CALL)

    for i, (name, first, last, lp, rp) in enumerate(frames):
        fy = ys[first - 1] - 70
        fh = ys[last - 1] - ys[first - 1] + 90
        fx = max(4, min(xs[lp], xs[rp]) - BOX / 2 - 6)
        fr = min(width - 4, max(xs[lp], xs[rp]) + BOX / 2 + 6)
        d.vertex(f"frame{i}", escape(name), FRAME.format(w=min(int(fr - fx) - 20, 13 * len(name) + 36)),
                 fx, fy, fr - fx, fh)
    return d


# ── Participants ──
INVESTOR = ("user", "Investor", "browser")
VISITOR = ("user", "Visitor", "browser")
AGENT_UI = ("agent", "Agent", "Nuxt dashboard")
WEB = ("web", "Web frontend", "Nuxt 3")
CDN = ("cdn", "CDN", "CloudFront")
API = ("api", "REST API", "FastAPI")
REDIS = ("redis", "Cache", "Redis")
DB = ("db", "Database", "MySQL")


def flows() -> list[Sequence]:
    b1 = sequence(
        "B1 Search listings (FR-02, FR-04, FR-10)",
        [INVESTOR, WEB, API, REDIS, DB],
        [
            ("call", "user", "web", "set filters"),
            ("call", "web", "api", "GET /properties?…"),
            ("self", "api", "api", "validate params"),
            ("reply", "api", "web", "422 VALIDATION_ERROR"),
            ("call", "api", "redis", "GET search key"),
            ("reply", "redis", "api", "page | nil"),
            ("call", "api", "db", "SELECT … LIMIT"),
            ("reply", "db", "api", "rows + total"),
            ("call", "api", "redis", "SET key, 60 s"),
            ("reply", "api", "web", "200 Page[T]"),
            ("reply", "web", "user", "result grid"),
        ],
        frames=(("opt [invalid params]", 4, 4, "web", "api"),
                ("opt [cache miss]", 7, 9, "api", "db")),
    )
    b2 = sequence(
        "B2 View listing with SSR and SEO (FR-03, FR-12)",
        [VISITOR, CDN, WEB, API, REDIS, DB],
        [
            ("call", "user", "cdn", "GET /properties/{slug}"),
            ("call", "cdn", "web", "forward on miss"),
            ("call", "web", "api", "GET /properties/{slug}"),
            ("call", "api", "redis", "GET detail key"),
            ("call", "api", "db", "SELECT listing"),
            ("call", "api", "redis", "SET key, 300 s"),
            ("reply", "api", "web", "200 listing | 404"),
            ("self", "web", "web", "render + SEO meta"),
            ("reply", "web", "cdn", "HTML"),
            ("reply", "cdn", "user", "HTML"),
            ("self", "user", "user", "hydrate page"),
        ],
        frames=(("opt [cache miss]", 5, 6, "api", "db"),),
    )
    b3 = sequence(
        "B3 Login and session (FR-05, NFR-05)",
        [("user", "User", "browser"), WEB, API, REDIS, DB],
        [
            ("call", "user", "web", "email + password"),
            ("call", "web", "api", "POST /auth/login"),
            ("call", "api", "redis", "INCR login:{ip}"),
            ("reply", "api", "web", "429 RATE_LIMITED"),
            ("call", "api", "db", "find user by email"),
            ("reply", "db", "api", "user + hash"),
            ("self", "api", "api", "bcrypt verify"),
            ("self", "api", "api", "sign JWT pair"),
            ("reply", "api", "web", "200 access + cookie"),
            ("call", "web", "api", "POST /auth/refresh"),
            ("call", "api", "redis", "revoke old jti"),
            ("reply", "api", "web", "200 new pair | 401"),
        ],
        frames=(("opt [> 5 per min]", 4, 4, "web", "api"),
                ("opt [password OK]", 8, 9, "web", "redis"),
                ("opt [access expired]", 10, 12, "web", "redis")),
    )
    b4 = sequence(
        "B4 Favourites (FR-06)",
        [INVESTOR, WEB, API, REDIS, DB],
        [
            ("call", "user", "web", "click heart"),
            ("self", "web", "web", "toggle icon now"),
            ("call", "web", "api", "POST /favorites/{id}"),
            ("call", "api", "redis", "jti revoked?"),
            ("call", "api", "db", "INSERT IGNORE"),
            ("reply", "api", "web", "200 (idempotent)"),
            ("self", "web", "web", "revert + toast"),
            ("call", "user", "web", "open /favorites"),
            ("call", "web", "api", "GET /favorites"),
            ("reply", "api", "web", "200 list"),
        ],
        frames=(("opt [request failed]", 7, 7, "user", "api"),),
    )
    b5 = sequence(
        "B5 Send inquiry to agent (FR-07, FR-09)",
        [INVESTOR, WEB, API, REDIS, DB, ("agent", "Agent", "dashboard")],
        [
            ("call", "user", "web", "fill inquiry form"),
            ("call", "web", "api", "POST …/inquiries"),
            ("call", "api", "redis", "INCR inquiry:{user}"),
            ("reply", "api", "web", "429 Retry-After"),
            ("call", "api", "db", "listing published?"),
            ("call", "api", "db", "INSERT (NEW)"),
            ("reply", "api", "web", "201 Created"),
            ("reply", "web", "user", "confirmation"),
            ("call", "agent", "api", "GET my inquiries"),
            ("reply", "api", "agent", "list (NEW)"),
            ("call", "agent", "api", "PATCH → CONTACTED"),
        ],
        frames=(("opt [> 10 per hour]", 4, 4, "web", "api"),),
    )
    b6 = sequence(
        "B6 Listing lifecycle (FR-08, NFR-06)",
        [AGENT_UI, API, DB, REDIS],
        [
            ("call", "agent", "api", "POST /properties"),
            ("self", "api", "api", "owner = current agent"),
            ("call", "api", "db", "INSERT (DRAFT)"),
            ("reply", "api", "agent", "201 DRAFT"),
            ("call", "agent", "api", "POST /{id}/publish"),
            ("self", "api", "api", "check rules"),
            ("reply", "api", "agent", "409 CONFLICT"),
            ("call", "api", "db", "UPDATE PUBLISHED"),
            ("call", "api", "redis", "DEL key, INCR version"),
            ("reply", "api", "agent", "200 PUBLISHED"),
        ],
        frames=(("opt [not allowed]", 7, 7, "agent", "api"),),
    )
    return [b1, b2, b3, b4, b5, b6]


# PNG file name per page, in page order (descriptive, like aws_architecture.png).
PNG_NAMES = [
    "flow_b1_search_listings.png",
    "flow_b2_view_listing_ssr_seo.png",
    "flow_b3_login_session.png",
    "flow_b4_favourites.png",
    "flow_b5_send_inquiry.png",
    "flow_b6_listing_lifecycle.png",
]


def export_png() -> None:
    """Export every page with draw.io desktop (brew install --cask drawio)."""
    import subprocess

    for index, name in enumerate(PNG_NAMES, 1):
        subprocess.run(["drawio", "--export", "--format", "png", "--scale", "2", "--border", "16",
                        "--page-index", str(index), "-o", str(OUT_FILE.parent / name), str(OUT_FILE)],
                       check=True, capture_output=True)
        print("exported", name)


if __name__ == "__main__":
    pages = flows()
    assert len(pages) == len(PNG_NAMES), "add a PNG name for every flow"
    OUT_FILE.write_text(mxfile(pages, host="gen_business_flows.py"), encoding="utf-8")
    print("wrote", OUT_FILE, f"({len(pages)} pages)")
    if "--png" in sys.argv:
        export_png()
