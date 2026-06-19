# Data Collection and Processing Overview

## Overview
Sehat Saathi collects only the information needed to generate a personalized fitness and nutrition plan. The flow is simple: collect user input, validate it, calculate health metrics, generate plans, and store progress data.

## Collected Inputs
- Age, gender, height, and weight
- Goal and activity level
- Workout experience
- Diet preference
- Medical conditions, injuries, and allergies
- Water and sleep targets

## Processing Steps
1. Validate field formats and numeric ranges.
2. Compute BMI, BMR, and TDEE.
3. Apply goal-based calorie adjustments.
4. Generate workout and meal recommendations.
5. Save profile and progress data in SQLite.

## Data Quality
- Required fields are checked before submission.
- Invalid values are blocked early.
- Progress entries are stored with timestamps.
- Feedback remains tied to the active profile.

## Privacy and Security
- Data stays in the local application database.
- No unnecessary external sharing is used.
- The app includes policy pages for privacy and terms.
- Sensitive health inputs are handled with minimal complexity.

## Conclusion
The processing pipeline keeps the Sehat Saathi experience reliable and easy to maintain while still supporting personalized planning.
