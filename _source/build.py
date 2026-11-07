#!/usr/bin/env python3
"""
Génère les pages du site ismailsabor.com à partir des données ci-dessous.

Pour ajouter / mettre à jour un chapitre :
  1. déposer le PDF dans cours/ ou td/ (même nom que l'ancien pour une mise à jour) ;
  2. lancer :  python3 _source/build.py
     (la date « Mis à jour le » est lue automatiquement dans les PDF).

Le dossier _source/ n'est pas publié par GitHub Pages (il commence par « _ »).
"""
import datetime, html, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SITE = "https://ismailsabor.com"
GOAT = "ismailsabor"

# --------------------------------------------------------------------------
# Données
# --------------------------------------------------------------------------
THEMES = {
    "fond":    ("Fondamentaux", "fond"),
    "analyse": ("Analyse", "analyse"),
    "algebre": ("Algèbre", "algebre"),
    "geo":     ("Géométrie", "geo"),
}

# (numéro, slug, titre, thème, résumé court, programme détaillé)
CHAPITRES = [
    (0, "rappels-calculatoires", "Rappels calculatoires", "fond",
     "Les techniques de calcul indispensables, abordées d’un point de vue pratique.",
     "Le but de ce chapitre est de mettre en œuvre des techniques de calcul indispensables en mathématiques et dans les autres disciplines scientifiques. Les définitions précises et les constructions rigoureuses sont à étudier ultérieurement. Le point de vue adopté ici est essentiellement pratique."),
    (1, "nombres-complexes", "Nombres complexes", "algebre",
     "Formes algébrique et exponentielle, équations du second degré, racines n-ièmes, géométrie.",
     "Le but de ce chapitre est de consolider et d’approfondir les notions de nombres complexes acquises en classe de terminale. L’étude algébrique de l’ensemble ℂ, la résolution des équations algébriques (second degré, racines n-ièmes de l’unité), l’introduction de l’exponentielle complexe et l’interprétation géométrique des nombres complexes sont les aspects que nous y aborderons."),
    (2, "etude-globale-des-fonctions", "Généralités sur les fonctions", "analyse",
     "Parité, monotonie, branches infinies et bijections.",
     "L’objectif de ce chapitre est de présenter les notions fondamentales relatives aux fonctions d’une variable réelle (parité, monotonie, branches infinies, etc.) et d’introduire une section dédiée à la notion de bijection."),
    (3, "fonctions-usuelles", "Fonctions usuelles", "analyse",
     "Fonctions trigonométriques, hyperboliques et leurs réciproques.",
     "Nous présentons les fonctions usuelles telles que le sinus et le cosinus. Leur existence est admise, mais leurs principales propriétés sont étudiées afin d’introduire d’autres fonctions importantes. L’objectif est de donner une bonne maîtrise de ces fonctions : savoir lire et tracer leur graphe, définir les fonctions réciproques (trigonométriques et hyperboliques) et manipuler des relations essentielles comme les formules d’addition."),
    (4, "logique-et-raisonnement", "Logique et raisonnement", "fond",
     "Connecteurs, quantificateurs et grands types de raisonnement.",
     "Ce chapitre introduit le vocabulaire, les notations et les outils nécessaires à la rédaction claire et rigoureuse d’une démonstration : connecteurs logiques et quantificateurs, négation d’une proposition, réciproque et contraposée, conditions nécessaires et suffisantes, contre-exemples, et les principaux types de raisonnement — par contraposée, par disjonction des cas, par analyse-synthèse, par l’absurde et par récurrence."),
    (5, "calcul-algebrique", "Calcul algébrique", "fond",
     "Sommes, produits et formule du binôme.",
     "Ce chapitre initie aux techniques fondamentales de calcul sur les sommes et produits de nombres réels ou complexes, notamment la formule du binôme. L’objectif est de développer l’aisance dans la manipulation des symboles et des expressions à travers des exemples variés et de difficulté progressive."),
    (6, "primitives-et-calcul-integral", "Primitives et calcul intégral", "analyse",
     "Primitives usuelles, changement de variable, intégration par parties.",
     "Ce chapitre introduit le calcul des primitives et les premières notions de calcul intégral. Il s’agit de revoir et d’approfondir les techniques du lycée, de savoir calculer les primitives des fonctions usuelles et d’utiliser les méthodes d’intégration courantes — changement de variable, intégration par parties — en comprenant quand les appliquer. L’accent est mis sur la pratique et l’intuition du calcul intégral."),
    (7, "equations-differentielles", "Équations différentielles linéaires", "analyse",
     "Équations du premier et du second ordre, problème de Cauchy.",
     "Ce chapitre porte sur les équations différentielles linéaires du premier et du second ordre : résolution des équations homogènes, recherche d’une solution particulière, application au problème de Cauchy, existence et unicité des solutions."),
    (8, "systemes-lineaires", "Systèmes linéaires", "algebre",
     "Résolution des systèmes d’équations linéaires par la méthode du pivot.",
     ""),
    (9, "geometrie-plane", "Géométrie plane", "geo",
     "Repères, produit scalaire, déterminant, droites et cercles.",
     "Ce chapitre est consacré à la géométrie du plan euclidien : repères, coordonnées cartésiennes et polaires, vecteurs, produit scalaire et déterminant avec leurs interprétations géométriques, droites, cercles et transformations du plan sous forme géométrique et analytique."),
    (10, "geometrie-dans-l-espace", "Géométrie dans l’espace", "geo",
     "Produit vectoriel, droites et plans, distances et projections.",
     "Ce chapitre prolonge l’étude à l’espace euclidien : repères, vecteurs, produit scalaire et produit vectoriel, droites et plans par équations cartésiennes et paramétriques, distances, projections orthogonales et intersections."),
    (11, "nombres-reels", "Nombres réels", "fond",
     "Ordre, inégalités, valeur absolue, bornes supérieure et inférieure.",
     "Les propriétés fondamentales des nombres réels sont rappelées en mettant l’accent sur l’ordre : inégalités, valeur absolue, intervalles, puis axiome de la borne supérieure et notions de maximum, minimum, majorant et minorant. Les quantificateurs servent à formuler rigoureusement ces propriétés et leurs négations."),
    (12, "suites-usuelles", "Suites usuelles", "analyse",
     "Suites arithmétiques, géométriques et récurrentes linéaires d’ordre 2.",
     "Un chapitre volontairement léger : suites arithmétiques, géométriques et arithmético-géométriques, puis suites récurrentes linéaires homogènes d’ordre deux, avec pour objectif principal la détermination de leur terme général."),
    (13, "suites-numeriques", "Suites numériques", "analyse",
     "Convergence, opérations sur les limites, suites extraites et monotones.",
     "Ce chapitre étudie les suites numériques sous leurs aspects qualitatifs (monotonie, convergence, divergence) et quantitatifs (majoration, encadrement, vitesse de convergence) : limites et opérations, formes indéterminées, théorèmes de convergence, suites extraites, suites monotones et applications algorithmiques."),
    (14, "limites", "Limites de fonctions", "analyse",
     "Limites finies et infinies, opérations, encadrement, formes indéterminées.",
     "Les notions de limite pour les fonctions prolongent celles des suites : limite finie ou infinie en un point ou à l’infini, unicité, limites à gauche et à droite, opérations, théorèmes d’encadrement et de monotonie, formes indéterminées."),
    (15, "continuite", "Continuité", "analyse",
     "Valeurs intermédiaires, bornes atteintes, dichotomie, fonction réciproque.",
     "Continuité en un point puis sur un intervalle, caractérisation séquentielle, opérations sur les fonctions continues, théorème des valeurs intermédiaires et des bornes atteintes, méthode de dichotomie, continuité et stricte monotonie, et extension aux fonctions à valeurs complexes."),
    (16, "derivabilite", "Dérivabilité", "analyse",
     "Rolle, accroissements finis, fonctions lipschitziennes, classe Cᵏ, convexité.",
     "Nombre dérivé, interprétations géométrique et cinématique, opérations sur les fonctions dérivables, théorème de Rolle et des accroissements finis, variations, extremums et inégalités, fonctions lipschitziennes, dérivées d’ordre supérieur et classe Cᵏ, convexité, et extension aux fonctions à valeurs complexes."),
    (17, "developpements-limites", "Développements limités", "analyse",
     "Relations de comparaison, Taylor-Young et calculs asymptotiques.",
     "Relations de comparaison (domination, négligeabilité, équivalence), développements limités usuels et formule de Taylor-Young, puis applications : calcul de limites, étude locale, asymptotes, position par rapport à la tangente, prolongement par continuité, extremums locaux et suites récurrentes."),
    (18, "calcul-matriciel", "Calcul matriciel", "algebre",
     "Opérations sur les matrices, pivot de Gauss-Jordan, inversion.",
     "Matrices et opérations usuelles, produit matriciel et ses propriétés, opérations élémentaires et méthode du pivot de Gauss-Jordan pour résoudre des systèmes et inverser une matrice, matrices diagonales, triangulaires, symétriques et antisymétriques, transposée, groupe linéaire et puissances de matrices."),
    (19, "polynomes-et-fractions-rationnelles", "Polynômes et fractions rationnelles", "algebre",
     "Racines, factorisation dans ℝ[X] et ℂ[X], éléments simples.",
     "Opérations sur les polynômes et division euclidienne, divisibilité et racines, multiplicité, factorisation dans ℝ[X] et ℂ[X] et théorème de d’Alembert-Gauss, formules de Leibniz et de Taylor, puis fractions rationnelles et décomposition en éléments simples dans les cas classiques."),
    (20, "espaces-vectoriels", "Espaces vectoriels", "algebre",
     "Sous-espaces, familles libres et génératrices, sommes directes.",
     "Structure d’espace vectoriel, sous-espaces, combinaisons linéaires et sous-espaces engendrés, familles génératrices, libres ou liées, sommes de sous-espaces, sommes directes et supplémentaires, bases et coordonnées."),
    (21, "espaces-vectoriels-de-dimension-finie", "Espaces vectoriels de dimension finie", "algebre",
     "Bases, dimension, rang et formule de Grassmann.",
     "Existence de bases, théorèmes de la base extraite et de la base incomplète, caractérisations des bases, calcul de dimensions et de rangs par l’algorithme de Gauss, sous-espaces et supplémentaires en dimension finie, formule de Grassmann."),
    (22, "applications-lineaires", "Applications linéaires", "algebre",
     "Noyau, image, isomorphismes et théorème du rang.",
     "Applications linéaires, noyau et image, injectivité, surjectivité et bijectivité, isomorphismes, endomorphismes et automorphismes, détermination par l’image d’une base, interprétation géométrique, puis théorème du rang et ses conséquences."),
    (23, "representations-matricielles", "Représentations matricielles", "algebre",
     "Matrice d’une application linéaire, changement de base, matrices semblables.",
     "Matrice d’une famille de vecteurs et d’une application linéaire dans des bases données, rang, noyau et image d’une matrice, lien avec les systèmes linéaires, changements de base et matrices semblables."),
]

