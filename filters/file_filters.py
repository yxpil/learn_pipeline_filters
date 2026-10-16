"""File-processing filters. Each does ONE thing, reads/writes the shared context dict."""
from framework.pipeline import StopPipeline


def validate(ctx):
    """Check file type and size."""
    name = ctx.get("filename", "")
    size = ctx.get("size", 0)
    if not name.lower().endswith((".png", ".jpg", ".jpeg")):
        raise StopPipeline(f"unsupported file type: {name}")
    if size > 10_000_000:
        raise StopPipeline(f"file too large: {size} bytes")
    ctx["validated"] = True
    return ctx
validate.name = "validate"


def virus_scan(ctx):
    """Simulated AV scan; flags a known bad filename."""
    if "evil" in ctx.get("filename", ""):
        raise StopPipeline("virus detected")
    ctx["scanned"] = True
    return ctx
virus_scan.name = "virus_scan"


def watermark(ctx):
    """Optional filter: stamp a watermark onto the image."""
    ctx["watermarked"] = True
    return ctx
watermark.name = "watermark"


def thumbnail(ctx):
    """Simulated thumbnail generation."""
    ctx["thumbnail"] = f"thumb_{ctx.get('filename','')}"
    return ctx
thumbnail.name = "thumbnail"


def persist(ctx):
    """Simulated DB/storage write."""
    ctx["saved_to"] = f"s3://bucket/{ctx.get('filename','')}"
    return ctx
persist.name = "persist"


def notify(ctx):
    """Simulated notification to the owner."""
    ctx["notified"] = f"owner of {ctx.get('filename','')}"
    return ctx
notify.name = "notify"
