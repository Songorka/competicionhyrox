#!/usr/bin/env python3
"""Genera la web estática de competicionhyrox.es.

Uso:  python3 build.py
Lee las páginas de src/ y el calendario de data/competiciones.json,
y escribe los .html finales en la raíz (lo que publica GitHub Pages).
"""
import json, datetime, html, pathlib, re

ROOT = pathlib.Path(__file__).parent
SITE = "https://competicionhyrox.es"
# ID de medición de Google Analytics (empieza por G-). Vacío = sin Analytics ni aviso de cookies.
GA_ID = "G-E2T1MMFZN3"
MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

PAGES = [
    # (fuente, destino, ruta, título, descripción, menú)
    ("inicio.html", "index.html", "/", "Competiciones HYROX en España: calendario, guía y calculadora",
     "Calendario de competiciones HYROX en España, guía de categorías y estaciones y calculadora de tiempo. Web informativa en español.", "inicio"),
    ("calendario.html", "calendario/index.html", "/calendario/", "Calendario HYROX España 2026/27: fechas y sedes",
     "Todas las competiciones HYROX en España: próximas fechas, sedes y resumen de las pruebas ya celebradas.", "calendario"),
    ("que-es.html", "que-es-hyrox/index.html", "/que-es-hyrox/", "Qué es HYROX: formato, recorrido y para quién es",
     "Qué es una competición HYROX, cómo es el formato de 8 km de carrera y 8 estaciones y por qué se ha hecho tan popular en España.", "que-es"),
    ("estaciones.html", "estaciones/index.html", "/estaciones/", "Las 8 estaciones de HYROX explicadas",
     "SkiErg, Sled Push, Sled Pull, Burpee Broad Jumps, remo, Farmers Carry, Sandbag Lunges y Wall Balls: qué son y cómo afrontarlas.", "estaciones"),
    ("categorias.html", "categorias-y-pesos/index.html", "/categorias-y-pesos/", "Categorías y pesos HYROX: Open, Pro, Doubles y Relay",
     "Diferencias entre las categorías Open, Pro, Doubles y Relay y tabla de pesos por estación para hombres y mujeres.", "categorias"),
    ("primera-competicion.html", "primera-competicion/index.html", "/primera-competicion/", "Tu primera competición HYROX: guía práctica",
     "Qué llevar, cómo es el día de la prueba y cómo repartir fuerzas en tu primera competición HYROX.", "primera"),
    ("calculadora.html", "calculadora/index.html", "/calculadora/", "Calculadora de tiempo HYROX: estima tu marca",
     "Calcula tu tiempo estimado en una competición HYROX a partir de tu ritmo de carrera y tu nivel en las estaciones.", "calculadora"),
    ("aviso-legal.html", "aviso-legal/index.html", "/aviso-legal/", "Aviso legal y cookies",
     "Aviso legal, información sobre la naturaleza informativa de la web y política de cookies.", ""),
    ("404.html", "404.html", "/404.html", "Página no encontrada", "La página que buscas no existe.", ""),
]

NAV = [("calendario","/calendario/","Calendario"),("que-es","/que-es-hyrox/","Qué es"),
       ("estaciones","/estaciones/","Estaciones"),("categorias","/categorias-y-pesos/","Categorías y pesos"),
       ("calculadora","/calculadora/","Calculadora")]

FAQ = [
    ("¿Qué es una competición HYROX?",
     "Una carrera de fitness que combina 8 km de carrera con 8 estaciones de ejercicio funcional: 1 km de carrera, una estación, y así hasta completar las ocho. El recorrido es igual en todas las ciudades."),
    ("¿Cuánto se tarda en completar una prueba?",
     "La mayoría de participantes termina entre una hora y una hora y media. En una primera participación, entre 1h15 y 1h45 es un rango habitual."),
    ("¿Necesito clasificarme para participar?",
     "No. Cualquiera puede inscribirse en la categoría que prefiera, sin marcas mínimas ni clasificación previa."),
    ("¿Qué categoría elijo para mi primera vez?",
     "Open si vas solo; Doubles si vas en pareja y prefieres repartir el esfuerzo; Relay si queréis hacerlo en equipo de cuatro."),
    ("¿Cuándo es la próxima competición en España?",
     "Consulta el calendario de esta web: lo actualizamos cada semana con las fechas y sedes anunciadas en España."),
]

def fecha_rango(a, b):
    a = datetime.date.fromisoformat(a); b = datetime.date.fromisoformat(b)
    if a.month == b.month:
        return f"{a.day}–{b.day} {MESES[a.month-1]} {a.year}"
    return f"{a.day} {MESES[a.month-1]} – {b.day} {MESES[b.month-1]} {b.year}"

def json_ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

def event_ld(c):
    return {"@type": "SportsEvent", "name": f"HYROX {c['ciudad']} {c['inicio'][:4]}",
            "startDate": c["inicio"], "endDate": c["fin"],
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "location": {"@type": "Place", "name": c["sede"],
                         "address": {"@type": "PostalAddress", "addressLocality": c["ciudad"], "addressCountry": "ES"}},
            "description": f"Competición de fitness HYROX en {c['ciudad']}: 8 km de carrera y 8 estaciones.",
            "image": f"{SITE}/assets/img/og-portada.jpg",
            "url": f"{SITE}/calendario/#{c['id']}"}

