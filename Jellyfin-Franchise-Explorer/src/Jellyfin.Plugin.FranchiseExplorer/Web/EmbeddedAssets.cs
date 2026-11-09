using System;
using System.Collections.Concurrent;
using System.IO;

namespace Jellyfin.Plugin.FranchiseExplorer.Web;

/// <summary>
/// Reads embedded web resources once per process. They never change while a
/// given plugin DLL is loaded, so re-reading the manifest stream on every
/// request (or on every registration attempt) is wasted work.
/// </summary>
internal static class EmbeddedAssets
{
    public const string BrowsePage = "Jellyfin.Plugin.FranchiseExplorer.Configuration.browsePage.html";
    public const string TimelineScript = "Jellyfin.Plugin.FranchiseExplorer.Web.franchise-timeline.js";
    public const string HomeScript = "Jellyfin.Plugin.FranchiseExplorer.Web.franchise-my-media.js";
    public const string TileArt = "Jellyfin.Plugin.FranchiseExplorer.Web.franchise-tile-backdrop.webp";

    private static readonly ConcurrentDictionary<string, byte[]?> Cache = new(StringComparer.Ordinal);

    /// <summary>Gets the plugin version, used for cache-busting and ETags.</summary>
    public static string Version { get; } =
        typeof(Plugin).Assembly.GetName().Version?.ToString() ?? "0.0.0.0";

    /// <summary>Gets a strong ETag for any embedded asset of this build.</summary>
    public static string ETag { get; } = "\"fe-" + Version + "\"";

    public static byte[]? Bytes(string resource) => Cache.GetOrAdd(resource, static name =>
    {
        using var stream = typeof(Plugin).Assembly.GetManifestResourceStream(name);
        if (stream is null) return null;
        using var buffer = new MemoryStream();
        stream.CopyTo(buffer);
        return buffer.ToArray();
    });

    public static string? Text(string resource)
    {
        var bytes = Bytes(resource);
        return bytes is null ? null : System.Text.Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF');
    }
}
