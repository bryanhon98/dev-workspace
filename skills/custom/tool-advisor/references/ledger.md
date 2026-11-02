# Local ledger command contract

Run the bundled script with Python, passing the target project explicitly:

```sh
python3 /path/to/tool-advisor/scripts/ledger.py --project /path/to/project init --goal "Research a suitable document workflow"
python3 /path/to/tool-advisor/scripts/ledger.py --project /path/to/project status
```

The checkout also provides `python3 scripts/advisor.py` as an entrypoint. Run `--help` for flags. State lives under the project's ignored `.tool-advisor/` directory. Only the coordinator writes it. A lock protects against simultaneous updates; inspect a stale lock and the active process before removing it manually.

The helper reads the explicit JSON inputs and existing state, and writes its state, lock and ignore file within that project directory. It launches no subprocesses, contacts no service and grants no host tool permissions. Normal host permissions still govern running it. These statements describe intended scope, not a sandbox around an arbitrary process.

Use UTF-8 JSON files for structured inputs. A brief has this shape:

```json
{
  "goal": "Choose a document extraction workflow",
  "deliverables": ["Comparison with a tested recommendation"],
  "constraints": ["Use public sample documents"],
  "success_criteria": ["Preserve tables and cite extraction gaps"],
  "open_questions": [],
  "assumptions": []
}
```

A proposal has `roles` and `tasks` arrays. Each role has `id`, `job`, `component`, `kind` (skill/agent/tool/manual), `source`, `revision`, `availability` (ready/needs-install/unverified), `reason` and `alternatives` (string array). Each task has `id`, `title`, `role`, `depends_on` (task-ID array) and `acceptance` (string array). Use `local` and `not-applicable` for an honest manual role's source/revision. IDs use letters, numbers, dots, underscores or hyphens.

Commands, in order:

1. `brief --file brief.json` records the interview result.
2. `propose --file proposal.json` validates the plan and returns its digest. Resolve open questions first.
3. `confirm --digest DIGEST --evidence "User's actual answer and context"` records confirmation of the displayed proposal. The CLI records an assertion by its caller; it cannot authenticate the user. Do this only after the real answer arrives.
4. `ready --role ROLE --evidence "Actual capability checks"` records readiness. Even a proposed ready role needs evidence.
5. `start --task TASK --actor ACTOR` claims ready work after its dependencies finish.
6. `update --task TASK --status review --evidence "Output and checks"` records a worker result; use `blocked` with the reason when needed, and `done` only after verification.
7. `status` resumes from persisted state; `complete` checks that all agreed tasks are done.

Changing the brief or proposal invalidates prior confirmation. Preserve old plans and outcomes; do not overwrite history to make a new plan look approved. The CLI has no model-launching or external publishing side effects. Real-world acceptance, permission and evidence still require the coordinating assistant's judgment.