DEVOIRS = [
    ("DL01", "devoirs/DL01.pdf", "Devoir libre n°1", "Rappels calculatoires",
     "Cinq exercices indépendants pour consolider les techniques de calcul."),
    ("DL02", "devoirs/DL02.pdf", "Devoir libre n°2", "Nombres complexes",
     "Calculer cos(π/17) et l’exprimer à l’aide de radicaux."),
]

# (code, pdf, difficulté 1-3, source, description, chapitres)
VERS_EXCELLENCE = [
    ("VE1", "vers-excellence/VE1.pdf", 2, "",
     "Deux problèmes : décomposition en éléments simples et sommes harmoniques, puis calcul d’une intégrale de Gauss.",
     [5, 6]),
    ("VE2", "vers-excellence/VE2.pdf", 2, "",
     "Résolution guidée d’une équation différentielle linéaire du second ordre à coefficients variables.",
     [6, 7]),
    ("VE3", "vers-excellence/VE3.pdf", 3, "",
     "Deux exercices et deux problèmes, dont la convergence de la somme des inverses des carrés vers π²/6.",
     [5, 6, 7]),
    ("VE4", "vers-excellence/VE4.pdf", 3, "Inspiré de Maths 1 — CNC 2026",
     "Formule de Taylor avec reste intégral et application au calcul de sommes de séries.",
     [6, 5, 13, 20]),
]

