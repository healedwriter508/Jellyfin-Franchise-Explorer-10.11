# Jellyfin 10.11.11 Port Notes (`0.8.9.1015` / `0.8.9.15-port.10.11`)

> [!IMPORTANT]
> **Unofficial Port — Not Endorsed by the Original Author**
>
> This repository is an **unofficial community port** of **Jellyfin Franchise Explorer** to **Jellyfin Server `10.11.11`** (`net9.0`, `targetAbi` `10.11.0.0`).
>
> - **Original project:** [Gost1o1/Jellyfin-Franchise-Explorer](https://github.com/Gost1o1/Jellyfin-Franchise-Explorer) (targeting Jellyfin `12.2` / `.NET 10`)
> - **Original author:** Quinton Burgess (**Gost1o1**)
> - **Disclaimer:** This port is **not affiliated with, endorsed by, or supported by Gost1o1**. Do **not** open issues or support requests for this `10.11` port on the upstream repository.
> - **License:** The upstream [Personal and Noncommercial Use License (Draft) v0.1](LICENSE) is preserved unmodified.

---

## Summary of Substantive Changes

### 1. Target Framework, SDK & Package References
- **Project file (`Jellyfin-Franchise-Explorer/src/Jellyfin.Plugin.FranchiseExplorer/Jellyfin.Plugin.FranchiseExplorer.csproj`):**
  - Retargeted `<TargetFramework>` from `net10.0` to `net9.0` (matching Jellyfin `10.11.11`).
  - Changed `Jellyfin.Controller` and `Jellyfin.Model` `<PackageReference>` versions from `12.2.0` to `10.11.11` with `<ExcludeAssets>runtime</ExcludeAssets>` so zero Jellyfin or ASP.NET runtime DLLs are shipped in the plugin archive.

### 2. Versioning (`0.8.9.1015` / `0.8.9.15-port.10.11`)
- Jellyfin `10.11.11`'s `MediaBrowser.Model.Updates.VersionInfo` (`manifest.json`) and `MediaBrowser.Common.Plugins.LocalPlugin` (`meta.json`) parse plugin versions with `System.Version.Parse`, which throws `System.FormatException` on non-numeric SemVer suffixes such as `0.8.9.15-port`.
- Set numeric 4-part version `0.8.9.1015` across `<Version>`, `<AssemblyVersion>`, `<FileVersion>`, `HomeTileRegistrationService` (`pluginVersion`), `manifest.json`, and `meta.json`, paired with `<InformationalVersion>0.8.9.15-port.10.11</InformationalVersion>` and UI port labeling (`v0.8.9.15-port (Jellyfin 10.11)`).

### 3. Server-Side API & Host Compatibility (`10.11.11` Assembly Audit)
Verified directly against the restored `10.11.11` assemblies (`MediaBrowser.Common.dll`, `MediaBrowser.Controller.dll`, `MediaBrowser.Model.dll`, `Jellyfin.Data.dll`, `Jellyfin.Extensions.dll`):
- **`Api/FranchiseArtworkController.cs`:** Added `[Consumes("multipart/form-data")]` to `Upload(Guid nodeId, string slot, IFormFile file, CancellationToken cancellationToken)` so Jellyfin `10.11`'s Swashbuckle/OpenAPI generator handles `IFormFile` on `[ApiController]` endpoints cleanly without schema generation failures.
- **`Web/TimelinePlaybackMonitorService.cs`:** Confirmed `ISessionManager.PlaybackStart`, `PlaybackProgress` (`EventHandler<PlaybackProgressEventArgs>`), and `PlaybackStopped` (`EventHandler<PlaybackStopEventArgs>`) in `MediaBrowser.Controller.Library`. Updated `Dispatch` to fall back to `args.Users[0].Id` when `args.Session?.UserId` is `Guid.Empty` (a `10.11` session/cast edge case where `PlaybackProgressEventArgs.Users` carries the active user entity).
- **`Api/FranchiseTimelineController.cs`:** Kept `User.FindFirst("Jellyfin-UserId")` primary (`InternalClaimTypes.UserId` in `10.11.11`) and added fallback to `ClaimTypes.NameIdentifier`. Preserved explicit `JsonSerializerOptions(JsonSerializerDefaults.Web)` responses because `10.11.11`'s `JsonDefaults.Options` uses `PropertyNamingPolicy = null` (emitting PascalCase for C# DTO properties).
- **`Plugin.cs`:** Confirmed `BasePlugin<PluginConfiguration>(IApplicationPaths, IXmlSerializer)` and `IHasWebPages`; added `DisplayName = Name` to `PluginPageInfo`.
- **`Web/HomeTileRegistrationService.cs`:** Confirmed `IPluginServiceRegistrator.RegisterServices(IServiceCollection, IServerApplicationHost)` signature in `MediaBrowser.Controller.Plugins` `10.11.11` and preserved reflection-based registration against `Jellyfin.Plugin.JavaScriptInjector.PluginInterface` (`RegisterScript` / `UnregisterScript`), updating `pluginVersion` to `"0.8.9.1015"`.

### 4. Jellyfin Web (`10.11`) Frontend Adjustments & TV Franchise Preservation
- **`Web/franchise-my-media.js`:**
  - **SPA hash routing (`#/home.html` vs `#/home`):** Jellyfin `10.11`'s `jellyfin-web` frequently routes Home as `#/home.html` (or `#!/home.html`, optionally with `?tab=0`) and item pages as `#/details?...`, `#!/details?...`, or `#/details.html?...`. Updated route regexes in `consumeHomeQuickPlay`, `followLocalTimeline`, `params`, `armPlaybackReturn`, and `restorePlaybackOrigin` from `/^#\/?home(?:\?|$)/i` and `/^#\/?details\?/i` to accept optional `!` and `.html`.
  - **Home `.itemsContainer` lookup:** Broadened `FranchiseExplorerNativePlayback.play` container selector to include `#homeTab:not(.hide) .itemsContainer`, `.tabContent.is-active .itemsContainer`, and `.homeSectionsContainer .itemsContainer:not(.hide)` used by `jellyfin-web` `10.11`.
  - **Session & device matching:** Added `LastConnectionAddress` to `localCredentials()` origin matching and `window.ApiClient?.deviceId?.()` fallback in `deviceId()`.
- **`Configuration/configPage.html`:**
  - Added `viewshow` event listeners alongside `pageshow` (with a 300 ms debounce on `loadOnShow`) so Jellyfin `10.11`'s Dashboard initializes the configuration page under both legacy and modern view transitions.
  - Passed `userId` query parameter in the `ApiClient.getJSON` fallback for `Items/{id}`.
  - Updated heading badge to `v0.8.9.15-port (Jellyfin 10.11)`.
- **`Configuration/browsePage.html` & `Web/franchise-timeline.js`:**
  - Added defensive camelCase key normalization when loading `/FranchiseExplorer/Catalog`.
  - Kept full **TV franchise support** intact across admin configuration, standalone browsing, chronological queues, and Home resume cards: complete TV series (`Full`), season ranges (`Seasons`), and cross-season episode ranges (`Episodes`) mixed with movies (`Movie`) and collections (`BoxSet`), backed by `/Shows/{seriesId}/Episodes?userId=...&startIndex=...&limit=...&isMissing=false` and `10.11.11`'s `BaseItemDto` properties (`SeriesId`, `SeriesName`, `ParentIndexNumber`, `IndexNumber`, `RunTimeTicks`).

### 5. Catalog Manifests, Checksum Placeholder & GitHub Actions Packaging
- Updated root [`manifest.json`](manifest.json), [`Jellyfin-Franchise-Explorer/manifest.json`](Jellyfin-Franchise-Explorer/manifest.json), and [`Jellyfin-Franchise-Explorer/scripts/publish_manifest.py`](Jellyfin-Franchise-Explorer/scripts/publish_manifest.py) with:
  - `version`: `"0.8.9.1015"`
  - `targetAbi`: `"10.11.0.0"`
  - `sourceUrl`: `"https://github.com/healedwriter508/Jellyfin-Franchise-Explorer-10.11/releases/download/v0.8.9.1015/franchise-explorer_0.8.9.1015.zip"`
  - `checksum`: `"00000000000000000000000000000000"` (32-hex MD5 placeholder; **must be replaced with the actual release ZIP's MD5 hash** after publishing a GitHub release, either from the workflow summary/artifact `.md5` file or via `python3 Jellyfin-Franchise-Explorer/scripts/publish_manifest.py --version 0.8.9.1015 --archive franchise-explorer_0.8.9.1015.zip --repository healedwriter508/Jellyfin-Franchise-Explorer-10.11`).
- Updated [`.github/workflows/build.yml`](.github/workflows/build.yml) (and aligned [`.github/workflows/release.yml`](.github/workflows/release.yml)) to set up `.NET 9`, run offline static/unit tests, build `Release`, package `Jellyfin.Plugin.FranchiseExplorer.dll` + `meta.json` (`targetAbi: 10.11.0.0`) into `franchise-explorer_0.8.9.1015.zip`, upload the ZIP + `.md5` as build artifacts, and attach the ZIP to a GitHub Release **only** when a `v*` tag is pushed (`startsWith(github.ref, 'refs/tags/')`).

### 6. Companion Plugin Note (`JavaScript Injector` on Jellyfin 10.11)
- When installing `n00bcodr`'s optional **JavaScript Injector** plugin on Jellyfin `10.11.11`, if the general catalog URL (`https://raw.githubusercontent.com/n00bcodr/jellyfin-plugins/main/manifest.json`) does not offer a `10.11` build, use the `10.11`-specific manifest URL:
  ```text
  https://raw.githubusercontent.com/n00bcodr/jellyfin-plugins/main/10.11/manifest.json
  ```

---

## Web-Script Risks Requiring Live Jellyfin `10.11.11` Verification

Static analysis, assembly reflection, and Node/Python contract suites cannot replace testing inside a live `jellyfin-web` `10.11.11` session. Verify the following on a test `10.11.11` server:
1. **Delegated shortcut playback (`FranchiseExplorerNativePlayback.play`):** Confirm `jellyfin-web` `10.11`'s `shortcuts.js` delegated click listener on `.itemsContainer` accepts the synthetic `.card.itemAction[data-action="play"|"resume"]` element (`data-id`, `data-serverid`, `data-type`, `data-mediatype="Video"`, `data-positionticks`) on Home and launches `PlaybackManager` directly.
2. **"My Media (small)" library strip mode:** If a user enables **My Media (small)** in Jellyfin `10.11` Home settings, `jellyfin-web` renders `.homeLibraryButton` buttons rather than `.card` posters; confirm whether tile cloning requires standard **My Media** card layout or custom theme CSS adjustments.
3. **Non-English UI locales:** since `0.8.9.1018`, `findMyMediaContainer()`, `homeAnchor()`, and `nativeRowSections()` fall back to Jellyfin Web markup (`data-type="CollectionFolder"` library cards, `data-collectiontype="boxsets"`, `data-monitor*="videoplayback"` rows) when the English headings are absent. This is covered by a mocked German Home test only; confirm on a live non-English `10.11` client.
4. **Post-playback route restoration & auto-next handoff:** Confirm how `jellyfin-web` `10.11` transitions out of the HTML5 video player (`#/video` -> `#/home.html` vs `#/details?id=...`) when an episode ends, and verify `consumeHomeQuickPlay()` + `restorePlaybackOrigin()` advance smoothly to the next TV episode or film without route loops.
5. **JavaScript Injector `10.11` `PluginInterface` load order:** Confirm the `10.11` build of `Jellyfin.Plugin.JavaScriptInjector` loads into `AssemblyLoadContext.All` within the 30-second startup retry window and injects the combined `franchise-timeline.js` + `franchise-my-media.js` payload before authentication (`requiresAuthentication: false`).
