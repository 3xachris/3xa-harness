# Order: demo verification (demo_20260807)   [FROZEN 2026-08-07 by maintainer]

**One sentence:** Add a small, independently tested status endpoint.

**Known facts**
- The endpoint contract is recorded in the test output at `.verification-demo/evidence/verification.txt`.

**Materials**
- Allowed: repository code and the standard test runner, MIT, checked 2026-08-07

**Build spec**
- Status response = `200 OK`, pinned at `evidence/verification.txt#status-check`
- Artifacts folder: `.verification-demo`

**Budget fuse:** 1 test run. On reaching it: stop and return what exists.

**Acceptance**
- [ ] AC-1: The endpoint returns `200 OK` | evidence: .verification-demo/evidence/verification.txt
- [ ] AC-2: The reviewed batch is approved by a named reviewer | evidence: .verification-demo/gate/review-01/approved.txt

**Non-goals**
- No changes to authentication or deployment configuration
