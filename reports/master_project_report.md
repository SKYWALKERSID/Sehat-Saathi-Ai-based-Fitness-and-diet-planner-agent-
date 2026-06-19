# Sehat Saathi - Project Report

AI Based Fitness & Diet Planner Agent

## Abstract
Sehat Saathi is a health-tech application that creates personalized fitness and nutrition plans from user biometrics, goals, dietary preferences, activity level, and health constraints. The system combines deterministic recommendation logic with clinical formulas to produce workout schedules, meal plans, and progress tracking views that are safe, explainable, and easy to use.

## 1. Project Summary
The application is built as a Flask web app with SQLite storage and a modern responsive frontend. It is designed for users who want practical fitness guidance without the complexity of a full mobile app or the risks of generic workout templates.

## 2. Objectives
- Generate personalized workout and diet plans.
- Apply safety filters for injuries, medical conditions, and allergies.
- Compute BMI, BMR, TDEE, and target calories.
- Track progress with charts and feedback.
- Present the experience in a premium SaaS-style interface.

## 3. Functional Scope
- 3-step onboarding wizard
- Profile switching in the dashboard
- Weekly workout schedule by day
- Daily meal plan with macro summaries
- Progress logging for weight, water, sleep, and calories
- Ratings and comments for plan review
- Privacy Policy and Terms pages

## 4. Recommendation Logic
The system uses rule-based logic instead of opaque model output. That makes the recommendations predictable and easy to audit. Workout suggestions are filtered by injury and restriction rules. Diet plans are adjusted by diet preference, calorie target, and macro distribution.

## 5. User Experience Direction
The interface follows a clean modern product style:
- white cards
- soft borders and shadows
- large whitespace
- Inter typography
- green accent color
- responsive layout for desktop and mobile
- simple interaction patterns with clear hierarchy

## 6. Technical Implementation
- Flask serves the app and API endpoints.
- SQLite stores profiles, progress logs, and feedback.
- Vanilla JavaScript hydrates the dashboard and renders charts.
- Chart.js shows trends over time.
- Bootstrap 5 supports responsive layout primitives.

## 7. Validation Summary
The project was tested with multiple user profiles to confirm that the generated plans remain aligned to calorie targets, diet restrictions, and workout safety rules. The dashboard updates correctly when profiles are switched and progress data is saved.

## 8. Conclusion
Sehat Saathi demonstrates how a small but well-structured rule-based engine can deliver useful fitness and nutrition guidance in a polished user interface. The current codebase is ready for iterative product work, content refinement, and future integration with richer health data sources.
