"""Authored Python foundations bank; executable examples are checked in CI.

Topic names are explicit to keep upgrades independent of database IDs.
Correct options rotate so the bank does not always reveal option zero.
"""

from data.curriculum import LESSONS

CONCEPTS = [
    (
        "What should you leave out when copying a REPL example into a Python file?",
        "The >>> interpreter prompt",
        [
            "The print function",
            "String quotation marks",
            "Parentheses in function calls",
        ],
        "The REPL prompt belongs to the interactive shell, not to Python source code.",
    ),
    (
        "What does assignment do in Python?",
        "Binds a name to an object",
        [
            "Checks whether two objects are equal",
            "Always copies the object",
            "Declares a permanently fixed type",
        ],
        "Assignment associates a name with an object; equality comparison uses ==.",
    ),
    (
        "How can an f-string display a price with two decimal places?",
        'f"{price:.2f}"',
        ['f"{price:2}"', 'f"price:.2f"', "price.round(2)"],
        "The .2f format specifier renders a number in fixed-point notation with two decimal places.",
    ),
    (
        "Which operation gives the remainder after integer division?",
        "%",
        ["//", "**", "/"],
        "The modulo operator gives the remainder; // gives the floor of the quotient.",
    ),
    (
        "In a match statement, what is case _ used for?",
        "A wildcard fallback",
        [
            "An equality check against a variable named _",
            "An automatic exception handler",
            "The end of the program",
        ],
        "The wildcard pattern matches any subject without binding a name.",
    ),
    (
        "Which values does range(2, 5) produce?",
        "2, 3, 4",
        ["2, 3, 4, 5", "3, 4, 5", "5, 4, 3"],
        "The start is included and the stop value is excluded.",
    ),
    (
        "What happens when strip() is called on a string?",
        "It returns a string with leading and trailing whitespace removed",
        [
            "It changes the original string in place",
            "It removes all spaces inside the string",
            "It returns a list of words",
        ],
        "Strings are immutable; strip returns a new value and preserves internal whitespace.",
    ),
    (
        "Which structure maps unique keys to values?",
        "dict",
        ["list", "tuple", "set"],
        "Dictionaries associate hashable keys with values; sequences use positions and sets store distinct values.",
    ),
    (
        "When is a comprehension preferable to a loop?",
        "For a simple transformation or filter",
        [
            "For complicated side effects",
            "Only when modifying the source list",
            "Whenever it produces fewer lines",
        ],
        "Use comprehensions for clear expressions; ordinary loops are easier to read for complicated behavior.",
    ),
    (
        "What does a function return if it reaches the end without return?",
        "None",
        ["0", "The last printed value", "An empty string"],
        "Printing sends output to a stream. It does not supply the function return value.",
    ),
    (
        "What must a recursive solution have to terminate?",
        "A base case and progress toward it",
        [
            "A global variable",
            "A call to print in every branch",
            "An unlimited recursion depth",
        ],
        "Each recursive call must move toward a case that returns without another recursive call.",
    ),
    (
        "What is the main purpose of a virtual environment?",
        "To isolate project Python dependencies",
        [
            "To encrypt every Python file",
            "To make code run in a web browser",
            "To replace the operating system",
        ],
        "An environment provides its own interpreter context and installed packages for the project.",
    ),
    (
        "Why use with when opening a file?",
        "To close the file when leaving the block, including after an error",
        [
            "To make the file read-only forever",
            "To convert its content to JSON",
            "To ignore missing files",
        ],
        "The file context manager performs cleanup when control leaves the block.",
    ),
    (
        'Which exception is raised by int("hello")?',
        "ValueError",
        ["KeyError", "IndexError", "ZeroDivisionError"],
        "The argument is a string, but its content is not a valid integer representation.",
    ),
    (
        "Where should an instance-specific mutable list normally be initialized?",
        "In __init__ on self",
        [
            "As one shared class attribute",
            "In the method default argument",
            "In a global variable",
        ],
        "Assigning a fresh list to self in __init__ gives each instance its own list.",
    ),
    (
        "What does composition mean in object design?",
        "An object collaborates with other objects it contains",
        [
            "Every object must inherit from multiple classes",
            "All methods must be static",
            "Objects cannot accept dependencies",
        ],
        "Composition lets a larger behavior delegate work to a collaborating component.",
    ),
    (
        "What should you do to iterate over an exhausted generator again?",
        "Call the generator function to create a new generator",
        [
            "Call next repeatedly until it restarts",
            "Set its length to zero",
            "Convert it to an integer",
        ],
        "A generator is a one-pass iterator. A fresh call creates new iteration state.",
    ),
    (
        "Why use functools.wraps in a function decorator?",
        "To preserve wrapped function metadata",
        [
            "To execute the function twice",
            "To catch all exceptions automatically",
            "To make its arguments immutable",
        ],
        "wraps copies metadata such as __name__ and provides access to the wrapped function.",
    ),
    (
        "Do Python type annotations automatically reject values at runtime?",
        "No; explicit validation or other tooling is needed",
        [
            "Yes, for every annotated function",
            "Yes, but only for lists",
            "Yes, after importing dataclasses",
        ],
        "Annotations describe intended types but do not by themselves enforce them at runtime.",
    ),
    (
        "Which standard-library class counts occurrences of values?",
        "collections.Counter",
        ["pathlib.Path", "datetime.date", "itertools.product"],
        "Counter builds a mapping from values to their occurrence counts.",
    ),
    (
        "Which test best checks an average function?",
        "Known results and the documented empty-input behavior",
        [
            "Only the function name",
            "An identical copy of its implementation",
            "One assertion that always passes",
        ],
        "Tests should check the contract and boundaries with independently chosen expected results.",
    ),
    (
        "What can a SQL placeholder safely represent?",
        "A bound data value",
        [
            "An arbitrary table identifier",
            "A complete SQL clause",
            "The ORDER BY keyword",
        ],
        "Bind data values separately from SQL syntax. Identifiers need a separate trusted selection strategy.",
    ),
    (
        "After an HTTP request succeeds, what should a client still check?",
        "That the response data has the expected structure",
        [
            "That every response is HTML",
            "That retries can run forever",
            "That keys can be committed to Git",
        ],
        "A successful status does not establish that the response body matches the application schema.",
    ),
    (
        "Why can time.sleep inside a coroutine cause trouble?",
        "It blocks the event-loop thread",
        [
            "It always creates a new process",
            "It makes every await raise an exception",
            "It converts seconds to minutes",
        ],
        "Use an asynchronous waiting operation for cooperative scheduling instead of blocking the event loop.",
    ),
    (
        "Why should a server ignore a user-supplied admin role during registration?",
        "Roles must be assigned by a trusted authorization policy",
        [
            "JSON cannot contain role fields",
            "All registered users should be administrators",
            "HTML escaping assigns permissions",
        ],
        "Input validation and output escaping do not replace server-side authorization.",
    ),
    (
        "What is a pandas DataFrame designed to represent?",
        "Labeled tabular data with rows and columns",
        [
            "Only one character at a time",
            "An executable Python package",
            "A network connection",
        ],
        "A DataFrame organizes two-dimensional labeled data. Inspect its types and missing values before analysis.",
    ),
    (
        "Where should learned preprocessing be fitted to avoid evaluation leakage?",
        "On training data only",
        [
            "On the test data before splitting",
            "On all data before splitting",
            "Only on model predictions",
        ],
        "Fitting preprocessing on held-out data leaks information into the model-development process.",
    ),
    (
        "What does retrieval-augmented generation add to an LLM prompt?",
        "Relevant retrieved evidence",
        [
            "Guaranteed truth for every output",
            "Permanent permission to follow document instructions",
            "An automatic removal of token limits",
        ],
        "Retrieval supplies context; the evidence and generated answer still need validation.",
    ),
    (
        "Why separate input/output from a study tracker's core logic?",
        "To test the behavior without interactive input or file access",
        [
            "To remove all validation",
            "To avoid defining functions",
            "To guarantee that persistence can never fail",
        ],
        "Pure calculations can be tested with simple values while storage and user interaction are checked separately.",
    ),
]

