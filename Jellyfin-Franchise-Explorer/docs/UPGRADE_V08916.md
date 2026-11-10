# Franchise Explorer v0.8.9.16 — Performance, tidy-up, and a Jellyfin-native look

This experimental source release targets Jellyfin 12.2. Use GitHub Actions to build a compiled release; the source ZIP itself is not a plugin installation archive. Timeline history, configuration and uploaded artwork are unchanged by this update.

## What changed

- **Less load on the Jellyfin server.** Playback-progress events only touch timelines that are actually armed or playing; everyone else's playback skips disk access. Routine playback log lines are now Debug level.
- **Less work in every browser tab.** The Home integration is idle outside Jellyfin Home, the injected script no longer carries an inline base64 image, auto-next polls a single timeline row, and artwork is cached.
- **A Jellyfin-native look.** Jellyfin's accent colour, greys, font and control shapes are used throughout the Franchises browser, Home card, menus, dialogs and settings editor.
- **Works with non-English Jellyfin.** The Home tile and Continue Your Franchises no longer depend on English headings such as "My Media".
- The Injector script ID is now `jellyfin-franchise-explorer-my-media-v08916`. The plugin retires the v0.8.9.15 script after registering the new one.

## Publish and check

1. Back up your Franchise Explorer settings, push the source and run **Publish experimental release** for `0.8.9.16`.
2. Install the compiled release, restart Jellyfin and hard-refresh Jellyfin Web.
3. In JS Injector confirm only the v0.8.9.16 Franchise Explorer script is enabled. `window.__franchiseExplorerUiVersion` should report `0.8.9.16`.
4. On Jellyfin Home, check the Franchises tile artwork loads (it now comes from `/FranchiseExplorer/TileArt`) and that Continue Your Franchises aligns with the native rows.
5. Resume a franchise from Home and let an episode finish: the next entry should still start automatically.
6. Optional: with Debug logging disabled, confirm the Jellyfin log no longer gets a Franchise Explorer line for every playback stop.

Static contracts and offline simulations cannot prove compatibility with your installed Jellyfin Web client. Please report live playback issues.
