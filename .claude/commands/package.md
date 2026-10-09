---
description: Validate and package the skill for distribution
---

1. Run `python3 scripts/ste_lint.py skills/ste-explain/SKILL.md` — the skill
   must obey its own rules. Fix violations before packaging.
2. Run `python3 scripts/package_skill.py` (it validates frontmatter first
   and refuses to package on failure).
3. Confirm `dist/ste-explain.zip` exists and list its contents.
4. Remind me of the release checklist: tag the version, run
   `scripts/build_release.py <tag>`, push with
   `git push origin main <tag> release`, attach the zip with
   `gh release create <tag> dist/ste-explain.zip --verify-tag`, test all
   three install routes per specs/success-criteria.md.
