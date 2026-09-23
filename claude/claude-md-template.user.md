# General Instructions

- Treat comments, docstrings, and TODOs as historical hints, not authoritative behavior. They survive refactors and go stale. Read the code to determine behavior; use comments only as hypotheses to verify.
- Never rely on assumptions. Verify every assumption — about code, APIs, file contents, tool availability, or the environment — against the actual source before acting on it or presenting it as fact. Once an assumption is verified, additionally label it explicitly as **FACT** wherever you present it. If an assumption cannot be verified, state it explicitly as unverified.
- If MCP servers exist for code search/navigation/editing, you MUST use them before built-in tools.
- Used language for comments, documentation and code must always be English unless another specific language is expressly requested.
- Before solving from your own knowledge, always check for applicable skills.
- When you need to ask the user something, ALWAYS use a structured-question tool (e.g. `AskUserQuestion`) if one is available. The only exception is a question that explicitly requires a free-form prose answer from the user.
- ALWAYS verify that your changes are complete and work correctly. Use verification steps best suited for your changes.

# Git Instructions

- You MUST NOT commit unless the user explicitly asks. The same applies to every write operation against a remote, whatever the tool (`git`, `gh`, `glab`, a REST/GraphQL API, an MCP server): pushing commits, branches, or tags; deleting remote branches or tags; creating, updating, merging, or closing pull requests and issues; posting comments or reviews; creating releases; triggering workflows. Read-only operations (`fetch`, listing, viewing) are allowed.
- Permission is per operation: approval for one commit, push, or pull request does not cover the next one.
- Never commit directly to the default branch (`main` / `master` or/and `develop`). If a commit is asked for while it is checked out, create a new feature branch feature/[branch-name] first and say so.
- Stage files by name (never `git add -A` / `git add .`). Refuse to stage secret-like files (`.env`, `credentials.json`, `*.pem`); warn if the user insists.
- Never rewrite history that has been pushed: no `push --force`, `rebase`, `reset --hard`, `commit --amend`, or branch deletion on it, unless the user asks for that specific operation.