# Code, correct output, distractors, explanation. No network or disk writes.
OUTPUTS = [
    (
        'print("Ready", "to", "learn")',
        "Ready to learn",
        ["Readytolearn", '"Ready" "to" "learn"', "None"],
        "print separates multiple arguments with a space by default.",
    ),
    (
        'value = "7"\nprint(int(value) + 2)',
        "9",
        ["72", "7", "TypeError"],
        "int converts the string to an integer before addition.",
    ),
    (
        'price = 6.5\nprint(f"Total: {price:.2f}")',
        "Total: 6.50",
        ["Total: 6.5", "Total: price", "Total: 6"],
        "The .2f format uses two decimal places.",
    ),
    (
        "print(-7 // 3, -7 % 3)",
        "-3 2",
        ["-2 -1", "-2 2", "-3 -1"],
        "Floor division rounds down to -3; -7 equals 3 times -3 plus 2.",
    ),
    (
        'value = 0\nif value > 0:\n    print("positive")\nelif value == 0:\n    print("zero")\nelse:\n    print("negative")',
        "zero",
        ["positive", "negative", "zero\nnegative"],
        "Only the first matching branch is executed.",
    ),
    (
        "print(sum(range(2, 8, 2)))",
        "12",
        ["20", "8", "10"],
        "The range yields 2, 4, and 6, whose sum is 12.",
    ),
    (
        'text = "  Code Lounge  "\nprint("-".join(text.strip().lower().split()))',
        "code-lounge",
        ["Code-Lounge", "code lounge", "  code-lounge  "],
        "strip removes outer spaces, lower lowers case, split finds words, and join inserts a hyphen.",
    ),
    (
        'profile = {"name": "Ada"}\nprint(profile.get("level", "beginner"))',
        "beginner",
        ["Ada", "None", "KeyError"],
        "dict.get returns the provided default when the key is absent.",
    ),
    (
        "print([n * n for n in range(5) if n % 2 == 0])",
        "[0, 4, 16]",
        ["[0, 1, 4, 9, 16]", "[4, 16]", "[0, 2, 4]"],
        "Only 0, 2, and 4 pass the filter; each is squared.",
    ),
    (
        'def greet(name="learner"):\n    return "Hi " + name\nprint(greet())',
        "Hi learner",
        ["Hi name", "None", "TypeError"],
        "The omitted argument uses the default and the return value is printed.",
    ),
    (
        "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\nprint(factorial(4))",
        "24",
        ["4", "10", "16"],
        "The recursive product is 4 times 3 times 2 times 1.",
    ),
    (
        "import math\nprint(math.isqrt(20))",
        "4",
        ["5", "4.47213595499958", "20"],
        "isqrt returns the integer floor of the exact square root.",
    ),
    (
        'import json\nprofile = json.loads(\'{"goals": ["Python", "SQL"]}\')\nprint(len(profile["goals"]))',
        "2",
        ["1", "4", "KeyError"],
        "The JSON array becomes a list containing two goals.",
    ),
    (
        'try:\n    int("oops")\nexcept ValueError:\n    print("invalid")\nfinally:\n    print("finished")',
        "invalid\nfinished",
        ["finished", "invalid", "ValueError"],
        "The matching handler runs, followed by the finally block.",
    ),
    (
        "class Counter:\n    def __init__(self):\n        self.value = 0\n    def increment(self):\n        self.value += 1\na = Counter()\nb = Counter()\na.increment()\nprint(a.value, b.value)",
        "1 0",
        ["1 1", "0 0", "0 1"],
        "Each instance initializes its own value; only a is incremented.",
    ),
    (
        'class Notifier:\n    def send(self, text):\n        return "Notice: " + text\nclass Reminder:\n    def __init__(self, notifier):\n        self.notifier = notifier\n    def remind(self):\n        return self.notifier.send("Practice")\nprint(Reminder(Notifier()).remind())',
        "Notice: Practice",
        ["Practice", "None", "AttributeError"],
        "Reminder delegates sending to its contained notifier and returns the result.",
    ),
    (
        "def numbers():\n    yield 1\n    yield 2\ng = numbers()\nprint(list(g), list(g))",
        "[1, 2] []",
        ["[1, 2] [1, 2]", "[] []", "[1] [2]"],
        "The first list consumes the generator, leaving it exhausted.",
    ),
    (
        'from functools import wraps\ndef keep_name(fn):\n    @wraps(fn)\n    def wrapped():\n        return fn()\n    return wrapped\n@keep_name\ndef greet():\n    return "hello"\nprint(greet.__name__, greet())',
        "greet hello",
        ["wrapped hello", "greet None", "wrapped None"],
        "wraps preserves the function name and the wrapper forwards its return value.",
    ),
    (
        "from dataclasses import dataclass, field\n@dataclass\nclass Learner:\n    scores: list = field(default_factory=list)\na = Learner()\nb = Learner()\na.scores.append(8)\nprint(a.scores, b.scores)",
        "[8] []",
        ["[8] [8]", "[] []", "TypeError"],
        "The factory creates a separate list for each instance.",
    ),
    (
        'from collections import Counter\ncounts = Counter("banana")\nprint(counts["a"], counts["z"])',
        "3 0",
        ["3 KeyError", "2 0", "1 1"],
        "There are three a characters; Counter returns zero for a missing item.",
    ),
    (
        'def add(a, b):\n    return a + b\nassert add(-2, 2) == 0\nprint("passed")',
        "passed",
        ["0", "AssertionError", "None"],
        "The assertion succeeds and execution continues to print.",
    ),
    (
        'import sqlite3\nconn = sqlite3.connect(":memory:")\ntry:\n    conn.execute("CREATE TABLE goals (title TEXT)")\n    conn.execute("INSERT INTO goals VALUES (?)", ("Learn SQL",))\n    print(conn.execute("SELECT COUNT(*) FROM goals").fetchone()[0])\nfinally:\n    conn.close()',
        "1",
        ["0", "Learn SQL", "OperationalError"],
        "The parameterized insert adds one row, so COUNT returns one.",
    ),
    (
        'import json\nresponse = json.loads(\'{"status": "ok", "items": [1, 2, 3]}\')\nprint(response["status"], len(response["items"]))',
        "ok 3",
        ["ok 2", "status 3", "KeyError"],
        "The decoded object contains the status string and three list items.",
    ),
    (
        "import asyncio\nasync def value(n):\n    await asyncio.sleep(0)\n    return n * 2\nasync def main():\n    print(await asyncio.gather(value(3), value(1)))\nasyncio.run(main())",
        "[6, 2]",
        ["[2, 6]", "6 2", "None"],
        "gather returns results in the order of its input awaitables, not completion order.",
    ),
    (
        'from flask import Flask\napp = Flask(__name__)\n@app.get("/")\ndef home():\n    return "Hello"\nresponse = app.test_client().get("/")\nprint(response.status_code, response.get_data(as_text=True))',
        "200 Hello",
        ["404 Hello", "200 None", "500 Hello"],
        "The local test client dispatches the GET request to the registered route without a live server.",
    ),
    (
        "scores = [10, 20, 30]\nprint(sum(scores) / len(scores))",
        "20.0",
        ["60", "30.0", "10.0"],
        "This plain-Python baseline mean divides the sum 60 by the three scores.",
    ),
    (
        "actual = [1, 0, 1, 1]\npredicted = [1, 0, 0, 1]\ncorrect = sum(a == p for a, p in zip(actual, predicted))\nprint(correct / len(actual))",
        "0.75",
        ["1.0", "0.25", "3.0"],
        "Three out of four predictions match, so this example accuracy is 0.75.",
    ),
    (
        'documents = ["lists are mutable", "tuples are immutable"]\nevidence = [text for text in documents if "lists" in text]\nprint(" | ".join(evidence))',
        "lists are mutable",
        ["tuples are immutable", "lists are mutable | tuples are immutable", "[]"],
        "The filter selects only the evidence containing lists; no model call is made.",
    ),
    (
        'def completion_rate(goals):\n    if not goals:\n        return 0.0\n    return sum(goal["done"] for goal in goals) / len(goals) * 100\nprint(completion_rate([]), completion_rate([{ "done": True }, { "done": False }]))',
        "0.0 50.0",
        ["0.0 100.0", "ZeroDivisionError", "50.0 0.0"],
        "Empty input uses the guard; one completed goal out of two gives 50 percent.",
    ),
]

