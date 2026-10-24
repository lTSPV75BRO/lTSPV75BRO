#!/usr/bin/env python3
"""Generate the animated terminal header (dark + light) for the profile README.

Pure SVG with SMIL animations, so it renders inside GitHub's <img> sandbox
with no external fonts or scripts. Edit LINES and re-run:
    python3 tools/make_header.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 900, 272
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
FS = 17                 # font size
CW = FS * 0.602         # approx. monospace character width
X0, Y0, LH = 28, 92, 30  # text origin and line height

THEMES = {
    "dark":  dict(bg="#0d1117", bar="#161b22", border="#30363d", text="#c9d1d9", dim="#8b949e",
                  prompt="#3fb950", path="#58a6ff", out="#79c0ff", accent="#d2a8ff", warn="#e3b341",
                  glow="#1f6feb"),
    "light": dict(bg="#ffffff", bar="#f6f8fa", border="#d0d7de", text="#24292f", dim="#57606a",
                  prompt="#1a7f37", path="#0969da", out="#0550ae", accent="#8250df", warn="#9a6700",
                  glow="#54aeff"),
}

PROMPT = [("prompt", "prajwal@infra"), ("dim", ":"), ("path", "~"), ("dim", "$ ")]

# (segments, is_command). Commands are "typed"; outputs appear quickly.
LINES = [
    (PROMPT + [("text", "whoami")], True),
    ([("out", "Prajwal Vernekar"), ("dim", "  ·  "), ("text", "Infrastructure Consultant @ Nutanix"),
      ("dim", "  ·  "), ("text", "Pune, India")], False),
    (PROMPT + [("text", "cat stack.txt")], True),
    ([("accent", "Nutanix"), ("dim", " (AOS · AHV · NCC · NKP)  "), ("accent", "Kubernetes"), ("dim", "  "),
      ("accent", "Go"), ("dim", "  "), ("accent", "Python"), ("dim", "  "), ("accent", "Bash"), ("dim", "  "),
      ("accent", "Redfish")], False),
    (PROMPT + [("text", "echo $MOTTO")], True),
    ([("warn", "> "), ("text", "automate the boring parts of infrastructure, then make them safe")], False),
]


def render(theme: str) -> str:
    c = THEMES[theme]
    defs, body = [], []
    t = 0.4
    for i, (segs, is_cmd) in enumerate(LINES):
        y = Y0 + i * LH
        text = "".join(s for _, s in segs)
        width = len(text) * CW + 6
        if is_cmd:
            prompt_len = sum(len(s) for _, s in PROMPT) * CW
            # prompt appears instantly, the command is typed
            start_w, dur = prompt_len, max(0.35, 0.06 * (len(text) - sum(len(s) for _, s in PROMPT)))
        else:
            start_w, dur = 0, 0.35
        cid = f"l{i}"
        defs.append(
            f'<clipPath id="{cid}"><rect x="{X0 - 2}" y="{y - FS}" height="{LH}" width="0">'
            f'<set attributeName="width" to="{start_w:.0f}" begin="{t:.2f}s" fill="freeze"/>'
            f'<animate attributeName="width" from="{start_w:.0f}" to="{width:.0f}" begin="{t + 0.15:.2f}s" '
            f'dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        spans = "".join(f'<tspan fill="{c[k]}">{escape(s)}</tspan>' for k, s in segs)
        if i == len(LINES) - 1:
            # Blinking block cursor as a trailing glyph, so it always sits right
            # after the text whatever monospace font the viewer ends up using.
            cursor_at = t + 0.15 + dur
            spans += (f'<tspan fill="{c["prompt"]}" fill-opacity="0"> ▋'
                      f'<set attributeName="fill-opacity" to="1" begin="{cursor_at:.2f}s"/>'
                      f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
                      f'dur="1.1s" begin="{cursor_at:.2f}s" repeatCount="indefinite"/></tspan>')
            width += 3 * CW
        defs[-1] = defs[-1].replace(f'to="{len(text) * CW + 6:.0f}"', f'to="{width:.0f}"')
        body.append(f'<text x="{X0}" y="{y}" clip-path="url(#{cid})" xml:space="preserve">{spans}</text>')
        t += 0.15 + dur + (0.35 if is_cmd else 0.25)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Prajwal Vernekar · Infrastructure Consultant @ Nutanix">
<title>Prajwal Vernekar · Infrastructure Consultant @ Nutanix</title>
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{c["glow"]}" stop-opacity="0.18"/>
    <stop offset="1" stop-color="{c["accent"]}" stop-opacity="0.10"/>
  </linearGradient>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{c["border"]}" stroke-width="0.6" opacity="0.35"/>
  </pattern>
  {"".join(defs)}
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="url(#grid)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="url(#g)"/>
<path d="M1 13a12 12 0 0 1 12-12h{W - 26}a12 12 0 0 1 12 12v27H1z" fill="{c["bar"]}"/>
<line x1="1" y1="40" x2="{W - 1}" y2="40" stroke="{c["border"]}"/>
<circle cx="24" cy="21" r="6" fill="#ff5f57"/><circle cx="44" cy="21" r="6" fill="#febc2e"/><circle cx="64" cy="21" r="6" fill="#28c840"/>
<text x="{W / 2}" y="26" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{c["dim"]}">prajwal@infra: ~ — zsh — 120×30</text>
<g font-family="{FONT}" font-size="{FS}">
{chr(10).join(body)}
</g>
<rect x="0" y="0" width="{W}" height="3" fill="{c["glow"]}" opacity="0.0">
  <animate attributeName="y" values="40;{H};40" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;0.25;0" dur="6s" repeatCount="indefinite"/>
</rect>
</svg>
'''


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for th in THEMES:
        (out / f"header-{th}.svg").write_text(render(th), encoding="utf-8", newline="\n")
        print("wrote", out / f"header-{th}.svg")
