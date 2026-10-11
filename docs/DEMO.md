# Learning Lounge demo walkthrough

Use the local installation in the README before following this guide.
This is a local walkthrough; no public hosted demo is currently linked.

## Learner flow

1. Open http://localhost:5066 and browse the course catalog.
2. Open **Python, from the ground up** to inspect its syllabus.
3. Register your own learner account at `/register`.
4. Enroll in the course and open the first lesson.
5. Read the explanation, inspect the code example, and complete the lesson.
6. Open the dashboard to see saved progress. Reopen the course to continue.
7. Explore practice using topics with approved questions. Review mistakes
   and result history after completing an available assessment.

For a portfolio presentation, show the syllabus, a lesson, saved progress,
and an assessment result using your own sample account. Use sample data;
keep real learner names and email addresses out of shared screenshots.

## Administrator flow

Run `flask --app run create-admin` and enter your own credentials when
prompted. The administrator password must be at least 12 characters.
Sign in to review course content, questions, resources, and AI jobs.
AI-generated questions require review before entering the approved bank.

## Service boundaries

- The local preset leaves AI_MODEL empty. AI generation is unconfigured.
- Coding execution requires a trusted operator-controlled Judge0 service.
- Password-reset emails require configured SMTP. Registration does not
  require an email service.
- The local walkthrough does not start Celery workers or periodic tasks.
  Use the configured full stack for background processing.
- Final assessments must cover every syllabus topic and selected category.
  The introductory seed bank is too small for a full-course final; add
  reviewed questions before showcasing that flow.

Certificates reflect this application's assessment rules, not external
accreditation. Deployment and live integrations need separate verification.
