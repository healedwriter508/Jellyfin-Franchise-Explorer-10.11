using System;
using System.IO;
using System.Linq;
using MediaBrowser.Common.Api;
using Jellyfin.Plugin.FranchiseExplorer.Web;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace Jellyfin.Plugin.FranchiseExplorer.Api;

/// <summary>
/// Read-only, user-facing, responsive franchise browsing page.
/// The HTML shell contains no private data; the catalog requires authentication.
/// Media names, descriptions and artwork are resolved through each viewer's
/// own Jellyfin API access, not copied from the administrator's link labels.
/// </summary>
[ApiController]
[Route("FranchiseExplorer")]
public sealed class FranchiseBrowseController : ControllerBase
{
    [HttpGet("Browse")]
    [AllowAnonymous]
    public IActionResult Browse()
    {
        // Serving a public HTML shell is safe: it contains no configuration,
        // user data or media metadata, and its API calls still require auth.
        if (NotModified()) return StatusCode(StatusCodes.Status304NotModified);
        var html = EmbeddedAssets.Text(EmbeddedAssets.BrowsePage);
        if (html is null) return NotFound("Franchise browser resource is missing.");
        Response.Headers["Referrer-Policy"] = "no-referrer";
        Response.Headers["X-Frame-Options"] = "SAMEORIGIN";
        return Content(html, "text/html; charset=utf-8");
    }

    [HttpGet("TimelineClient.js")]
    [AllowAnonymous]
    public IActionResult TimelineClient()
    {
        if (NotModified()) return StatusCode(StatusCodes.Status304NotModified);
        var script = EmbeddedAssets.Text(EmbeddedAssets.TimelineScript);
        if (script is null) return NotFound();
        return Content(script, "text/javascript; charset=utf-8");
    }

    /// <summary>
    /// Artwork for the optional My Media tile. Previously this 170 KB image was
    /// inlined as base64 into the injected script on every Jellyfin page load;
    /// serving it separately lets the browser cache it once per plugin version.
    /// </summary>
    [HttpGet("TileArt")]
    [AllowAnonymous]
    public IActionResult TileArt()
    {
        var bytes = EmbeddedAssets.Bytes(EmbeddedAssets.TileArt);
        if (bytes is null) return NotFound();
        Response.Headers["Cache-Control"] = "public, max-age=604800";
        Response.Headers["ETag"] = EmbeddedAssets.ETag;
        Response.Headers["X-Content-Type-Options"] = "nosniff";
        if (Request.Headers.IfNoneMatch.ToString() == EmbeddedAssets.ETag) return StatusCode(StatusCodes.Status304NotModified);
        return File(bytes, "image/webp");
    }

    // Embedded pages change only when the plugin DLL changes. Revalidate on
    // each load (so upgrades apply immediately) but answer with 304 when the
    // browser already holds this exact build.
    private bool NotModified()
    {
        Response.Headers["Cache-Control"] = "no-cache";
        Response.Headers["ETag"] = EmbeddedAssets.ETag;
        Response.Headers["X-Content-Type-Options"] = "nosniff";
        return Request.Headers.IfNoneMatch.ToString() == EmbeddedAssets.ETag;
    }

    [HttpGet("Catalog")]
    [Authorize]
    public IActionResult Catalog()
    {
        var plugin = Plugin.Instance;
        if (plugin is null) return StatusCode(503);
        var config = plugin.Configuration;
        Response.Headers["Cache-Control"] = "no-store";
        Response.Headers["X-Content-Type-Options"] = "nosniff";
        // Shared display metadata is intentionally visible to authenticated users.
        // Do not expose admin-defined media display labels, which may contain
        // titles that a particular user isn't allowed to browse.
        return Ok(new
        {
            version = EmbeddedAssets.Version,
            title = string.IsNullOrWhiteSpace(config.NavigationLabel) ? "Franchises" : config.NavigationLabel,
            nodes = config.Nodes.Select(n => new
            {
                id = n.Id,
                parentId = n.ParentId,
                name = n.Name,
                nodeType = n.NodeType,
                collectionId = n.CollectionId,
                overview = n.Overview,
                sortOrder = n.SortOrder,
                artwork = new
                {
                    primaryUrl = n.Artwork?.PrimaryUrl ?? "",
                    backdropUrl = n.Artwork?.BackdropUrl ?? "",
                    logoUrl = n.Artwork?.LogoUrl ?? "",
                    thumbUrl = n.Artwork?.ThumbUrl ?? "",
                    bannerUrl = n.Artwork?.BannerUrl ?? ""
                }
            }).ToArray(),
            rows = config.Rows.Select(r => new
            {
                id = r.Id,
                parentNodeId = r.ParentNodeId,
                name = r.Name,
                rowType = r.RowType,
                sortOrder = r.SortOrder,
                nodeIds = r.NodeIds,
                mediaLinkIds = r.MediaLinkIds,
                mediaOrder = r.MediaOrder,
                items = r.Items?.Select(i => new
                {
                    id = i.Id,
                    itemId = i.JellyfinItemId,
                    itemType = i.ItemType,
                    rangeMode = i.RangeMode,
                    startSeason = i.StartSeason,
                    endSeason = i.EndSeason,
                    startEpisode = i.StartEpisode,
                    endEpisode = i.EndEpisode
                }).ToArray()
            }).ToArray(),
            links = config.MediaLinks.Select(l => new
            {
                id = l.Id,
                nodeId = l.NodeId,
                itemId = l.JellyfinItemId,
                itemType = l.ItemType,
                rangeMode = l.RangeMode,
                startSeason = l.StartSeason,
                endSeason = l.EndSeason,
                startEpisode = l.StartEpisode,
                endEpisode = l.EndEpisode,
                viewingOrder = l.ViewingOrder,
                position = l.Position
            }).ToArray()
        });
    }
}
