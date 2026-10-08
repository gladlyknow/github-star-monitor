# GitHub Star Surge Monitor
Monitor GitHub repositories daily. Discover candidates via GitHub Search, collect repository metadata and README, and store daily JSON snapshots.
Never fabricate 24-hour Star gains. Only calculate gains when two timestamped samples are 20–28 hours apart. Explain that the resulting figure is a sample-to-sample difference, not an exact rolling 24-hour metric.
Summarize functionality from README and official documentation only; label unreviewed excerpts. Report Top 10 verified gainers and a separate watchlist without historical comparisons.
Run `python -m scripts.monitor` from the repository root. GitHub Actions uses the repository's built-in GITHUB_TOKEN; no personal access token is required.
