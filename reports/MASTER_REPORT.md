# Sehat Saathi - Master Report

![Sehat Saathi logo](app/static/img/sehatlogo.png)

**AI Based Fitness & Diet Planner Agent**

## Table of Contents
1. Executive Summary
2. Product Overview
3. Recommendation Engine
4. Data Collection and Processing
5. Decision-Making Algorithms
6. User-Centric Application Design
7. Health Technology Perspective
8. Technical Implementation
9. Validation Results
10. Future Scope
11. Conclusion

## Executive Summary
Sehat Saathi is a premium fitness and nutrition planner designed for a safe, simple, and personalized user experience. The application generates workout and diet plans from user data while accounting for injuries, allergies, medical conditions, goals, and lifestyle patterns.

The current product direction emphasizes a clean SaaS interface, white cards, soft shadows, green accent color, and mobile-first responsiveness. The dashboard presents plans, progress, and feedback in a way that is readable and easy to maintain.

## Product Overview
The problem Sehat Saathi solves is straightforward: many fitness apps are visually noisy, difficult to follow, and do not respect safety constraints. This project focuses on clarity and practical recommendations instead of generic templates.

### Main capabilities
- Personalized onboarding flow
- Weekly workout plan generation
- Meal plan generation with macros
- Progress charts and logging
- Feedback capture
- Policy pages and app branding

## Recommendation Engine
The recommendation engine is deterministic and rule-based. It uses the following inputs:
- age
- gender
- height
- weight
- activity level
- fitness goal
- diet preference
- injuries
- medical conditions
- allergies

The system outputs:
- BMI, BMR, TDEE, and target calories
- workout schedule with sets, reps, and rest periods
- meal plan with macro allocation
- safety and confidence indicators

## Data Collection and Processing
User input is validated before plan generation. The application then computes health metrics, transforms those metrics into plan targets, and stores the results in SQLite. Progress logs and feedback are saved separately so the dashboard can display trends.

## Decision-Making Algorithms
Sehat Saathi applies rules for:
- calorie target adjustments
- macro split selection
- exercise exclusions and substitutions
- meal filtering by preference and allergy
- confidence scoring based on user risk factors

## User-Centric Application Design
The UI is designed for fast scanning and low cognitive load. Cards are large, spacing is generous, and the layout adapts to smaller screens without hiding critical information. The interface avoids unnecessary visual effects.

## Health Technology Perspective
The app sits in the health-tech category because it combines biometric calculations, nutrition planning, progress tracking, and safety-aware decision-making in one system. The design is intended to support students, professionals, and fitness users who want a practical planning tool.

## Technical Implementation
- Backend: Python Flask
- Database: SQLite
- Frontend: HTML, CSS, Vanilla JavaScript
- Charts: Chart.js
- Layout support: Bootstrap 5

## Validation Results
The system was validated using multiple sample profiles to ensure that the generated plans stay aligned with user-specific goals and constraints. The dashboard and planning views render correctly across the main application flow.

## Future Scope
Possible future improvements include wearable integration, richer progress analytics, stronger onboarding guidance, and broader personalization for special diet or recovery cases.

## Conclusion
Sehat Saathi is a focused health-tech product that combines safe recommendations with a polished user experience. The codebase now reflects the same brand and product identity across the application and documentation.
