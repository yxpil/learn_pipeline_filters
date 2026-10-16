"""Demo: build a file-processing pipeline and show pluggability, reorder, early stop."""
from framework.pipeline import Pipeline
from filters import file_filters as F


def show(title, ctx):
    print(f"\n--- {title} ---")
    print("pipeline logs:")
    for line in ctx["_logs"]:
        print(" ", line)
    extras = {k: v for k, v in ctx.items() if k not in ("_logs",) and not k.startswith("_")}
    print("context after run:", extras)


def main():
    # Base pipeline
    p = Pipeline("upload-pipeline")
    p.use(F.validate).use(F.virus_scan).use(F.thumbnail).use(F.persist).use(F.notify)
    print("base pipeline:", p.describe())

    # Case 1: happy path
    show("Case 1: normal upload", p.run({"filename": "photo.png", "size": 2_000_000}))

    # Case 2: plug in a new filter (watermark) between virus_scan and thumbnail
    p2 = Pipeline("upload-pipeline-v2")
    p2.use(F.validate).use(F.virus_scan).use(F.thumbnail).use(F.persist).use(F.notify)
    p2.insert_after("virus_scan", F.watermark)
    print("\nplugged-in pipeline:", p2.describe())
    show("Case 2: with watermark inserted", p2.run({"filename": "holiday.jpg", "size": 1_000_000}))

    # Case 3: early stop — bad file type, later filters never run
    show("Case 3: unsupported type stops early", p.run({"filename": "malware.exe", "size": 100}))

    # Case 4: early stop — virus detected
    show("Case 4: virus detected stops early", p.run({"filename": "evil.png", "size": 500}))

    # Case 5: reorder — put notify before persist (weird but shows reorder ability)
    p3 = Pipeline("reordered")
    p3.use(F.validate).use(F.virus_scan).use(F.notify).use(F.thumbnail).use(F.persist)
    print("\nreordered pipeline:", p3.describe())
    show("Case 5: reordered run", p3.run({"filename": "cat.png", "size": 300_000}))

    print("\n== all cases done ==")


if __name__ == "__main__":
    main()