DIFF_LABEL = {1: "Accessible", 2: "Intermédiaire", 3: "Exigeant"}

# --------------------------------------------------------------------------
# Outils
# --------------------------------------------------------------------------
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

def pdf_info(path):
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", out).group(1))
    m = re.search(r"ModDate:\s+(.*)", out) or re.search(r"CreationDate:\s+(.*)", out)
    try:
        d = datetime.datetime.strptime(m.group(1).strip()[:24], "%a %b %d %H:%M:%S %Y").date()
    except Exception:
        d = datetime.date.fromtimestamp(os.path.getmtime(path))
    return pages, d

def fdate(d):
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"

def esc(s):
    return html.escape(s, quote=True)

ICONS = {
    # Σ stylisé
    "fond": '<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M29 9H11l10 11-10 11h18"/></svg>',
    # courbe et tangente
    "analyse": '<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 31c6-1 9-16 15-16s9 9 15 4" /><path d="M8 25 33 9" stroke-width="1.6" stroke-dasharray="2 3"/><circle cx="20" cy="15" r="2.2" fill="currentColor" stroke="none"/></svg>',
    # matrice
    "algebre": '<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8H8v24h4M28 8h4v24h-4"/><g fill="currentColor" stroke="none"><circle cx="15" cy="14" r="1.8"/><circle cx="20" cy="14" r="1.8"/><circle cx="25" cy="14" r="1.8"/><circle cx="15" cy="20" r="1.8"/><circle cx="20" cy="20" r="1.8"/><circle cx="25" cy="20" r="1.8"/><circle cx="15" cy="26" r="1.8"/><circle cx="20" cy="26" r="1.8"/><circle cx="25" cy="26" r="1.8"/></g></svg>',
    # triangle inscrit
    "geo": '<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"><circle cx="20" cy="21" r="13"/><path d="M20 8 31.3 27.5H8.7Z"/></svg>',
}
ICON_DL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 20h14"/></svg>'
STAR = '<svg viewBox="0 0 24 24" class="{c}"><path d="M12 2.8l2.8 6 6.5.7-4.9 4.4 1.4 6.4L12 17l-5.8 3.3 1.4-6.4L2.7 9.5l6.5-.7z"/></svg>'
LOGO = '<svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#731928"/><path d="M40 12c-6 0-8 4-9 11l-3 20c-1 6-3 9-8 9" fill="none" stroke="#d6822a" stroke-width="5" stroke-linecap="round"/><path d="M22 34h14" stroke="#fff" stroke-width="4" stroke-linecap="round"/></svg>'

