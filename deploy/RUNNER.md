# Isolated Judge0 deployment

Learner code is sent only to an operator-provided Judge0 CE endpoint. It is never executed by Flask, eval, exec, or a grading subprocess. This repository does not install a privileged sandbox onto the application host.

1. Deploy the maintained Judge0 CE distribution on a separate dedicated Linux host or VM using the official installation instructions: https://github.com/judge0/judge0 and https://ce.judge0.com/ . Review the release security advisories before selecting a release.
2. Isolate that host from application databases, Redis, cloud metadata, credentials, host mounts, and the public application network. Only the application may reach the Judge0 API. Enforce outbound network denial at the host/network layer as well as the API setting. Never rely solely on a learner-supplied configuration flag.
3. Configure Judge0 maximum CPU, wall time, memory, process/thread, output file limits, and disable network access. Application requests additionally set CPU 2s, wall 5s, memory 128000 KB, 16 processes/threads, and file size 64 KB. Runner administrators must ensure these limits cannot be bypassed and set bounded queue capacity.
4. Set JUDGE0_URL and optionally JUDGE0_TOKEN in the application environment. Do not use a public shared sandbox for private hidden tests without an explicit operator decision.
5. Query the installed `/languages` endpoint. Select the actual installed runtime ID, not a hardcoded example. The curriculum targets Python 3.14; install a corresponding runtime or document and review compatibility before changing the question's runtime requirement.
6. Run `PYTHONPATH=. .venv/bin/python scripts/configure_runner.py --language-id ID --version 'Python 3.14' --name 'Isolated Python' --course python-foundations`.
7. Open Admin → Questions. Review the coding draft and set its state to approved. This invokes its reference solution against every test. Approval fails if the runner is unavailable or any reference test fails.
8. Before allowing real users, verify alternative correct solutions, an infinite loop, excessive allocations, fork attempts, network calls, oversized output, and host-file access. These live isolation tests have NOT been run in the delivered local build because no Judge0 service was configured.

Samples run only visible tests. Grading runs every weighted test independently. Hidden input and expected output never appear in active-attempt responses. An infrastructure failure leaves the submitted code in grading state for the periodic worker to retry.

For React or other framework environments, prepare an operator-managed build/test environment separately. A plain language ID does not imply framework support.
