# Week 4 assignment: context assembly diagnosis

You have 20 minutes to work and 10 minutes to show. Everything you need is in this
folder and in `../practice/context-lab/`.

## The task

One held-out scenario, `GRADED-flaky-cache`, is set up with a context defect. You
assemble its context, run it once, name the failure, predict whether your chosen
fix will work, apply one assembly move, run it again, and record what changed
against your prediction.

## Work (20 minutes)

Run everything from `../practice/context-lab/`.

1. Open `scenario-brief.md` (in this folder) and `context-diagnosis.md`. Put your
   name and the date at the top of `context-diagnosis.md`.

2. Inspect the baseline context:
   ```
   python3 context_lab.py GRADED-flaky-cache --show-context
   ```
   Record the per-block list and the total token estimate in
   `context-diagnosis.md`.

3. Run the baseline once against a live model:
   ```
   python3 context_lab.py GRADED-flaky-cache
   ```
   Paste the output and the `[provenance]` line into `context-diagnosis.md`.

4. Diagnose one failure. Name it with the correct Week 4 term; no list is given
   here, use your lecture notes. Quote the exact detail in the output that shows
   it.

5. Before you touch anything, predict in one sentence: will your planned move
   fix the output, partially fix it, or leave it unchanged, and why (tie it to
   your diagnosis)?

6. Apply exactly one assembly move from this session's practice and record the
   exact command or file change. Forgot the exact flag?
   ```
   python3 context_lab.py --help
   ```

7. Run it again the same way. Record the new output, the new `[provenance]` line,
   and the new `--show-context` total.

8. In `context-diagnosis.md`: state the result as improved, no change, or worse,
   whether it matched your prediction from step 5, with one concrete
   before-and-after detail, and report the token-count change
   and why it moved (down for Select or Compress; up slightly for a trust flip,
   which adds an untrusted-handling rule to the trusted layer; roughly flat for a
   forget or update).

9. Fill in the AI-use disclosure block.

10. Upload `context-diagnosis.md` to the Week 4 assignment in Canvas.

## Show (10 minutes)

Display `context-diagnosis.md`. Present: the failure named in Week 4 vocabulary
with its quoted evidence, the one assembly move you applied with your prediction
and whether it held, the before-and-after output detail, and the before-and-after
token totals.

## Deliverable

`context-diagnosis.md`, uploaded to the Week 4 Canvas assignment.

Course-wide rules on tooling, disclosure, and ownership are on the Canvas course
information page.