def stars(n):
    s = "".join(STAR.format(c="on" if i < n else "off") for i in range(3))
    return f'<span class="stars" role="img" aria-label="Difficulté {n} sur 3 : {DIFF_LABEL[n]}">{s}<span class="stars-label">{DIFF_LABEL[n]}</span></span>'

NAV = [("index.html", "Accueil"), ("Cours.html", "Cours & TD"), ("Devoirs.html", "Devoirs"),
       ("verslexcellence.html", "Vers l’Excellence"), ("index.html#contact", "Contact")]

def page(filename, title, description, body, current, extra_head=""):
    nav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>'
        for href, label in NAV)
    url = SITE + ("/" if filename == "index.html" else "/" + filename)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ismail Sabor — Mathématiques">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/img/apercu.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="img/apple-touch-icon.png">
  <meta name="theme-color" content="#731928">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&family=Source+Sans+3:wght@400;600;700&display=swap">
  <link rel="stylesheet" href="assets/css/site.css">
  <script data-goatcounter="https://{GOAT}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html">{LOGO}<span>Ismail Sabor</span></a>
    <button class="menu-btn" aria-label="Menu" aria-expanded="false" onclick="var n=document.querySelector('.nav');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <ul class="nav">{nav}</ul>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <span>© <span class="year">2026</span> Ismail Sabor — Professeur de mathématiques, CPGE Lydex Benguerir</span>
    <a href="index.html#contact">Contact</a>
  </div>