def layout(title, desc, path, body, current, extra_head=""):
    cur_attr = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{href}"{cur_attr if key == current else ""}>{label}</a></li>'
        for key, href, label in NAV)
    ga_attr = f' data-ga="{GA_ID}"' if GA_ID else ""
    cookie_link = ' · <a href="#" data-cookie-reset>Configurar cookies</a>' if GA_ID else ""
    cookie_box = ('<div class="cookie" id="cookie" role="dialog" aria-label="Aviso de cookies" hidden>'
                  '<p>Usamos Google Analytics para saber cuántas personas visitan la web. Solo se activa si aceptas. '
                  '<a href="/aviso-legal/#cookies">Más información</a></p>'
                  '<div class="btns"><button class="btn btn-accent" type="button" data-c="si">Aceptar</button>'
                  '<button class="btn btn-ghost" type="button" data-c="no">Rechazar</button></div></div>') if GA_ID else ""
    return f"""<!doctype html>
<html lang="es"{ga_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | competicionhyrox.es</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/img/og-portada.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0E0F0C">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
{extra_head}
</head>
<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="site-header">
<div class="wrap">
<a class="logo" href="/">COMPETICIÓN<span>HYROX</span>.es</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menú</button>
<nav id="site-nav" class="site-nav" aria-label="Principal"><ul>{nav}</ul></nav>
</div>
</header>
<main id="contenido">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<p>Web informativa e independiente, sin relación con la organización oficial de la competición. HYROX es una marca registrada de su titular. Para inscripciones y reglamento, consulta siempre la web oficial.</p>
<p>© {datetime.date.today().year} competicionhyrox.es · <a href="/aviso-legal/">Aviso legal y cookies</a>{cookie_link}</p>
</div>
</footer>
{cookie_box}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""

def relativize(page, dst):
    """Convierte enlaces internos absolutos (/x) en relativos (../x) para que la web
    funcione igual con el dominio, en usuario.github.io/repositorio/ y abierta en local.
    La 404 se queda con rutas absolutas porque GitHub la sirve desde cualquier dirección."""
    if dst == "404.html":
        return page
    pre = "../" * dst.count("/") or "./"
    page = re.sub(r'(href|src|poster|srcset)="/(?!/)', lambda m: f'{m.group(1)}="{pre}', page)
    return page.replace(", /assets/", ", " + pre + "assets/")

def main():
    hoy = datetime.date.today()
    data = json.loads((ROOT/"data/competiciones.json").read_text(encoding="utf-8"))
    comps = data["competiciones"]
    prox = sorted([c for c in comps if datetime.date.fromisoformat(c["fin"]) >= hoy], key=lambda c: c["inicio"])
    pas = sorted([c for c in comps if datetime.date.fromisoformat(c["fin"]) < hoy], key=lambda c: c["inicio"], reverse=True)

    filas = []
    for i, c in enumerate(prox):
        badge = '<span class="badge next">Próxima</span>' if i == 0 else '<span class="badge">Anunciada</span>'
        extra = f' · {html.escape(c["extra"])}' if c.get("extra") else ""
        filas.append(f'<article class="event" id="{c["id"]}"><span class="dates">{fecha_rango(c["inicio"], c["fin"])}</span>'
                     f'<div class="info"><strong>{html.escape(c["ciudad"])}</strong><span>{html.escape(c["sede"])}{extra}</span></div>{badge}</article>')
    pasadas = []
    for c in pas:
        res = html.escape(c["resumen"]) if c["resumen"] else html.escape(c["sede"]) + "."
        pasadas.append(f'<article class="card past" id="{c["id"]}"><span class="tag">{fecha_rango(c["inicio"], c["fin"])}</span>'
                       f'<h3 style="margin-top:6px">{html.escape(c["ciudad"])}</h3><p>{res}</p></article>')

    if prox:
        n = prox[0]
        proxima = (f'<div class="next-card"><p class="label">Próxima en España</p><p class="city">{html.escape(n["ciudad"])}</p>'
                   f'<p class="meta">{fecha_rango(n["inicio"], n["fin"])} · {html.escape(n["sede"])}</p>'
                   f'<div class="stats"><div class="stat"><b data-countdown="{n["inicio"]}">–</b><span>días</span></div>'
                   f'<div class="stat"><b>{len(prox)}</b><span>pruebas por delante</span></div></div>'
                   f'<a href="/calendario/#{n["id"]}">Ver calendario completo →</a></div>')
    else:
        proxima = ""

    faq_html = '<div class="faq">' + "".join(
        f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in FAQ) + "</div>"
    heads = {
        "index.html": json_ld({"@context": "https://schema.org", "@graph": [
            {"@type": "WebSite", "name": "competicionhyrox.es", "url": SITE + "/", "inLanguage": "es-ES"},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}),
        "calendario/index.html": json_ld({"@context": "https://schema.org", "@graph": [event_ld(c) for c in prox]}),
    }
    repl = {"{{FAQ}}": faq_html, "{{PROXIMA}}": proxima, "{{CAL_PROXIMAS}}": "\n".join(filas) or "<p>No hay pruebas anunciadas por ahora.</p>",
            "{{CAL_PASADAS}}": "\n".join(pasadas), "{{ACTUALIZADO}}": data.get("actualizado", "")}

    urls = []
    for src, dst, path, title, desc, cur in PAGES:
        body = (ROOT/"src"/src).read_text(encoding="utf-8")
        for k, v in repl.items():
            body = body.replace(k, v)
        out = ROOT/dst
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(relativize(layout(title, desc, path, body, cur, heads.get(dst, "")), dst), encoding="utf-8")
        if dst != "404.html":
            urls.append(path)
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{hoy}</lastmod></url>" for u in urls)
    (ROOT/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    print("OK:", len(PAGES), "páginas")

if __name__ == "__main__":
    main()
