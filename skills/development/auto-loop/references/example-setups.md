# Example setups

Worked parameter sets, to make the setup interview concrete. Use them to show the user what a good
answer looks like — particularly for criteria and the progress metric, which are the two parameters
users most often leave too vague to loop on.

The pattern to notice across all three: the criteria are things a command decides, and the metric is
a single number that a round can move. When either is missing, the run has no way to tell progress
from motion, and the stagnation brake becomes meaningless.

## 1. Green again after a framework upgrade

The classic auto-loop shape: a large, mechanical failure surface where each round removes a few
failures and the finish line is unambiguous.

| Parameter | Value |
|---|---|
| Goal | "Get the test suite green again after upgrading to EF Core 10" |
| Criteria | C-1 `dotnet test` exits 0 · C-2 no test is skipped or removed relative to `main` |
| Verification | `dotnet build -warnaserror` and `dotnet test` |
| Metric | failing tests |
| Iteration budget | 15 |
| Mode | sub-agent |
| Scope limits | `Migrations/`, `*.Designer.cs`, CI configuration |
| Stagnation | 3 |

C-2 is the interesting one. Without it, the fastest route to a green suite is deleting the tests
that fail — and every round would look like progress. Whenever the goal is "make X pass", add the
criterion that forbids the degenerate solution.

## 2. Enable nullable reference types across a project

Slow, steady, and easy to measure — but the metric moves in a direction users often get backwards.

| Parameter | Value |
|---|---|
| Goal | "Enable nullable reference types in Acme.Core and fix every warning" |
| Criteria | C-1 `<Nullable>enable</Nullable>` in the csproj · C-2 build produces zero CS86xx warnings · C-3 no new `!` null-forgiving operators beyond the baseline count |
| Verification | `dotnet build -warnaserror:CS8600;CS8602;CS8618;CS8625` |
| Metric | CS86xx warning count |
| Iteration budget | 20 |
| Mode | sub-agent |
| Scope limits | generated code, `*.g.cs` |
| Stagnation | 4 |

C-3 again blocks the degenerate solution: silencing warnings with `!` satisfies C-2 perfectly while
making the code worse. The stagnation threshold is higher than the default because progress here is
genuinely lumpy — annotating one widely-used type can move the count by a hundred after three rounds
that moved nothing.

## 3. Eliminate a flaky test

A poor fit, included because recognising it matters. Look at what happens to the metric.

| Parameter | Value |
|---|---|
| Goal | "Stop OrderServiceTests.ConcurrentCheckout from failing intermittently" |
| Criteria | C-1 100 consecutive runs of the test pass |
| Verification | `for i in $(seq 100); do dotnet test --filter ConcurrentCheckout \|\| break; done` |
| Metric | consecutive passes before failure |
| Iteration budget | 8 |
| Mode | in-session |

The metric is noisy: a round can score 100 by luck and 3 by luck, so improvement is not evidence and
stagnation is not evidence either. Worse, the loop does not know *why* the test flakes, and a loop
that iterates without a hypothesis is guessing at speed.

Route this to `diagnose-bug` first. Once the cause is known, an auto-loop over "apply the fix and
prove it across the suite" is reasonable — but the diagnosis is not loop work. In general: if the
goal is *find out why*, it is not an auto-loop; if the goal is *grind through a known kind of change
until a number reaches zero*, it is.

## Sanity check before the go

Four questions that catch most bad setups while the user is still in the room:

1. **Could a lazy solution satisfy every criterion without achieving the goal?** If yes, add the
   criterion that forbids it — as C-2 and C-3 do above.
2. **Can one round plausibly move the metric?** If a single round cannot move it at all, the
   stagnation brake will fire on healthy work.
3. **Is the metric read from a command, or from a judgement?** Judgements drift; commands do not.
4. **Would the user recognise "done" from the criteria alone?** If not, the loop will stop somewhere
   the user did not want and report success.