</footer>
<script>document.querySelectorAll('.year').forEach(function(e){{e.textContent=new Date().getFullYear()}});</script>
</body>
</html>
"""

def write(name, content):
    with open(name, "w", encoding="utf-8") as f:
        f.write(content)

# --------------------------------------------------------------------------
# Cours & TD
# --------------------------------------------------------------------------
def build_cours():
    rows = []
    for n, slug, titre, theme, resume, prog in CHAPITRES:
        cours, td = f"cours/Cours{n:02d}_{slug}.pdf", f"td/TD{n:02d}_{slug}.pdf"
        pc, dc = pdf_info(cours)
        pt, dt = pdf_info(td)
        maj = max(dc, dt)
        tname, tcls = THEMES[theme]
        details = f"<details><summary>Programme du chapitre</summary><p>{esc(prog)}</p></details>" if prog else ""
        search = esc(f"{n} {titre} {resume} {prog} {tname}".lower())
        rows.append(f"""
    <article class="chapter" id="ch{n:02d}" data-theme="{theme}" data-search="{search}">
      <div class="icon theme-{tcls}" aria-hidden="true">{ICONS[theme]}</div>
      <div>
        <div class="num">Chapitre {n}</div>
        <h3>{esc(titre)}</h3>
        <p class="summary">{esc(resume)}</p>
        <div class="meta"><span class="theme-tag c-{tcls}">{tname}</span><span>Mis à jour le {fdate(maj)}</span></div>
        {details}
      </div>
      <div class="dl">
        <a class="btn primary small" href="{cours}" data-goatcounter-click="cours-{n:02d}-{slug}" data-goatcounter-title="Cours {n} — {esc(titre)}">{ICON_DL}Cours <small>{pc} p.</small></a>
        <a class="btn small" href="{td}" data-goatcounter-click="td-{n:02d}-{slug}" data-goatcounter-title="TD {n} — {esc(titre)}">{ICON_DL}TD <small>{pt} p.</small></a>
      </div>
    </article>""")

    chips = '<button class="chip" data-filter="all" aria-pressed="true">Tous</button>' + "".join(
        f'<button class="chip" data-filter="{k}" aria-pressed="false"><span class="dot theme-{v[1]}"></span>{v[0]}</button>'
        for k, v in THEMES.items())

    body = f"""
<div class="wrap">
  <div class="page-head">
    <div class="eyebrow">1ère année TSI</div>
    <h1>Cours &amp; TD</h1>
    <p class="lead">Les {len(CHAPITRES)} chapitres du programme de première année TSI, dans l’ordre du cours. Pour chaque chapitre : le polycopié de cours et la feuille de TD.</p>
    <p class="lead" style="font-size:.95rem">Je tiens à remercier vivement M. El Bakkali, dont le cours a été une source d’inspiration majeure.</p>
  </div>
  <div class="toolbar" role="toolbar" aria-label="Filtrer les chapitres">
    {chips}
    <label class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input type="search" id="q" placeholder="Rechercher un chapitre…" aria-label="Rechercher un chapitre"></label>
  </div>
  <div class="chapters">{"".join(rows)}
    <p class="empty" id="empty">Aucun chapitre ne correspond à votre recherche.</p>
  </div>
</div>
<script>
(function () {{
  var chips = document.querySelectorAll('.chip'), q = document.getElementById('q'),
      rows = document.querySelectorAll('.chapter'), empty = document.getElementById('empty'), theme = 'all';
  function norm(s) {{ return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, ''); }}
  function apply() {{
    var t = norm(q.value.trim()), shown = 0;
    rows.forEach(function (r) {{
      var ok = (theme === 'all' || r.dataset.theme === theme) && (!t || norm(r.dataset.search).indexOf(t) > -1);
      r.style.display = ok ? '' : 'none'; if (ok) shown++;
    }});
    empty.style.display = shown ? 'none' : 'block';
  }}
  chips.forEach(function (c) {{
    c.addEventListener('click', function () {{
      chips.forEach(function (x) {{ x.setAttribute('aria-pressed', 'false'); }});
      c.setAttribute('aria-pressed', 'true'); theme = c.dataset.filter; apply();
    }});
  }});
  q.addEventListener('input', apply);
}})();
</script>"""
    write("Cours.html", page("Cours.html", "Cours et TD de mathématiques — 1ère année TSI | Ismail Sabor",
                             "Les 24 chapitres de mathématiques de première année TSI : polycopiés de cours et feuilles de TD à télécharger.",
                             body, "Cours.html"))

    # anciennes pages ChapitreN.html : redirection vers la bonne ligne
    for n, slug, titre, *_ in CHAPITRES:
        target = f"Cours.html#ch{n:02d}"
        write(f"Chapitre{n}.html", f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Chapitre {n} : {esc(titre)} | Ismail Sabor</title>
  <link rel="canonical" href="{SITE}/{target}">
  <meta http-equiv="refresh" content="0; url={target}">
  <meta name="robots" content="noindex">
</head>
<body>
  <p>Cette page a déménagé : <a href="{target}">Chapitre {n} — {esc(titre)}</a>.</p>
</body>
</html>
""")

