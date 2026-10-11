# Python foundations question bank

The seed contains 76 approved objective questions and one existing draft
coding exercise. This update adds 29 concept, 29 output, and six error
questions. Each of the 29 syllabus topics has a concept and output question.
Correct option positions vary; explanations describe the underlying behavior.

Run `flask --app run seed` after upgrading an existing installation. Stable
bank fingerprints identify additions. The seeder leaves existing content,
review states, attempts, and certificates unchanged. Topics are matched by
exact title within the seeded course, not by hard-coded database IDs. If a
required topic was renamed or duplicated before the bank was installed,
seeding reports the mismatch rather than attaching questions to the wrong
lesson. Restore the intended syllabus title or resolve the mapping manually.

## Verification

Questions were authored and reviewed with AI assistance. Schema validation
checks four unique choices and one valid answer index. CI executes the 29
output examples and six intentional error examples in separate Python
processes with timeouts. These are checked-in programs, not learner code.
The examples use Python's standard library and the project's Flask dependency;
they do not need network services, NumPy, pandas, or model credentials.

Integration tests assemble and fully grade finals covering all 29 topics.
Tests also exercise upgrading an old seed and reseeding without resetting an
administrator's edits. Concept explanations were checked against the sources
below; executable checks do not substitute for future editorial review.

## Sources and scope

These are original questions, not copied exam material. Reference sources:

- [Python 3.14 tutorial](https://docs.python.org/3.14/tutorial/)
- [Python sqlite3 reference](https://docs.python.org/3.14/library/sqlite3.html)
- [Python asyncio tasks](https://docs.python.org/3.14/library/asyncio-task.html)
- [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/)
- [NumPy beginner guide](https://numpy.org/doc/stable/user/absolute_beginners.html)
- [pandas table introduction](https://pandas.pydata.org/docs/getting_started/intro_tutorials/01_table_oriented.html)
- [scikit-learn data-leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html)

Data analysis, ML, HTTP, and RAG topics remain introductions. Their questions
assess basic concepts or small illustrative calculations. They do not
establish professional certification or specialist proficiency.

A full-course final needs at least 29 questions. Concept-only and output-only
finals are available; mixed concept/output/error finals are supported. The
error bank alone is not comprehensive. Coding content stays draft until its
runner and review requirements are met. Course rules and the 30-question
maximum are unchanged.
