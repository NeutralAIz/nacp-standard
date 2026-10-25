# Agent instructions

Release history: the GitHub Releases page (one Release per train, SemVer tags). Spec changes go in CHANGELOG.md in the same topic.

<!-- release-train:begin -->
## Release train: how work reaches `main`

Never open or merge a PR into `main` (or `release/next`). One bot-owned PR (`release/next` -> `main`) ships
everything; a guard closes any other PR into those branches within seconds.

1. Work on a topic branch `t/<agent>/<ticket>-<slug>` (e.g. `t/flores/q-2301-recency`).
   End every commit on a topic branch with a `Ticket: <ticket>` trailer as its LAST line (otherwise the controller rejects the landing: `E_BAD_COMMIT_MESSAGE`).
2. `train claim <ticket>` (e.g. `Q-2301`). One claim per ticket; it is bound to your GitHub account.
3. `train land <claim-id> <topic-ref>` queues the topic. The controller rebases it into the next release and
   runs the gate. You do not merge anything.
4. `train status` shows your claims and the next action. `train hold <claim-id> <reason>` / `train unhold
   <claim-id>` pause landed work (a hold blocks the whole cut: keep it short). `train release <claim-id>`
   gives a claim up.

No CLI? Post the same commands as a `/train <cmd> ...` comment on the pinned `train-control` issue.
Answers arrive on the controller's next poll (up to about 5 minutes); do not retry.

**Stopping the train for this repo.** Ask a train-maintainer to pause it.
`gh variable set` replaces the whole value; append to the existing list (comma or whitespace separated) by reading it first:

```sh
paused_repos=$(gh variable list -R NeutralAIz/release-train --json name,value --jq '.[] | select(.name == "TRAIN_PAUSED_REPOS") | .value') &&
gh variable set TRAIN_PAUSED_REPOS --body "${paused_repos:+$paused_repos,}NeutralAIz/nacp-standard" -R NeutralAIz/release-train
```

A failed read prevents the write. Coordinate edits with other maintainers: this read/modify/write is not atomic.
To unpause, remove this repo from that variable. A pause skips future controller passes, including manual runs; an active pass may finish.
To stop the whole self-dispatch chain, set repo variable `TRAIN_SELF_DISPATCH=off` on `NeutralAIz/release-train`;
cron and manual passes still run (see release-train's `docs/HEARTBEAT.md`).
To leave the train entirely, remove this repo from `allowlist.json` via PR and disable this repo's train rulesets.
<!-- release-train:end -->