# --------------------------------------------------------------------------
# Devoirs
# --------------------------------------------------------------------------
def build_devoirs():
    cards = []
    for code, pdf, titre, theme, desc in DEVOIRS:
        p, d = pdf_info(pdf)
        cards.append(f"""
    <article class="card">
      <div class="top"><h3>{code[:2]} {int(code[2:])}</h3><span class="source">{esc(theme)}</span></div>
      <p>{esc(desc)}</p>
      <div class="foot"><small>{p} pages · {fdate(d)}</small>
        <a class="btn primary small" href="{pdf}" data-goatcounter-click="devoir-{code.lower()}" data-goatcounter-title="{esc(titre)}">{ICON_DL}Télécharger</a></div>
    </article>""")
    body = f"""
<div class="wrap">
  <div class="page-head">
    <div class="eyebrow">1ère année TSI</div>
    <h1>Devoirs</h1>
    <p class="lead">Les devoirs libres, pour s’entraîner à la maison sur les chapitres déjà traités en classe.</p>
  </div>
  <div class="cards">{"".join(cards)}
  </div>
</div>"""
    write("Devoirs.html", page("Devoirs.html", "Devoirs de mathématiques — 1ère année TSI | Ismail Sabor",
                               "Devoirs libres de mathématiques pour la première année TSI, à télécharger.",
                               body, "Devoirs.html"))

# --------------------------------------------------------------------------
# Vers l'Excellence
# --------------------------------------------------------------------------
def build_ve():
    titres = {n: t for n, _, t, *_ in CHAPITRES}
    cards = []
    for code, pdf, diff, source, desc, chaps in VERS_EXCELLENCE:
        p, d = pdf_info(pdf)
        tags = "".join(f'<span class="tag">{esc(titres[c])}</span>' for c in sorted(chaps))
        data = " ".join(str(c) for c in chaps)
        cards.append(f"""
    <article class="card" data-chap="{data}" data-diff="{diff}">
      <div class="top"><h3>{code}</h3>{f'<span class="source">{esc(source)}</span>' if source else ""}</div>
      {stars(diff)}
      <p>{esc(desc)}</p>
      <div class="tags">{tags}</div>
      <div class="foot"><small>{p} pages</small>
        <a class="btn primary small" href="{pdf}" data-goatcounter-click="ve-{code.lower()}" data-goatcounter-title="Vers l'Excellence {code}">{ICON_DL}Télécharger</a></div>
    </article>""")
    used = sorted({c for *_, chaps in VERS_EXCELLENCE for c in chaps})
    opts = "".join(f'<option value="{c}">Ch. {c} — {esc(titres[c])}</option>' for c in used)
    body = f"""
<div class="wrap">
  <div class="page-head">
    <div class="eyebrow">Préparation aux concours</div>
    <h1>Vers l’Excellence</h1>
    <p class="lead">Des sujets inspirés des concours de mathématiques français et marocains, adaptés au programme de première année TSI. Chaque sujet indique les chapitres à maîtriser et un niveau de difficulté pour guider votre progression.</p>
  </div>
  <div class="legend">
    {stars(1)} {stars(2)} {stars(3)}
  </div>
  <div class="toolbar">
    <label class="search" style="margin-left:0;max-width:380px">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 6h16M7 12h10M10 18h4"/></svg>
      <select id="chap" aria-label="Filtrer par chapitre" style="width:100%;padding:9px 14px 9px 38px;border-radius:999px;border:1.5px solid var(--line);font:inherit;background:var(--card)">
        <option value="">Tous les chapitres</option>{opts}
      </select>
    </label>
  </div>
  <div class="cards">{"".join(cards)}
  </div>
</div>
<script>
document.getElementById('chap').addEventListener('change', function () {{
  var v = this.value;
  document.querySelectorAll('.card[data-chap]').forEach(function (c) {{
    c.style.display = !v || c.dataset.chap.split(' ').indexOf(v) > -1 ? '' : 'none';
  }});
}});
</script>"""
    write("verslexcellence.html", page("verslexcellence.html", "Vers l’Excellence — sujets de concours, 1ère année TSI | Ismail Sabor",
                                       "Sujets inspirés des concours (CNC, concours français) adaptés à la première année TSI, avec niveau de difficulté et chapitres concernés.",
                                       body, "verslexcellence.html"))