ERRORS = [
    (
        1,
        "Why does this numeric conversion fail?",
        'print(int("3.5"))',
        "The text is not a valid integer representation",
        [
            "int accepts no strings",
            "print cannot display integers",
            "The decimal point is a Python syntax error",
        ],
        "int cannot parse a decimal string directly. Decide whether a float or an integer is intended before converting.",
        "ValueError",
    ),
    (
        6,
        "Why does this string edit fail?",
        'text = "Python"\ntext[0] = "p"',
        "Strings do not support item assignment",
        [
            "The index is outside the string",
            "Lowercase letters are forbidden",
            "Strings cannot contain six characters",
        ],
        "Strings are immutable. Build a new string rather than assigning a character by index.",
        "TypeError",
    ),
    (
        7,
        "Why does this dictionary lookup fail?",
        'profile = {"name": "Ada"}\nprint(profile["score"])',
        "The requested key does not exist",
        [
            "Dictionaries require numeric keys",
            "print cannot access dictionaries",
            "Ada is not a valid value",
        ],
        "Indexing a missing dictionary key raises KeyError. Use get when a default is appropriate.",
        "KeyError",
    ),
    (
        9,
        "Why does this function call fail?",
        "def double(n):\n    return n * 2\nprint(double())",
        "A required positional argument is missing",
        [
            "Functions cannot multiply",
            "return must contain a string",
            "The function must be called twice",
        ],
        "The function defines a required parameter n; supply it in the call.",
        "TypeError",
    ),
    (
        16,
        "Why does the third next call fail?",
        "values = iter([1, 2])\nnext(values)\nnext(values)\nnext(values)",
        "The iterator is exhausted",
        [
            "Iterators start at index one",
            "next returns the whole list",
            "Lists cannot contain two integers",
        ],
        "After the two values have been consumed, next raises StopIteration without a supplied default.",
        "StopIteration",
    ),
    (
        28,
        "Why does this completion calculation fail on empty input?",
        'goals = []\nprint(sum(goal["done"] for goal in goals) / len(goals))',
        "The denominator is zero",
        [
            "Empty lists cannot be iterated",
            "sum always raises on empty input",
            "Boolean values cannot be summed",
        ],
        "sum of an empty iterable is zero and len is zero. Define an empty-input result before dividing.",
        "ZeroDivisionError",
    ),
]


def bank_entries():
    """Yield stable IDs, topic titles, and validated question content."""
    for index, (concept, output) in enumerate(zip(CONCEPTS, OUTPUTS, strict=True)):
        prompt, answer, distractors, explanation = concept
        yield _entry(index, "concept", prompt, "", answer, distractors, explanation)
        code, answer, distractors, explanation = output
        prompt = "What does this complete Python program print?"
        yield _entry(index, "output", prompt, code, answer, distractors, explanation)
    for index, prompt, code, answer, distractors, explanation, error in ERRORS:
        entry = _entry(index, "error", prompt, code, answer, distractors, explanation)
        entry[2]["expected_error"] = error
        yield entry


def _entry(index, category, prompt, code, answer, distractors, explanation):
    options = [answer, *distractors]
    offset = index % 4
    options = options[offset:] + options[:offset]
    content = dict(
        prompt=prompt,
        category=category,
        difficulty="beginner",
        code=code,
        options=options,
        correct=options.index(answer),
        explanation=explanation,
        tests=[],
        reference="",
        runtime="",
        error_category="runtime" if category == "error" else "",
    )
    return f"foundations-v1-{index}-{category}", LESSONS[index][1], content
