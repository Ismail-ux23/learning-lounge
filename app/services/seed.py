import hashlib
from app.extensions import db
from app.models import Course,Module,Topic,Lesson,Question,Resource,Category
from data.curriculum import LESSONS

def seed_database():
    seed_resources()
    if Course.query.filter_by(slug='python-foundations').first(): return
    course=Course(title='Python, from the ground up',slug='python-foundations',description='Build a strong foundation, solve real problems, and find your next step. 29 practical lessons, from your first line to data and AI.',objectives='Read and write Python confidently. Design small programs. Test your work. Explore specialist fields.',status='published',version='2026.1 · Python 3.14',reviewed='2026-09-29',references='https://docs.python.org/3.14/tutorial/',level='Beginner to intermediate')
    db.session.add(course); db.session.flush()
    course.rules={**course.rules,'artwork':'python-course'}
    modules={}; topics=[]
    for i,(group,title,body,code,mistake,exercise) in enumerate(LESSONS):
        if group not in modules:
            module=Module(course_id=course.id,title=group,position=len(modules)); db.session.add(module); db.session.flush(); modules[group]=module
        topic=Topic(module_id=modules[group].id,title=title,position=i); db.session.add(topic); db.session.flush(); topics.append(topic)
        db.session.add(Lesson(topic_id=topic.id,title=title,objectives='Understand '+title.lower()+'. Apply the example and complete the exercise.',body=body,code=code,mistakes=mistake,exercise=exercise,position=i))
    questions=[
      (1,'concept','What is the type of the value returned by input()?','',['str','int','float','bool'],0,'input() always returns text. Convert and validate that text when a numeric value is needed.'),
      (1,'concept','Which statement assigns the integer 7 to a variable named score?','',['score = 7','score == 7','7 = score','int score = 7'],0,'The assignment operator = binds the name on the left to the value on the right.'),
      (3,'output','What does this program print?','print(17 // 5)',['3','3.4','2','4'],0,'Floor division gives 3 because 5 fits into 17 three whole times.'),
      (5,'output','What is printed by this loop?','total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)',['6','10','3','4'],0,'range(1, 4) produces 1, 2, 3. Their sum is 6.'),
      (7,'error','Why does this program fail?','values = [1, 2]\nvalues = values.append(3)\nprint(len(values))',['append returns None, so values becomes None','Lists cannot contain 3','len only accepts strings','append returns an integer'],0,'append modifies a list in place and returns None. Correct code: values.append(3), followed by print(len(values)).'),
      (9,'error','Why does this call print None after printing 10?','def double(n):\n    print(n * 2)\nprint(double(5))',['The function has no return statement','Multiplication is invalid','Functions cannot print','The argument must be a string'],0,'The inner print displays 10. The function implicitly returns None, which the outer print displays. Use return n * 2.'),
      (6,'output','What is the result of this slice?','print("Python"[1:4])',['yth','Pyt','ytho','tho'],0,'Slicing includes the start index 1 and excludes the stop index 4.'),
      (7,'concept','Which collection is designed to store unique values?','',['set','list','tuple','str'],0,'A set contains distinct hashable values. Its iteration order should not be assumed.'),
      (9,'concept','Which default avoids sharing a mutable list across calls?','',['None, then create a list inside the function','An empty list in the signature','A global empty list','A list stored as a class attribute'],0,'Default arguments are evaluated once. Use None and create a fresh list for each call.'),
      (13,'concept','Which exception should you catch when int("hello") fails?','',['ValueError','KeyError','IndexError','ZeroDivisionError'],0,'The string has the right type but is not a valid integer representation, so int raises ValueError.'),
      (20,'concept','Which test is most useful for a function computing an average?','',['Test empty input and known numeric examples','Only test its name','Copy the implementation into the test','Always expect zero'],0,'Tests should cover defined behavior and boundary cases rather than duplicating the implementation.'),
      (21,'concept','How should user-provided values be supplied to a SQL query?','',['Using query parameters','Using an f-string','By concatenating raw strings','By removing spaces'],0,'Bound parameters keep values separate from the SQL statement and prevent values from becoming SQL syntax.'),
    ]
    for topic,category,prompt,code,options,correct,explanation in questions:
        content=dict(prompt=prompt,category=category,difficulty='beginner',code=code,options=options,correct=correct,explanation=explanation,tests=[],reference='',runtime='',error_category='runtime' if category=='error' else '')
        db.session.add(Question(course_id=course.id,topic_id=topics[topic].id,state='approved',category=category,difficulty='beginner',content=content,fingerprint=hashlib.sha256(prompt.lower().encode()).hexdigest()))
    prompt='Read two integers from standard input, separated by whitespace, and print their sum. Inputs are between -1000 and 1000.'
    content=dict(prompt=prompt,category='code',difficulty='beginner',code='# Read two integers and print their sum\n',options=[],correct=None,explanation='Split the input, convert both values to integers, and add them. Any implementation satisfying the input/output contract earns credit.',tests=[{'stdin':'2 3\n','expected':'5\n','weight':1,'visible':True},{'stdin':'-5 5\n','expected':'0\n','weight':2,'visible':False},{'stdin':'1000 -2\n','expected':'998\n','weight':2,'visible':False}],reference='a, b = map(int, input().split())\nprint(a + b)',runtime='Python 3.14')
    db.session.add(Question(course_id=course.id,topic_id=topics[2].id,state='draft',category='code',difficulty='beginner',content=content,fingerprint=hashlib.sha256(prompt.encode()).hexdigest()))
    db.session.commit()

def seed_resources():
    for name,slug in [('Programming languages','language'),('Frameworks','framework'),('Libraries','library'),('Databases','database'),('Technical subjects','technical')]:
        if not Category.query.filter_by(slug=slug).first(): db.session.add(Category(name=name,slug=slug))
    resources=[
        ('The Python tutorial','The official guide to Python syntax, core types, functions, classes, and the standard library.','https://docs.python.org/3.14/tutorial/','Official documentation'),
        ('Python standard library','Find the built-in tools for files, dates, data structures, testing, and more.','https://docs.python.org/3.14/library/','Reference'),
        ('Python packaging guide','Learn how virtual environments, package installation, and dependency distribution fit together.','https://packaging.python.org/en/latest/tutorials/installing-packages/','Practical guide'),
        ('Flask documentation','Explore routes, templates, application structure, and web-development fundamentals.','https://flask.palletsprojects.com/en/stable/','Web development')]
    for i,(title,description,url,category) in enumerate(resources):
        if not Resource.query.filter_by(url=url).first(): db.session.add(Resource(title=title,description=description,url=url,category=category,status='published',position=i))
    db.session.commit()