# --------------------------------------------------------------------------
# Accueil
# --------------------------------------------------------------------------
SOCIAL = {
    "LinkedIn": ("https://www.linkedin.com/in/ismail-sabor-1925b6318/", '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/>'),
    "X": ("https://twitter.com/SaborIsmail", '<path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.3l-4.9-6.4L5.2 21H2.1l7.3-8.3L1.8 3h6.4l4.4 5.9zm-1.1 16.2h1.7L7.3 4.7H5.5z"/>'),
    "Instagram": ("https://www.instagram.com/ismailsabor/", '<path d="M12 7.3a4.7 4.7 0 1 0 0 9.4 4.7 4.7 0 0 0 0-9.4zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm4.9-8.9a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2zM12 4.6c2.4 0 2.7 0 3.6.1 2.4.1 3.6 1.3 3.7 3.7.1.9.1 1.2.1 3.6s0 2.7-.1 3.6c-.1 2.4-1.3 3.6-3.7 3.7-.9.1-1.2.1-3.6.1s-2.7 0-3.6-.1c-2.4-.1-3.6-1.3-3.7-3.7C4.6 14.7 4.6 14.4 4.6 12s0-2.7.1-3.6C4.8 6 6 4.8 8.4 4.7c.9-.1 1.2-.1 3.6-.1zM12 3c-2.4 0-2.7 0-3.7.1C5.1 3.2 3.2 5 3.1 8.3 3 9.3 3 9.6 3 12s0 2.7.1 3.7c.1 3.3 2 5.1 5.2 5.2 1 .1 1.3.1 3.7.1s2.7 0 3.7-.1c3.3-.1 5.1-2 5.2-5.2.1-1 .1-1.3.1-3.7s0-2.7-.1-3.7c-.1-3.3-2-5.1-5.2-5.2C14.7 3 14.4 3 12 3z"/>'),
    "Facebook": ("https://www.facebook.com/Isma9lik1", '<path d="M13.5 21v-7.5H16l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H8v3h2.4V21z"/>'),
}

