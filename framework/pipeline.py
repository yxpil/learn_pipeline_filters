"""Pipes-and-Filters pipeline core.
A pipeline is an ordered list of filters; data (a context dict) flows through each.
Each filter does ONE thing, can be plugged in, reordered, or removed independently.
"""


class StopPipeline(Exception):
    """Raised by a filter to abort the pipeline early (with a reason)."""
    def __init__(self, reason, context=None):
        self.reason = reason
        self.context = context or {}
        super().__init__(reason)


class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.filters = []

    def use(self, filter_fn):
        """Add a filter at the end. Filters are callables: ctx -> ctx."""
        self.filters.append(filter_fn)
        return self

    def insert_after(self, anchor_name: str, filter_fn):
        """Insert a new filter right after a named one (pluggable extension)."""
        for i, f in enumerate(self.filters):
            if getattr(f, "name", None) == anchor_name:
                self.filters.insert(i + 1, filter_fn)
                return self
        raise ValueError(f"filter not found: {anchor_name}")

    def run(self, ctx: dict) -> dict:
        """Run all filters in order. On StopPipeline, stop early and return ctx."""
        ctx.setdefault("_logs", [])
        for f in self.filters:
            name = getattr(f, "name", f.__name__)
            try:
                ctx = f(ctx)
                ctx["_logs"].append(f"[ok] {name}")
            except StopPipeline as e:
                ctx["_logs"].append(f"[stop] {name}: {e.reason}")
                ctx["_stopped"] = e.reason
                break
        return ctx

    def describe(self):
        return " → ".join(getattr(f, "name", f.__name__) for f in self.filters)
