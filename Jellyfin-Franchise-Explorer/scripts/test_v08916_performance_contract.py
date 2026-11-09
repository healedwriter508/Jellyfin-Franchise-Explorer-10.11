#!/usr/bin/env python3
"""v0.8.9.16 performance and Jellyfin-theme contracts (static; live Jellyfin still required)."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
project = root / 'src/Jellyfin.Plugin.FranchiseExplorer'
read = lambda rel: (project / rel).read_text(encoding='utf-8')
timeline_cs = read('Api/FranchiseTimelineController.cs')
browse_cs = read('Api/FranchiseBrowseController.cs')
artwork_cs = read('Api/FranchiseArtworkController.cs')
monitor_cs = read('Web/TimelinePlaybackMonitorService.cs')
service_cs = read('Web/HomeTileRegistrationService.cs')
home_js = read('Web/franchise-my-media.js')
engine_js = read('Web/franchise-timeline.js')
browse_html = read('Configuration/browsePage.html')
config_html = read('Configuration/configPage.html')

# Server: playback events only touch armed/playing rows; idle users skip the lock and disk.
assert 'ActiveRows' in timeline_cs and 'LoadActiveRowsAsync' in timeline_cs
assert 'knownRows.IsEmpty) return;' in timeline_cs
assert timeline_cs.index('knownRows.IsEmpty') < timeline_cs.index('await WriteLock.WaitAsync(cancellationToken).ConfigureAwait(false);\n        try\n        {\n            var activeIndex')
assert timeline_cs.count('UpdateActiveIndex(user, rowId,') == 3, 'Save, Activate and Complete keep the index current'
assert 'no timeline records for this user' not in timeline_cs
assert '_logger.LogDebug("Franchise Explorer: Jellyfin playback stopped' in monitor_cs

# Server: cached embedded assets, ETag revalidation, separate cached tile art.
assert 'EmbeddedAssets.Text(EmbeddedAssets.BrowsePage)' in browse_cs
assert '[HttpGet("TileArt")]' in browse_cs and 'max-age=604800' in browse_cs
assert browse_cs.count('"no-store"') == 1, 'Only the authenticated Catalog stays no-store'
assert 'version = EmbeddedAssets.Version' in browse_cs
assert 'private, no-cache' in artwork_cs and 'etag' in artwork_cs
assert 'Convert.ToBase64String' not in service_cs and 'GetManifestResourceStream' not in service_cs

# Browser: Home-only work, single-row auto-next poll, tagged image URLs, deduplicated episode fetches.
assert home_js.count('function onHomeRoute()') == 1 and home_js.count('const onHomeRoute = ()') == 1
assert 'if (!onHomeRoute()) return;' in home_js
assert "!onHomeRoute() || (!force && Date.now() - lastFetch < 10000)" in home_js
assert "api('/FranchiseExplorer/TimelineState/'+encodeURIComponent(owner.rowId),auth)" in home_js
assert "const states=await api('/FranchiseExplorer/TimelineState',auth);" not in home_js
assert "imageTag(item.ImageTags.Primary)" in home_js and "tagged(tags[type])" in browse_html
assert 'episodesOf(item.Id)' in engine_js and 'Promise.all(refs.map' in engine_js
assert '__FE_TILE_ART_URL__' in home_js and 'data:image/webp' not in home_js

# Look: Jellyfin accent and no leftover teal palette in shipped UI.
for name, text in [('home', home_js), ('engine', engine_js), ('browse', browse_html), ('config', config_html)]:
    for teal in ('#11b3c8', '#0b9caf', '#079eb3', '#09b1c5', '#069eb1', '#12b7cb'):
        assert teal not in text.lower(), (name, teal)
assert 'sectionTitle sectionTitle-cards' in home_js
assert 'Jellyfin-native theme layer' in browse_html and 'Jellyfin-native theme layer' in config_html
assert 'font-family:inherit' in home_js and 'Arial' not in home_js
print('v0.8.9.16 performance and Jellyfin-theme contracts passed (static; live Jellyfin still required).')