def build_index():
    nb_ch = len(CHAPITRES)
    socials = "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{k}"><svg viewBox="0 0 24 24">{p}</svg></a>'
                      for k, (u, p) in SOCIAL.items())
    body = f"""
<section class="hero">
  <div class="wrap">
    <h1>Maybe it’s not about <em>being</em>,<br>but <em>becoming</em>.</h1>
    <p>Cours, TD et sujets de préparation aux concours de mathématiques pour la première année TSI.</p>
    <div class="actions">
      <a class="btn solid-light" href="Cours.html">Accéder aux cours &amp; TD</a>
      <a class="btn light" href="verslexcellence.html">Vers l’Excellence</a>
    </div>
  </div>
</section>

<div class="wrap">
  <div class="quick">
    <a href="Cours.html"><div class="eyebrow">Élèves</div><h3>Cours &amp; TD</h3><p>Polycopiés de cours et feuilles d’exercices, chapitre par chapitre.</p><span class="count">{nb_ch} chapitres →</span></a>
    <a href="Devoirs.html"><div class="eyebrow">Élèves</div><h3>Devoirs</h3><p>Devoirs libres pour s’entraîner à la maison.</p><span class="count">{len(DEVOIRS)} devoirs →</span></a>
    <a href="verslexcellence.html"><div class="eyebrow">Concours</div><h3>Vers l’Excellence</h3><p>Sujets de concours adaptés, classés par difficulté.</p><span class="count">{len(VERS_EXCELLENCE)} sujets →</span></a>
  </div>
</div>

<section class="block" id="apropos">
  <div class="wrap about">
    <img src="img/background.jpg" alt="Ismail Sabor" width="960" height="1280" loading="lazy">
    <div>
      <div class="eyebrow">À propos</div>
      <h2>Ismail Sabor</h2>
      <p class="intro">Professeur agrégé de mathématiques aux classes préparatoires (CPGE) du Lycée d’Excellence de Benguerir, Maroc.</p>
      <div class="timeline">
        <div>
          <h3>Formation</h3>
          <ul>
            <li>Baccalauréat Sciences Mathématiques A</li>
            <li>Licence en Mathématiques et Applications</li>
            <li>Master en Mathématiques pures</li>
            <li>Agrégation de Mathématiques</li>
          </ul>
        </div>
        <div>
          <h3>Expérience</h3>
          <ul>
            <li>Préparation à l’agrégation externe, CRMEF Fès (1 an)</li>
            <li>Préparation à l’agrégation externe, UM6P Benguerir (1 an)</li>
            <li>Stage aux CPGE Lydex Benguerir (1 an)</li>
            <li>Professeur de mathématiques, CPGE Lydex Benguerir</li>
          </ul>
        </div>
      </div>
      <p style="margin-top:24px"><a class="btn" href="CV-Ismail-Sabor.pdf" download data-goatcounter-click="cv" data-goatcounter-title="CV">{ICON_DL}Télécharger le CV</a></p>
    </div>
  </div>
</section>

<section class="block contact" id="contact">
  <div class="wrap grid">
    <div>
      <div class="eyebrow">Contact</div>
      <h2>Une question ?</h2>
      <p>Élèves, parents ou collègues : écrivez-moi via le formulaire ou directement par e-mail.</p>
      <a class="mail" href="mailto:isma9l.s1bor@gmail.com">isma9l.s1bor@gmail.com</a>
      <div class="socials">{socials}</div>
    </div>
    <form class="contact-form" id="contact-form" action="https://formspree.io/f/mblrjbar" method="POST">
      <input type="text" name="Nom" placeholder="Votre nom" required>
      <input type="email" name="email" placeholder="Votre e-mail" required>
      <input type="text" name="Établissement" placeholder="Votre établissement">
      <input type="text" name="Classe" placeholder="Votre classe">
      <textarea class="full" name="Message" rows="6" placeholder="Votre message" required></textarea>
      <div class="full"><button type="submit" class="btn solid-light">Envoyer</button><span id="msg" role="status"></span></div>
    </form>
  </div>
</section>
<script>
(function () {{
  var form = document.getElementById('contact-form'), msg = document.getElementById('msg');
  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    msg.textContent = 'Envoi en cours…';
    fetch(form.action, {{ method: 'POST', body: new FormData(form), headers: {{ 'Accept': 'application/json' }} }})
      .then(function (r) {{
        if (r.ok) {{ msg.textContent = 'Message envoyé, merci ! Je vous répondrai rapidement.'; form.reset(); }}
        else {{ msg.textContent = 'Erreur lors de l’envoi. Écrivez-moi directement par e-mail.'; }}
      }})
      .catch(function () {{ msg.textContent = 'Erreur réseau. Écrivez-moi directement par e-mail.'; }});
  }});
}})();
</script>"""
    write("index.html", page("index.html", "Ismail Sabor — Professeur de mathématiques, CPGE Lydex Benguerir",
                             "Ismail Sabor, professeur agrégé de mathématiques aux CPGE Lydex Benguerir : cours, TD, devoirs et sujets de concours pour la première année TSI.",
                             body, "index.html"))

def build_sitemap():
    today = datetime.date.today().isoformat()
    urls = ["", "Cours.html", "Devoirs.html", "verslexcellence.html"]
    items = "".join(f"<url><loc>{SITE}/{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

if __name__ == "__main__":
    build_index(); build_cours(); build_devoirs(); build_ve(); build_sitemap()
    print("Pages générées.")
