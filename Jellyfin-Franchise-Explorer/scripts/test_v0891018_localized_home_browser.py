#!/usr/bin/env python3
"""Home integration on a non-English Jellyfin Web (mocked German Home page).
Detection must rely on Jellyfin's markup, not on English heading text."""
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "src/Jellyfin.Plugin.FranchiseExplorer/Web/franchise-my-media.js").read_text(encoding="utf-8")
ORIGIN = "http://jellyfin.test"
USER = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
ROOT_NODE = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ROW = "11111111-1111-1111-1111-111111111111"
MOVIE = "55555555-5555-5555-5555-555555555555"
OTHER = "77777777-7777-7777-7777-777777777777"

HTML = f"""<!doctype html><html lang="de"><head><style>
body{{margin:0;background:#101010;color:#fff;font-family:sans-serif}}
.verticalSection{{padding:18px 3%}}.itemsContainer{{display:flex;gap:12px}}
.card{{flex:0 0 230px}}.cardScalable{{height:130px;background:#333}}
</style></head><body>
<div class="verticalSection section0"><h2 class="sectionTitle">Meine Medien</h2>
<div is="emby-itemscontainer" class="itemsContainer">
<div class="card" data-type="CollectionFolder" data-collectiontype="movies"><div class="cardScalable"></div><div class="cardText">Filme</div></div>
<div class="card" data-type="CollectionFolder" data-collectiontype="boxsets"><div class="cardScalable"></div><div class="cardText">Sammlungen</div></div>
<div class="card" data-type="CollectionFolder" data-collectiontype="tvshows"><div class="cardScalable"></div><div class="cardText">Serien</div></div>
</div></div>
<div class="verticalSection section1"><h2 class="sectionTitle">Weiterschauen</h2>
<div is="emby-itemscontainer" class="itemsContainer" data-monitor="videoplayback,markplayed">
<div class="card" data-id="{MOVIE}">Franchise-Film</div><div class="card" data-id="{OTHER}">Anderer Film</div></div></div>
<div class="verticalSection section2"><h2 class="sectionTitle">Neu hinzugefügt</h2>
<div is="emby-itemscontainer" class="itemsContainer"><div class="card" data-id="{MOVIE}">Franchise-Film</div></div></div>
</body></html>"""
STATE = {"RowId": ROW, "ParentNodeId": ROOT_NODE, "Name": "Chronologisch", "Index": 0, "Total": 3,
         "PlaybackMode": "paused", "QueueKeys": [f"x:{MOVIE}"], "CompletedKeys": []}
CATALOG = {"nodes": [{"id": ROOT_NODE, "parentId": "", "name": "Sternenkrieg"}],
           "rows": [{"id": ROW, "parentNodeId": ROOT_NODE, "name": "Chronologisch"}]}


def respond(route):
    path = urlparse(route.request.url).path
    reply = lambda body: route.fulfill(status=200, content_type="application/json", body=json.dumps(body))
    if path.endswith("/web/index.html"):
        route.fulfill(status=200, content_type="text/html", body=HTML)
    elif path.endswith("/FranchiseExplorer/TimelineState"):
        reply([STATE])
    elif path.endswith("/FranchiseExplorer/Catalog"):
        reply(CATALOG)
    elif path.endswith("/Items/" + MOVIE):
        reply({"Id": MOVIE, "Name": "Franchise-Film", "Type": "Movie"})
    elif path.endswith("/Items/" + OTHER):
        reply({"Id": OTHER, "Name": "Anderer Film", "Type": "Movie"})
    else:
        route.fulfill(status=404, body="Not found")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"],
        executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.route(ORIGIN + "/**", respond)
    hide_key = "fe-show-active-native-rows:" + ORIGIN + ":" + USER
    page.add_init_script(
        f"localStorage.setItem('jellyfin_credentials', JSON.stringify({{Servers:[{{UserId:'{USER}', AccessToken:'mock', ManualAddress:'{ORIGIN}'}}]}}));"
        f"localStorage.setItem('{hide_key}','0');")
    page.goto(ORIGIN + "/web/index.html")
    page.add_script_tag(content=SCRIPT)

    # The tile lands in the translated My Media row, directly after Collections.
    page.wait_for_selector("#franchise-explorer-my-media-tile", timeout=10000)
    order = page.evaluate("[...document.querySelector('.section0 .itemsContainer').children].map(c => c.id || c.getAttribute('data-collectiontype'))")
    assert order == ["movies", "boxsets", "franchise-explorer-my-media-tile", "tvshows"], order

    # The resume widget is placed after the translated Continue Watching row.
    page.wait_for_selector(".fe-resume-card", timeout=10000)
    assert page.evaluate("document.querySelector('.section1').nextElementSibling.id") == "franchise-timeline-resume"

    # Hiding franchise titles works in playback rows only; other rows are untouched.
    hidden = "(el) => el.classList.contains('fe-native-franchise-row-hidden')"
    page.wait_for_function(f"document.querySelector('.section1 .card[data-id=\"{MOVIE}\"]').classList.contains('fe-native-franchise-row-hidden')", timeout=10000)
    assert not page.locator(f'.section1 .card[data-id="{OTHER}"]').evaluate(hidden)
    assert not page.locator(f'.section2 .card[data-id="{MOVIE}"]').evaluate(hidden)
    browser.close()
print("PASS non-English Home: tile placement, resume widget anchor, and native-row filter")
