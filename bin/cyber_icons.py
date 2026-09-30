"""Theme-aware Stream Deck artwork; no device actions live here."""
import colorsys
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib

SHAPES = {
 'terminal': '<path d="M31 43l15 14-15 14M53 73h25"/><path d="M26 31h68v57H26z" stroke-width="2"/>',
 'browser': '<circle cx="60" cy="59" r="30"/><ellipse cx="60" cy="59" rx="13" ry="30"/><path d="M30 59h60M35 43h50M35 75h50" stroke-width="2"/>',
 'files': '<path d="M25 40h26l8 9h36l-8 36H25z"/><path d="M25 40v-8h30l8 9h25v8M27 58h62" stroke-width="2"/>',
 'herdr': '<path d="M32 31v51M32 46h23l17-15M32 65h23l17 18"/><rect x="23" y="22" width="18" height="18"/><rect x="71" y="22" width="18" height="18"/><rect x="71" y="74" width="18" height="18"/>',
 'media_play_pause': '<path d="M34 33l32 27-32 27z"/><path d="M78 36v48M89 36v48" stroke-width="7"/>',
 'screenshot': '<path d="M24 43V25h20M77 25h19v18M96 77v18H77M44 95H24V77"/><rect x="36" y="39" width="48" height="40" rx="4" stroke-width="2"/><circle cx="60" cy="59" r="12"/><path d="M53 23h14M60 16v14M53 96h14M60 90v13" stroke-width="2"/>',
 'screensaver': '<path d="M24 29h72v51H24zM60 81v11M43 93h34"/><path d="M64 37a17 17 0 1 0 15 27 21 21 0 0 1-15-27z" fill="{secondary}" stroke-width="2"/><path d="M40 39v8M36 43h8M82 47v6M79 50h6" stroke-width="2"/>',
 'lock': '<path d="M40 52V41a20 20 0 0 1 40 0v11"/><path d="M32 52h56v38H32z"/><circle cx="60" cy="68" r="5" fill="{secondary}"/><path d="M60 73v9"/>',
 'cliamp': '<path d="M50 80V34l38-9v46"/><circle cx="40" cy="80" r="10"/><circle cx="78" cy="71" r="10"/><path d="M50 46l38-9" stroke-width="2"/>',
 'orca': '<path d="M22 62c14-16 34-24 52-22 10 1 18 5 24 12-6 10-16 17-28 20-16 4-34 0-48-10z"/><path d="M74 40c2-8 8-14 16-16-2 8-2 15 2 21M40 72c-2 8-8 13-16 15 3-7 4-14 2-20" stroke-width="2"/><circle cx="42" cy="52" r="3" fill="{secondary}"/><path d="M52 78c10 6 24 6 34 0" stroke="{secondary}" stroke-width="2"/>',
 'govee_lamp': '<path d="M46 74c-12-9-15-24-8-36 5-9 13-13 22-13s17 4 22 13c7 12 4 27-8 36v8H46z"/><path d="M47 88h26M50 95h20M55 102h10"/><path d="M54 74V58M66 74V58M54 58c0-8 12-8 12 0" stroke="{secondary}" stroke-width="2"/><path d="M60 8v7M27 20l5 5M93 20l-5 5M16 45h7M97 45h7" stroke="{secondary}" stroke-width="2"/>',
}
DEFAULTS = {'background':'#08111f','cyan':'#38d9ef','magenta':'#ef61cb','yellow':'#f9d46c','foreground':'#e3f4ff'}

def palette():
    path = Path(os.environ.get('XDG_STATE_HOME', Path.home()/'.local/state'))/'omarchy/current/theme/colors.toml'
    try: raw = tomllib.loads(path.read_text())
    except (OSError, ValueError): raw = {}
    return {key: raw.get('bright_'+key, raw.get(key, value)) if re.fullmatch(r'#[0-9a-fA-F]{6}', str(raw.get('bright_'+key, raw.get(key, value)))) else value for key,value in DEFAULTS.items()}

def theme_signature():
    return json.dumps(palette(), sort_keys=True)

def luminous(color):
    rgb = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    h, saturation, value = colorsys.rgb_to_hsv(*rgb)
    rgb = colorsys.hsv_to_rgb(h, max(.65, saturation), max(.95, value))
    return '#'+''.join(f'{round(v*255):02x}' for v in rgb)

def icon_svg(action, colors=None):
    if action not in SHAPES: return None
    p = colors or palette()
    index = list(SHAPES).index(action)
    accents = [luminous(p[k]) for k in ('cyan','magenta','yellow')]
    primary, secondary = accents[index%3], accents[(index+1)%3]
    shape = SHAPES[action].replace('{secondary}', secondary)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
<rect width="120" height="120" fill="#020408"/><defs><linearGradient id="bg" x2="0.8" y2="1"><stop stop-color="{p['background']}"/><stop offset="1" stop-color="#020408"/></linearGradient><linearGradient id="neon"><stop stop-color="{primary}"/><stop offset="1" stop-color="{secondary}"/></linearGradient></defs>
<path d="M17 3h86l14 14v86l-14 14H17L3 103V17z" fill="url(#bg)" stroke="{primary}" stroke-opacity=".38"/>
<path d="M8 34V19L19 8h29M73 8h28l11 11v16M112 85v16l-11 11H73M48 112H19L8 101V86" fill="none" stroke="url(#neon)" stroke-width="2"/>
<path d="M14 52h5v17h-5M106 52h-5v17h5M29 102h15m3 0h5m27-85h11" fill="none" stroke="{secondary}" stroke-width="2" opacity=".65"/>
<g fill="none" stroke="{primary}" stroke-width="8" stroke-linejoin="bevel" opacity=".12">{shape}</g>
<g fill="none" stroke="url(#neon)" stroke-width="3.5" stroke-linejoin="bevel" stroke-linecap="square">{shape}</g>
<path d="M53 106h14" stroke="{secondary}" stroke-width="3"/><circle cx="102" cy="40" r="2" fill="{primary}"/>
</svg>'''

def render(action, cache, converter):
    try: return _render(action, cache, converter)
    except (OSError, subprocess.SubprocessError): return None

def _render(action, cache, converter):
    svg = icon_svg(action)
    if svg is None or not converter: return None
    cache.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(svg.encode()).hexdigest()[:20]
    out = cache/('cyber-'+digest+'.jpg')
    if not out.exists():
        with tempfile.TemporaryDirectory(prefix='elgato-cyber-') as directory:
            source=Path(directory)/'icon.svg';source.write_text(svg)
            temp=Path(directory)/'icon.jpg'
            subprocess.run([converter,'-background','#000000','-density','288',str(source),'-resize','120x120','-quality','95',str(temp)],check=True,timeout=5,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            out.write_bytes(temp.read_bytes())
    return out
