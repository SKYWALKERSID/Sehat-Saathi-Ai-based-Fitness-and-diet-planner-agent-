# Decision-Making Algorithms Overview

## Overview
Sehat Saathi uses deterministic decision-making rules so the app can produce safe and explainable recommendations.

## Core Metrics
### BMI
BMI is calculated from weight and height and used to categorize the user's current body status.

### BMR
BMR is calculated using the Mifflin-St Jeor formula.

### TDEE
TDEE is derived from BMR and activity level.

## Goal Adjustments
- Weight loss: calorie deficit
- Fat loss: moderate deficit
- Muscle gain: calorie surplus
- Strength training: slight surplus
- General fitness: maintenance

## Macro Rules
- Keto: higher fat, lower carbs
- Low carb: protein emphasis with reduced carbs
- High protein: balanced carbs and fat with higher protein
- Balanced: default macro split for general use

## Safety Rules
- Exclude exercises that may aggravate injuries
- Adjust plans for medical conditions and allergies
- Provide a confidence score for the recommendation set

## Plan Generation
The engine combines calculations and rules to generate a workout plan, meal plan, and progress targets that remain consistent with the user's profile.

## Conclusion
The algorithm layer is intentionally simple, auditable, and suitable for a health-focused project.
