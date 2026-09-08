# Isolation rules for parallel with_skill / without_skill runs

Verified for iteration-3: each run gets its own full copy of the fixture (distinct inodes,
own .git object store, no alternates), so file edits, checkouts and temporary changes made by
one agent are invisible to the other.

Shared resources that are NOT isolated by the copy, and how they are handled:

| Resource | Risk | Rule |
|---|---|---|
| `/tmp` | two agents pick the same filename and read each other's data | Never point agents at `/tmp`. Each run gets `<run>/scratch/`; the prompt names it as the only place for generated files. |
| network ports | a hardcoded port makes the second run fail or connect to the first | Prompt requires ephemeral ports (`listen(0)`) for any local server. |
| package caches (npm, NuGet, Gradle) | concurrent writes on first restore | Dependencies are installed while building the fixture; prompts forbid installs and network use. |
| build server daemons (dotnet, gradle) | shared background processes | Projects are in separate directories, so build outputs stay separate. |

Graders inherit the same rules: a grader re-running an executor's scripts must run them inside
that run's own tree and scratch dir.
