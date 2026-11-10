document.addEventListener('DOMContentLoaded', () => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const dashboardRoot = document.querySelector('#dashboardSection .ss-shell') || document.getElementById('dashboardSection');
    const dashboardGet = (id) => dashboardRoot?.querySelector(`#${id}`) || document.getElementById(id);

    // ----------------------------------------------------
    let currentStep = 1;
    const setupSection = dashboardGet('setupSection');
    const setupForm = dashboardGet('setupForm');
    const formSteps = document.querySelectorAll('.form-step');
    const btnPrevStep = dashboardGet('btnPrevStep');
    const btnNextStep = dashboardGet('btnNextStep');
    const btnSubmitForm = dashboardGet('btnSubmitForm');
    const btnNewProfile = dashboardGet('btnNewProfile');
    
    // Header profile switch hook
    const headerProfileSelect = dashboardGet('headerProfileSelect');
    const headerProfileSelectWrapper = dashboardGet('headerProfileSelectWrapper');

    if (btnNextStep) btnNextStep.addEventListener('click', handleNextStep);
    if (btnPrevStep) btnPrevStep.addEventListener('click', handlePrevStep);
    if (setupForm) setupForm.addEventListener('submit', handleFormSubmit);

    // Header selector change trigger
    if (headerProfileSelect) {
        headerProfileSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                loadProfileDetails(e.target.value);
            } else {
                showSetupWizard();
            }
        });
    }

    // Toggle button to add a new profile
    if (btnNewProfile) {
        btnNewProfile.addEventListener('click', () => {
            showSetupWizard();
        });
    }

    function handleNextStep() {
        if (validateStep(currentStep)) {
            currentStep++;
            updateStepUI();
        }
    }

    function handlePrevStep() {
        currentStep--;
        updateStepUI();
    }

    function updateStepUI() {
        formSteps.forEach(step => {
            step.classList.remove('active');
            if (parseInt(step.getAttribute('data-step')) === currentStep) {
                step.classList.add('active');
            }
        });

        if (btnPrevStep) btnPrevStep.disabled = currentStep === 1;
        
        if (currentStep === 3) {
            if (btnNextStep) btnNextStep.classList.add('hidden');
            if (btnSubmitForm) btnSubmitForm.classList.remove('hidden');
        } else {
            if (btnNextStep) btnNextStep.classList.remove('hidden');
            if (btnSubmitForm) btnSubmitForm.classList.add('hidden');
        }
    }

    function validateStep(step) {
        let isValid = true;
        const currentStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
        if (!currentStepEl) return true;
        
        const inputs = currentStepEl.querySelectorAll('[required]');
        
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
            
            if (!input.checkValidity() || input.value.trim() === "") {
                input.classList.add('is-invalid');
                isValid = false;
            }
            
            if (input.type === 'number') {
                const val = parseFloat(input.value);
                const min = parseFloat(input.min);
                const max = parseFloat(input.max);
                if (isNaN(val) || val < min || val > max) {
                    input.classList.add('is-invalid');
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }

    // ----------------------------------------------------
    // Profile Switch & UI Hydration
    // ----------------------------------------------------
    let activeProfileId = null;
    let weightChart = null;
    let lifestyleChart = null;
    let progressHistoryCache = [];
    let currentProfileSnapshot = null;
    let progressRange = 'week';
    const chartPalette = {
        primary: '#15803D',
        secondary: '#94A3B8',
        accent: '#22C55E',
        mutedFill: 'rgba(34, 197, 94, 0.08)',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#3B82F6'
    };

    function clampValue(value, min, max) {
        return Math.min(max, Math.max(min, value));
    }

    function toNumber(value, fallback = 0) {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function getDateKey(dateValue) {
        const date = dateValue instanceof Date ? dateValue : new Date(dateValue);
        if (Number.isNaN(date.getTime())) return '';
        return date.toISOString().split('T')[0];
    }

    function normalizeProgressHistory(history) {
        return (Array.isArray(history) ? history : [])
            .map((entry) => {
                const parsedDate = new Date(entry.log_date);
                return {
                    ...entry,
                    parsedDate,
                    dateKey: getDateKey(parsedDate)
                };
            })
            .filter((entry) => !Number.isNaN(entry.parsedDate.getTime()))
            .sort((a, b) => a.parsedDate - b.parsedDate);
    }

    function getProgressWindowSize(range) {
        if (range === 'month') return 30;
        if (range === 'year') return 365;
        return 7;
    }

    function getFilteredProgressHistory(history, range) {
        const sorted = normalizeProgressHistory(history);
        const windowSize = getProgressWindowSize(range);
        if (!sorted.length) return [];

        const latestDate = sorted[sorted.length - 1].parsedDate;
        const cutoff = new Date(latestDate);
        cutoff.setHours(0, 0, 0, 0);
        cutoff.setDate(cutoff.getDate() - (windowSize - 1));

        const filtered = sorted.filter((entry) => entry.parsedDate >= cutoff);
        return filtered.length > 0 ? filtered : sorted.slice(-windowSize);
    }

    function formatSignedDelta(delta, unit) {
        const sign = delta < 0 ? '↓' : delta > 0 ? '↑' : '→';
        return `${sign} ${Math.abs(delta).toFixed(1)} ${unit}`;
    }

    function getRangeLabel(range) {
        if (range === 'month') return 'Last 30 Days';
        if (range === 'year') return 'Last 365 Days';
        return 'Last 7 Days';
    }

    function formatDayLabel(dateValue) {
        const date = dateValue instanceof Date ? dateValue : new Date(dateValue);
        if (Number.isNaN(date.getTime())) return String(dateValue || '');
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }

    function animateCountTo(element, targetValue, suffix = '', decimals = 0, duration = 650) {
        if (!element) return;
        const finalValue = Number(targetValue);
        if (!Number.isFinite(finalValue)) {
            element.textContent = `${targetValue}${suffix}`;
            return;
        }

        if (prefersReducedMotion) {
            element.textContent = `${finalValue.toFixed(decimals)}${suffix}`;
            return;
        }

        const start = performance.now();
        const initial = 0;

        function tick(now) {
            const progress = clampValue((now - start) / duration, 0, 1);
            const value = initial + ((finalValue - initial) * progress);
            element.textContent = `${value.toFixed(decimals)}${suffix}`;
            if (progress < 1) {
                window.requestAnimationFrame(tick);
            }
        }

        window.requestAnimationFrame(tick);
    }

    function renderSparkline(svgElement, values, strokeColor, fillColor) {
        if (!svgElement) return;
        const points = (Array.isArray(values) ? values : []).map((value) => toNumber(value, 0));
        if (points.length === 0) {
            svgElement.innerHTML = '';
            return;
        }

        const width = 120;
        const height = 44;
        const padding = 4;
        const min = Math.min(...points);
        const max = Math.max(...points);
        const range = max - min || 1;
        const step = points.length > 1 ? (width - (padding * 2)) / (points.length - 1) : 0;
        const pathPoints = points.map((point, index) => {
            const x = padding + (index * step);
            const y = height - padding - (((point - min) / range) * (height - (padding * 2)));
            return `${x.toFixed(1)},${y.toFixed(1)}`;
        });
        const areaPath = `M ${padding},${height - padding} L ${pathPoints.join(' L ')} L ${width - padding},${height - padding} Z`;
        const linePath = `M ${pathPoints.join(' L ')}`;
        svgElement.innerHTML = `
            <path d="${areaPath}" fill="${fillColor}" opacity="0.55"></path>
            <path d="${linePath}" fill="none" stroke="${strokeColor}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path>
        `;
    }

    function getLatestEntry(history) {
        return history.length > 0 ? history[history.length - 1] : null;
    }

    function calculateLoggingStreak(history) {
        if (!history.length) return 0;
        const dates = new Set(history.map((entry) => entry.dateKey));
        let streak = 0;
        const cursor = new Date(history[history.length - 1].parsedDate);
        cursor.setHours(0, 0, 0, 0);

        while (dates.has(getDateKey(cursor))) {
            streak++;
            cursor.setDate(cursor.getDate() - 1);
        }

        return streak;
    }

    function estimateBodyFatPercent(user, bmi) {
        const age = toNumber(user?.age, 30);
        const gender = String(user?.gender || '').toLowerCase();
        const genderOffset = gender.includes('female') ? -10.8 : 0;
        return clampValue((1.2 * bmi) + (0.23 * age) - 5.4 + genderOffset, 8, 40);
    }

    function estimateMuscleMassPercent(bodyFatPercent) {
        return clampValue(100 - bodyFatPercent - 18, 30, 82);
    }

    function determineGoalWeight(user, currentWeight) {
        const goal = String(user?.fitness_goal || '').toLowerCase();
        const baseline = toNumber(currentWeight, toNumber(user?.weight, 0));

        if (goal.includes('gain') || goal.includes('muscle') || goal.includes('strength')) {
            return baseline + 5;
        }
        if (goal.includes('loss') || goal.includes('fat')) {
            return Math.max(40, baseline - 5);
        }
        return baseline;
    }

    function getProgressScoreLabel(score) {
        if (score >= 85) return 'Excellent';
        if (score >= 70) return 'Strong';
        if (score >= 55) return 'Steady';
        return 'Needs attention';
    }

    function animateReveal(elements, baseDelay = 80) {
        if (!elements || elements.length === 0) return;

        elements.forEach((element, index) => {
            element.classList.add('reveal-on-load');
            if (prefersReducedMotion) {
                element.classList.add('is-visible');
                return;
            }

            window.setTimeout(() => {
                element.classList.add('is-visible');
            }, index * baseDelay);
        });
    }

    function animateSection(section) {
        if (!section) return;
        section.classList.remove('is-visible');
        section.classList.add('reveal-on-load');

        if (prefersReducedMotion) {
            section.classList.add('is-visible');
            return;
        }

        window.requestAnimationFrame(() => {
            window.requestAnimationFrame(() => {
                section.classList.add('is-visible');
            });
        });
    }

    animateReveal(document.querySelectorAll('main .card, main .surface-panel, main .hero-panel, main .ss-card, main .saathi-info-card, main .saathi-feature-card, main .saathi-example-card, main .saathi-price-card, main .saathi-cta-card'), 50);

    const mealMeta = {
        Breakfast: {
            icon: '🌅',
            time: '7:00 AM – 9:00 AM',
            insight: 'A high-protein breakfast helps support morning energy and muscle recovery.',
            substitutions: {
                'Rolled Oats': 'Muesli',
                'Whole Eggs (Boiled)': 'Paneer',
                Almonds: 'Walnuts',
                'Egg Whites': 'Greek Yogurt',
                'Brown Rice': 'Quinoa',
                Spinach: 'Kale',
                Avocado: 'Apple',
                Tofu: 'Cottage Cheese',
                Tempeh: 'Tofu',
                Asparagus: 'Broccoli',
                'Peanut Butter': 'Chia Seeds'
            }
        },
        Lunch: {
            icon: '🍱',
            time: '12:30 PM – 2:00 PM',
            insight: 'Balanced lunch support keeps energy stable through the afternoon and reduces snacking.',
            substitutions: {
                'Egg Whites': 'Greek Yogurt',
                'Brown Rice': 'Quinoa',
                Spinach: 'Mixed Greens',
                Tofu: 'Paneer',
                Tempeh: 'Chickpeas'
            }
        },
        'Evening Snack': {
            icon: '🍎',
            time: '4:00 PM – 5:30 PM',
            insight: 'A lighter snack can maintain focus while keeping hunger and cravings under control.',
            substitutions: {
                Avocado: 'Apple Slices',
                Tofu: 'Greek Yogurt',
                Almonds: 'Pumpkin Seeds'
            }
        },
        Snack: {
            icon: '🍎',
            time: '4:00 PM – 5:30 PM',
            insight: 'A lighter snack can maintain focus while keeping hunger and cravings under control.',
            substitutions: {
                Avocado: 'Apple Slices',
                Tofu: 'Greek Yogurt',
                Almonds: 'Pumpkin Seeds'
            }
        },
        Dinner: {
            icon: '🍽',
            time: '7:30 PM – 9:00 PM',
            insight: 'Dinner is kept satisfying but not heavy, helping recovery without overshooting calories.',
            substitutions: {
                Tempeh: 'Paneer',
                Asparagus: 'Green Beans',
                'Peanut Butter': 'Hummus',
                Tofu: 'Paneer'
            }
        }
    };

    const workoutMeta = {
        Monday: {
            focus: 'Lower Body Focus',
            duration: 45,
            calories: 320,
            difficulty: 'Intermediate',
            muscles: 'Quads • Glutes • Core'
        },
        Tuesday: {
            focus: 'Upper Body Push',
            duration: 50,
            calories: 300,
            difficulty: 'Intermediate',
            muscles: 'Chest • Shoulders • Triceps'
        },
        Wednesday: {
            focus: 'Core & Conditioning',
            duration: 40,
            calories: 260,
            difficulty: 'Beginner',
            muscles: 'Core • Mobility • Cardio'
        },
        Thursday: {
            focus: 'Lower Body Strength',
            duration: 55,
            calories: 340,
            difficulty: 'Intermediate',
            muscles: 'Hamstrings • Glutes • Calves'
        },
        Friday: {
            focus: 'Full Body Hypertrophy',
            duration: 50,
            calories: 330,
            difficulty: 'Advanced',
            muscles: 'Chest • Back • Legs'
        },
        Saturday: {
            focus: 'Cardio & Mobility',
            duration: 35,
            calories: 240,
            difficulty: 'Beginner',
            muscles: 'Heart Rate • Mobility • Recovery'
        },
        Sunday: {
            focus: 'Recovery & Stretching',
            duration: 25,
            calories: 120,
            difficulty: 'Beginner',
            muscles: 'Mobility • Recovery • Breathwork'
        }
    };

    const workoutExerciseMeta = [
        {
            test: /squat/i,
            icon: '🏋️',
            muscles: 'Legs • Glutes',
            difficulty: 'Intermediate',
            tip: 'Focus on slow eccentric movement to maximize muscle activation.',
            instructions: 'Keep your chest up, brace the core, and drive through the mid-foot.',
            mistakes: 'Avoid collapsing the knees inward or rounding the lower back.',
            primary: 'Quadriceps',
            secondary: 'Glutes',
            equipment: 'Barbell',
            alternatives: ['Goblet Squat', 'Hack Squat', 'Leg Press']
        },
        {
            test: /pushup|pushups/i,
            icon: '💪',
            muscles: 'Chest • Triceps • Core',
            difficulty: 'Beginner',
            tip: 'Maintain a rigid plank line to keep tension on the chest and triceps.',
            instructions: 'Lower with control until your chest is close to the floor, then press back up.',
            mistakes: 'Avoid sagging hips or flaring the elbows too wide.',
            primary: 'Pectorals',
            secondary: 'Triceps',
            equipment: 'Bodyweight',
            alternatives: ['Incline Pushup', 'Dumbbell Press', 'Machine Chest Press']
        },
        {
            test: /plank/i,
            icon: '🧘',
            muscles: 'Core • Shoulders',
            difficulty: 'Beginner',
            tip: 'Keep the ribs down and squeeze the glutes for a stronger brace.',
            instructions: 'Hold a straight line from head to heels while breathing steadily.',
            mistakes: 'Avoid lifting the hips too high or letting the lower back sink.',
            primary: 'Abdominals',
            secondary: 'Shoulders',
            equipment: 'Mat',
            alternatives: ['Dead Bug', 'Bird Dog', 'Hollow Hold']
        },
        {
            test: /row/i,
            icon: '🚣',
            muscles: 'Back • Biceps',
            difficulty: 'Intermediate',
            tip: 'Drive elbows toward the hips and pause briefly at the top.',
            instructions: 'Pull the weight toward your torso with a neutral spine and controlled tempo.',
            mistakes: 'Avoid shrugging the shoulders or jerking through the movement.',
            primary: 'Lats',
            secondary: 'Rear Delts',
            equipment: 'Dumbbells',
            alternatives: ['Cable Row', 'Machine Row', 'Resistance Band Row']
        },
        {
            test: /deadlift/i,
            icon: '🏋️',
            muscles: 'Posterior Chain • Core',
            difficulty: 'Advanced',
            tip: 'Keep the bar close to your body for better leverage and safer mechanics.',
            instructions: 'Hinge at the hips, maintain a neutral spine, and stand tall at the top.',
            mistakes: 'Avoid rounding the back or yanking the bar off the floor.',
            primary: 'Hamstrings',
            secondary: 'Glutes',
            equipment: 'Barbell',
            alternatives: ['Romanian Deadlift', 'Trap Bar Deadlift', 'Kettlebell Swing']
        }
    ];

    const foodEmojiMap = [
        [/oat|oats|quinoa/i, '🥣'],
        [/egg/i, '🥚'],
        [/almond|walnut|nut|nuts|seed/i, '🥜'],
        [/rice|roti/i, '🍚'],
        [/spinach|greens|salad|palak/i, '🥬'],
        [/avocado/i, '🥑'],
        [/tofu|paneer|yogurt|milk|whey/i, '🧀'],
        [/tempeh|lentil|dal|chickpea|chana/i, '🍲'],
        [/chicken|salmon/i, '🍗'],
        [/banana|apple/i, '🍎'],
        [/asparagus|broccoli|beans|potato/i, '🥦'],
        [/peanut butter|butter/i, '🧈']
    ];

    function getMealMeta(mealType) {
        return mealMeta[mealType] || {
            icon: '🥗',
            time: 'Planned meal',
            insight: 'This meal is balanced for your target calories and macros.',
            substitutions: {}
        };
    }

    function getWorkoutMeta(day, dayExercises = []) {
        const base = workoutMeta[day] || workoutMeta.Monday;
        const activeEx = (Array.isArray(dayExercises) ? dayExercises : []).filter(e => e.name !== 'Rest & Recovery');
        if (activeEx.length === 0) {
            return {
                focus: 'Rest & Recovery',
                duration: 20,
                calories: 0,
                difficulty: 'Beginner',
                muscles: 'Full Body Recovery • Mobility'
            };
        }
        const muscleSet = new Set();
        const categories = new Set();
        activeEx.forEach(ex => {
            if (ex.primary) muscleSet.add(ex.primary);
            else if (ex.muscle_group) muscleSet.add(ex.muscle_group.split(',')[0].trim());
            if (ex.category) categories.add(ex.category);
        });
        const dynamicMuscles = Array.from(muscleSet).slice(0, 3).join(' • ') || base.muscles;
        const focusLabel = categories.has('Cardio') && categories.has('Strength')
            ? 'Hybrid Strength & Conditioning'
            : categories.has('Cardio')
                ? 'Cardio & Endurance'
                : categories.has('Mobility') && categories.size === 1
                    ? 'Mobility & Active Recovery'
                    : base.focus;
        const cals = activeEx.reduce((s, e) => s + (Number(e.calories_burned) || 0), 0) || base.calories;
        return {
            focus: focusLabel,
            duration: Math.max(20, activeEx.length * 12),
            calories: cals,
            difficulty: activeEx[0]?.difficulty || base.difficulty,
            muscles: dynamicMuscles
        };
    }

    function getWorkoutExerciseMeta(name, exerciseObj = {}) {
        const matched = workoutExerciseMeta.find((item) => item.test.test(name)) || {};
        const iconMap = [
            [/squat|leg press|deadlift/i, '🏋️'],
            [/pushup|bench|press|curl|tricep/i, '💪'],
            [/plank|yoga|stretch|bird-dog/i, '🧘'],
            [/row|pull-up/i, '🚣'],
            [/run|walk|hiit/i, '🏃'],
            [/swim/i, '🏊'],
            [/cycl/i, '🚴']
        ];
        const iconMatch = iconMap.find(([regex]) => regex.test(name));
        return {
            icon: matched.icon || (iconMatch ? iconMatch[1] : '🏋️'),
            muscles: exerciseObj.muscle_group || matched.muscles || 'Full Body',
            difficulty: exerciseObj.difficulty || matched.difficulty || 'Intermediate',
            tip: exerciseObj.tip || matched.tip || 'Move with control and keep each repetition consistent.',
            instructions: exerciseObj.instructions || matched.instructions || 'Keep good posture, control the movement, and breathe steadily.',
            mistakes: exerciseObj.mistakes || matched.mistakes || 'Avoid rushing the reps or losing tension.',
            primary: exerciseObj.primary || matched.primary || 'Primary muscles',
            secondary: exerciseObj.secondary || matched.secondary || 'Supporting muscles',
            equipment: exerciseObj.equipment || matched.equipment || 'Bodyweight or standard gym equipment',
            alternatives: (Array.isArray(exerciseObj.alternatives) && exerciseObj.alternatives.length > 0)
                ? exerciseObj.alternatives
                : (matched.alternatives || ['Machine variation', 'Dumbbell variation', 'Resistance band variation'])
        };
    }

    function getFoodAvatar(name) {
        const match = foodEmojiMap.find(([pattern]) => pattern.test(name));
        return match ? match[1] : '🥗';
    }

    function buildSubstitutions(foodItem, substitutions) {
        const foodName = typeof foodItem === 'object' ? (foodItem.name || '') : String(foodItem || '');
        if (typeof foodItem === 'object' && Array.isArray(foodItem.substitutions) && foodItem.substitutions.length > 0) {
            return `${foodName} → ${foodItem.substitutions.slice(0, 2).join(' or ')}`;
        }
        const primary = substitutions[foodName];
        if (primary) return `${foodName} → ${primary}`;

        const simple = foodName.replace(/\s*\([^)]*\)/g, '').trim();
        if (substitutions[simple]) return `${simple} → ${substitutions[simple]}`;

        return `${simple || foodName} → Mixed seasonal vegetables / Paneer / Tofu`;
    }

    function estimateFiber(meal) {
        return Math.max(4, Math.round((Number(meal.carbohydrates) || 0) * 0.18));
    }

    function getMealScore(meal) {
        const protein = Number(meal.protein) || 0;
        const carbs = Number(meal.carbohydrates) || 0;
        const fats = Number(meal.fats) || 0;
        const score = Math.round(84 + (protein * 0.55) + (carbs * 0.08) - (Math.max(0, fats - 18) * 0.18));
        return Math.max(72, Math.min(100, score));
    }

    function parseRepValue(reps) {
        if (!reps) return 10;
        const text = String(reps);
        const match = text.match(/(\d+)(?:\s*-\s*(\d+))?/);
        if (!match) return 10;
        const first = Number(match[1]) || 10;
        const second = Number(match[2]) || first;
        return Math.round((first + second) / 2);
    }

    function getDifficultyClass(level) {
        const normalized = String(level || '').toLowerCase();
        if (normalized.includes('beginner')) return 'beginner';
        if (normalized.includes('advanced')) return 'advanced';
        return 'intermediate';
    }

    // Load initial dropdown list
    loadUserProfilesList();

    function loadUserProfilesList() {
        return fetch('/api/profiles')
            .then(res => res.json())
            .then(profiles => {
                if (headerProfileSelect) {
                    headerProfileSelect.innerHTML = '<option value="">-- Switch/New Profile --</option>';
                    profiles.forEach(p => {
                        const opt = document.createElement('option');
                        opt.value = p.id;
                        opt.textContent = p.name;
                        headerProfileSelect.appendChild(opt);
                    });
                    
                    if (profiles.length > 0) {
                        headerProfileSelectWrapper.classList.remove('d-none');
                        // Auto-load the first profile
                        headerProfileSelect.value = profiles[0].id;
                        loadProfileDetails(profiles[0].id);
                    } else {
                        headerProfileSelectWrapper.classList.add('d-none');
                        showSetupWizard();
                    }
                }
            })
            .catch(err => console.error("Error loading profiles:", err));
    }

    function showSetupWizard() {
        if (setupSection) setupSection.classList.remove('hidden');
        const dashboardSection = dashboardGet('dashboardSection');
        if (dashboardSection) dashboardSection.classList.add('hidden');
        animateSection(setupSection);
        if (setupForm) setupForm.reset();
        currentStep = 1;
        updateStepUI();
        activeProfileId = null;
        if (headerProfileSelect) headerProfileSelect.value = "";
    }

    function loadProfileDetails(profileId) {
        activeProfileId = profileId;
        fetch(`/api/profile/${profileId}`)
            .then(res => res.json())
            .then(data => {
                // Show dashboard, hide onboarding
                if (setupSection) setupSection.classList.add('hidden');
                const dashboardSection = dashboardGet('dashboardSection');
                if (dashboardSection) dashboardSection.classList.remove('hidden');
                animateSection(dashboardSection);
                
                hydrateUI(data);
                loadProgressLogs(profileId);
                loadFeedbackTimeline(profileId);
            })
            .catch(err => console.error("Error loading profile:", err));
    }

    function hydrateUI(data) {
        const u = data.user;
        const g = data.goals;
        const diet = data.diet;

        // Display user banners
        dashboardGet('dispUserName').textContent = u.name;
        dashboardGet('dispUserGoal').innerHTML = `<i class="fa-solid fa-crosshairs"></i> Goal: ${u.fitness_goal} | Experience: ${u.workout_experience}`;
        dashboardGet('dispUserAge').textContent = `${u.age} yrs`;
        dashboardGet('dispUserWeight').textContent = `${u.weight} kg`;
        dashboardGet('dispUserHeight').textContent = `${u.height} cm`;
        dashboardGet('dispUserDiet').textContent = u.diet_preference;

        const sidebarProfileName = dashboardGet('sidebarProfileName');
        const sidebarGoal = dashboardGet('sidebarGoal');
        const railAge = dashboardGet('railAge');
        const railWeight = dashboardGet('railWeight');
        const railHeight = dashboardGet('railHeight');
        const railDiet = dashboardGet('railDiet');
        const railPlanScore = dashboardGet('railPlanScore');
        const railWeatherTemp = dashboardGet('railWeatherTemp');
        const railHydrationTarget = dashboardGet('railHydrationTarget');
        const railWeatherNote = dashboardGet('railWeatherNote');

        if (sidebarProfileName) sidebarProfileName.textContent = u.name;
        if (sidebarGoal) sidebarGoal.textContent = u.fitness_goal;
        if (railAge) railAge.textContent = `${u.age} yrs`;
        if (railWeight) railWeight.textContent = `${u.weight} kg`;
        if (railHeight) railHeight.textContent = `${u.height} cm`;
        if (railDiet) railDiet.textContent = u.diet_preference;
        if (railPlanScore) railPlanScore.textContent = g.recommendation_score ? `${g.recommendation_score} / 100` : `${g.confidence_score} / 100`;
        if (railWeatherTemp && g.weather_context) {
            railWeatherTemp.textContent = `${g.weather_context.temperature_c}°C (${g.weather_context.condition})`;
        }
        if (railHydrationTarget) {
            railHydrationTarget.textContent = `${u.hydration_target_l || u.water_intake} L/day`;
        }
        if (railWeatherNote && g.weather_context) {
            railWeatherNote.textContent = g.weather_context.recommendation || '';
        }

        // Coach tab ML Risk Badges
        const dispObesityRisk = dashboardGet('dispObesityRisk');
        const dispSedentaryRisk = dashboardGet('dispSedentaryRisk');
        const dispMetabolicRisk = dashboardGet('dispMetabolicRisk');
        const riskDict = g.predicted_risks || {};
        const formatRiskClass = (lvl) => lvl === 'High' ? 'badge bg-danger-subtle text-danger' : lvl === 'Moderate' ? 'badge bg-warning-subtle text-warning' : 'badge bg-success-subtle text-success';
        if (dispObesityRisk) {
            const r = riskDict.obesity_risk || 'Low';
            dispObesityRisk.textContent = r;
            dispObesityRisk.className = formatRiskClass(r);
        }
        if (dispSedentaryRisk) {
            const r = riskDict.sedentary_risk || 'Low';
            dispSedentaryRisk.textContent = r;
            dispSedentaryRisk.className = formatRiskClass(r);
        }
        if (dispMetabolicRisk) {
            const r = riskDict.metabolic_risk || 'Low';
            dispMetabolicRisk.textContent = r;
            dispMetabolicRisk.className = formatRiskClass(r);
        }

        // Metric badge
        dashboardGet('dispBMI').textContent = g.bmi;
        const bmiCat = dashboardGet('dispBMICat');
        bmiCat.textContent = g.bmi_category;
        bmiCat.className = 'badge';
        
        if (g.bmi_category === 'Normal') bmiCat.classList.add('normal-status');
        else if (g.bmi_category === 'Underweight') bmiCat.classList.add('warning-status');
        else bmiCat.classList.add('danger-status');

        dashboardGet('dispBMR').textContent = `${Math.round(g.bmr).toLocaleString()} kcal`;
        dashboardGet('dispTDEE').textContent = `${Math.round(g.tdee).toLocaleString()} kcal`;
        dashboardGet('dispTargetCals').textContent = `${Math.round(g.target_calories).toLocaleString()} kcal`;

        // Radial confidence
        const ring = dashboardGet('confidenceRing');
        const score = g.confidence_score;
        dashboardGet('dispConfidenceScore').textContent = `${score}%`;
        const offset = 251.2 - (251.2 * score / 100);
        if (ring) ring.style.strokeDashoffset = offset;

        // Advisory logs
        const advisoryDiv = dashboardGet('dispAdvisoryNotes');
        advisoryDiv.innerHTML = "";
        if (g.advisory_notes && g.advisory_notes.length > 0) {
            g.advisory_notes.forEach(note => {
                const p = document.createElement('p');
                p.className = 'warning-note text-warning fw-semibold mb-1';
                p.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${note}`;
                advisoryDiv.appendChild(p);
            });
        } else {
            const p = document.createElement('p');
            p.className = 'green-note text-success fw-semibold mb-0';
            p.innerHTML = `<i class="fa-solid fa-circle-check"></i> Standard healthy profile parameters. Safety engine approved.`;
            advisoryDiv.appendChild(p);
        }

        // Target macros percentages bars
        const cG = g.target_carbs;
        const pG = g.target_protein;
        const fG = g.target_fat;
        const totalMacroCals = (cG*4) + (pG*4) + (fG*9) || 1;

        dashboardGet('dispCarbsG').textContent = `${cG}g (${Math.round((cG*4/totalMacroCals)*100)}%)`;
        dashboardGet('dispProteinG').textContent = `${pG}g (${Math.round((pG*4/totalMacroCals)*100)}%)`;
        dashboardGet('dispFatG').textContent = `${fG}g (${Math.round((fG*9/totalMacroCals)*100)}%)`;

        dashboardGet('innerCarbsBar').style.width = `${(cG*4/totalMacroCals)*100}%`;
        dashboardGet('innerProteinBar').style.width = `${(pG*4/totalMacroCals)*100}%`;
        dashboardGet('innerFatBar').style.width = `${(fG*9/totalMacroCals)*100}%`;

        // Render Meals List
        const mealsList = dashboardGet('mealsList');
        mealsList.innerHTML = "";
        diet.forEach(meal => {
            const col = document.createElement('div');
            col.className = 'w-100';
            const meta = getMealMeta(meal.meal_type);
            const totalMacroCals = ((Number(meal.carbohydrates) || 0) * 4) + ((Number(meal.protein) || 0) * 4) + ((Number(meal.fats) || 0) * 9) || 1;
            const score = getMealScore(meal);
            const scoreLabel = score >= 90 ? 'Excellent balance' : score >= 80 ? 'Well balanced' : 'Needs tuning';
            const fiber = estimateFiber(meal);
            const foodsHtml = (meal.food_items || []).map(food => {
                const avatar = getFoodAvatar(food.name || '');
                const serving = `${Math.round(Number(food.serving_g) || 0)}g`;
                return `
                    <div class="ss-food-item">
                        <div class="ss-food-avatar" aria-hidden="true">${avatar}</div>
                        <div>
                            <div class="ss-food-name">${food.name}</div>
                            <div class="ss-food-serving">${serving}</div>
                        </div>
                    </div>
                `;
            }).join('');

            const substitutions = (meal.food_items || []).map(food => buildSubstitutions(food, meta.substitutions)).slice(0, 3);

            col.innerHTML = `
                <article class="ss-meal-card stagger-item w-100" data-meal="${meal.meal_type}">
                    <div class="ss-meal-left-col">
                        <div class="ss-meal-head">
                            <div class="ss-meal-main">
                                <div class="ss-meal-title">
                                    <span class="ss-meal-icon">${meta.icon}</span>
                                    <span class="ss-meal-name">${meal.meal_type}</span>
                                </div>
                                <div class="ss-meal-time">${meta.time}</div>
                            </div>
                            <div class="ss-meal-badges">
                                <span class="ss-meal-badge calories">${Math.round(meal.calories)} kcal</span>
                                <span class="ss-meal-badge protein">${Math.round(meal.protein)}g Protein</span>
                            </div>
                        </div>

                        <div class="ss-score-box mt-3">
                            <div>
                                <div class="ss-score-label">Nutrition Score</div>
                                <div class="ss-score-value">${score}/100</div>
                            </div>
                            <span class="ss-score-pill">${scoreLabel}</span>
                        </div>
                    </div>

                    <div class="ss-meal-mid-col">
                        <div class="ss-rail-title mb-2">Food Items</div>
                        <div class="ss-food-list">
                            ${foodsHtml}
                        </div>
                    </div>

                    <div class="ss-meal-right-col">
                        <div class="ss-macro-section">
                            <div class="ss-macro-row">
                                <div class="ss-macro-row-head"><span>Protein</span><strong>${Math.round(meal.protein)}g</strong></div>
                                <div class="ss-macro-track"><div class="ss-macro-fill protein" style="width: ${Math.round(((Number(meal.protein) || 0) * 4 / totalMacroCals) * 100)}%"></div></div>
                            </div>
                            <div class="ss-macro-row">
                                <div class="ss-macro-row-head"><span>Carbs</span><strong>${Math.round(meal.carbohydrates)}g</strong></div>
                                <div class="ss-macro-track"><div class="ss-macro-fill carbs" style="width: ${Math.round(((Number(meal.carbohydrates) || 0) * 4 / totalMacroCals) * 100)}%"></div></div>
                            </div>
                            <div class="ss-macro-row">
                                <div class="ss-macro-row-head"><span>Fat</span><strong>${Math.round(meal.fats)}g</strong></div>
                                <div class="ss-macro-track"><div class="ss-macro-fill fat" style="width: ${Math.round(((Number(meal.fats) || 0) * 9 / totalMacroCals) * 100)}%"></div></div>
                            </div>
                        </div>

                        <details class="ss-meal-details mt-3">
                            <summary><i class="fa-solid fa-chevron-down"></i> View Details</summary>
                            <div class="ss-details-grid">
                                <div class="ss-detail-chip"><span>Calories</span><strong>${Math.round(meal.calories)} kcal</strong></div>
                                <div class="ss-detail-chip"><span>Protein</span><strong>${Math.round(meal.protein)}g</strong></div>
                                <div class="ss-detail-chip"><span>Carbs</span><strong>${Math.round(meal.carbohydrates)}g</strong></div>
                                <div class="ss-detail-chip"><span>Fat</span><strong>${Math.round(meal.fats)}g</strong></div>
                                <div class="ss-detail-chip"><span>Fiber</span><strong>${fiber}g</strong></div>
                            </div>
                            <div class="ss-substitutions mt-3">
                                <h6>Food substitutions</h6>
                                <ul>
                                    ${substitutions.map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                        </details>

                        <div class="ss-meal-insight mt-3">
                            <strong>AI Insight</strong><br>
                            ${meta.insight}
                        </div>
                    </div>
                </article>
            `;
            mealsList.appendChild(col);
        });
        animateReveal(mealsList.querySelectorAll('.stagger-item'), 75);

        currentProfileSnapshot = { user: u, goals: g, diet, workout: data.workout };

        // Set up default day (Monday)
        renderWorkoutSchedule(data.workout, "Monday");
        
        // Progress logger form defaults
        dashboardGet('logWeight').value = u.weight;
        dashboardGet('logWater').value = u.water_intake;
        dashboardGet('logSleep').value = u.sleep_hours;
        dashboardGet('logCalConsumed').value = Math.round(g.target_calories);
        dashboardGet('logCalBurned').value = 0;
        dashboardGet('logDate').value = new Date().toISOString().split('T')[0];
    }

    const progressRangeToggle = dashboardGet('progressRangeToggle');
    if (progressRangeToggle) {
        progressRangeToggle.addEventListener('click', (e) => {
            const button = e.target.closest('.btn[data-range]');
            if (!button) return;
            progressRange = button.getAttribute('data-range') || 'week';
            progressRangeToggle.querySelectorAll('.btn').forEach((btn) => {
                btn.classList.toggle('active', btn === button);
            });
            renderProgressDashboard(progressHistoryCache);
        });
    }

    // Workout Nav triggers
    const workoutWeekNav = dashboardGet('workoutWeekNav');
    if (workoutWeekNav) {
        workoutWeekNav.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn[data-day]');
            if (btn && activeProfileId) {
                workoutWeekNav.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const day = btn.getAttribute('data-day');
                fetch(`/api/profile/${activeProfileId}`)
                    .then(res => res.json())
                    .then(data => {
                        if (currentProfileSnapshot) currentProfileSnapshot.workout = data.workout;
                        renderWorkoutSchedule(data.workout, day);
                    });
            }
        });
    }

    function renderWorkoutSchedule(workoutData, day) {
        const dayExercises = Array.isArray(workoutData?.[day]) ? workoutData[day] : [];
        const meta = getWorkoutMeta(day, dayExercises);
        const list = dashboardGet('exerciseCardsList');
        const safeText = (value) => String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');

        const primaryExercises = dayExercises.filter((exercise) => exercise.name !== 'Rest & Recovery');
        const visibleExercises = primaryExercises.length > 0 ? primaryExercises : dayExercises;
        const totalExercises = visibleExercises.length;
        const completedCount = totalExercises > 0
            ? visibleExercises.filter((exercise) => exercise.completed === true).length
            : 0;
        const completionPct = totalExercises > 0 ? Math.round((completedCount / totalExercises) * 100) : 0;
        const estimatedDuration = meta.duration || Math.max(25, totalExercises * 8);
        const summaryCalories = Math.round(
            visibleExercises.reduce((sum, exercise) => sum + (Number(exercise.calories_burned) || 0), 0) || meta.calories
        );
        const summaryVolume = Math.round(
            visibleExercises.reduce((sum, exercise) => {
                const sets = Number(exercise.sets) || 3;
                const reps = parseRepValue(exercise.reps);
                const exerciseInfo = getWorkoutExerciseMeta(exercise.name || '', exercise);
                const intensity = exerciseInfo.difficulty === 'Advanced' ? 72 : exerciseInfo.difficulty === 'Beginner' ? 45 : 58;
                return sum + (sets * reps * intensity);
            }, 0) || (totalExercises * estimatedDuration * 38)
        );

        dashboardGet('selectedDayTitle').textContent = `${day} - ${meta.focus}`;
        dashboardGet('workoutDuration').textContent = `${estimatedDuration} min`;
        dashboardGet('workoutCaloriesBurn').textContent = `${summaryCalories} kcal`;
        dashboardGet('workoutDifficulty').textContent = meta.difficulty;
        dashboardGet('workoutTargetMuscles').textContent = meta.muscles;
        dashboardGet('workoutProgressText').textContent = `${completedCount} of ${totalExercises} exercises completed`;
        dashboardGet('workoutProgressPct').textContent = `${completionPct}%`;
        dashboardGet('workoutProgressBar').style.width = `${completionPct}%`;
        dashboardGet('workoutSummaryExercises').textContent = `${totalExercises}`;
        dashboardGet('workoutSummaryTime').textContent = `${estimatedDuration} min`;
        dashboardGet('workoutSummaryCalories').textContent = `${summaryCalories} kcal`;
        dashboardGet('workoutSummaryVolume').textContent = `${summaryVolume.toLocaleString()} kg`;
        dashboardGet('workoutSummaryCompletion').textContent = `${completionPct}%`;
        dashboardGet('workoutCompletionRingValue').textContent = `${completionPct}%`;

        const workoutStatusBadge = dashboardGet('workoutStatusBadge');
        if (workoutStatusBadge) {
            workoutStatusBadge.innerHTML = completionPct === 100
                ? '<i class="fa-solid fa-trophy"></i> Session Complete'
                : completionPct > 0
                    ? `<i class="fa-solid fa-bolt"></i> In Progress (${completionPct}%)`
                    : '<i class="fa-solid fa-circle-check"></i> On Track';
        }

        const dayBadges = dashboardGet('workoutWeekNav')?.querySelectorAll('.btn') || [];
        dayBadges.forEach((btn) => {
            const isActive = btn.getAttribute('data-day') === day;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });

        if (!list) return;

        if (visibleExercises.length === 0) {
            list.innerHTML = `
                <article class="ss-exercise-card stagger-item" style="grid-column: 1 / -1;">
                    <div class="ss-exercise-card-head">
                        <div class="ss-exercise-thumb" aria-hidden="true">♻</div>
                        <div>
                            <div class="ss-exercise-name">Recovery Day</div>
                            <div class="ss-exercise-subtitle">Mobility • Stretching • Light movement</div>
                        </div>
                        <span class="ss-difficulty-badge beginner">Beginner</span>
                    </div>
                    <p class="ss-muted mb-0 mt-3">No exercises scheduled for this day. Use the time for walking, mobility, or active recovery.</p>
                </article>
            `;
            animateReveal(list.querySelectorAll('.stagger-item'), 70);
            return;
        }

        list.innerHTML = visibleExercises.map((exercise, index) => {
            const realIndex = dayExercises.indexOf(exercise);
            const info = getWorkoutExerciseMeta(exercise.name || '', exercise);
            const difficultyClass = getDifficultyClass(info.difficulty);
            const sets = Number(exercise.sets) || 3;
            const reps = exercise.reps || '10-12';
            const rest = exercise.rest_time || '60s';
            const calories = Number(exercise.calories_burned) || 0;
            const completed = exercise.completed === true;
            const targetMuscles = `${info.primary} • ${info.secondary}`;
            const alternateList = Array.isArray(info.alternatives) && info.alternatives.length > 0
                ? info.alternatives.join(' • ')
                : 'Bodyweight variation • Machine variation • Dumbbell variation';
            const cautionBanner = exercise.caution
                ? `<div class="alert alert-warning py-1.5 px-2.5 small mb-2 mt-2"><i class="fa-solid fa-triangle-exclamation me-1"></i> ${safeText(exercise.caution)}</div>`
                : '';

            return `
                <article class="ss-exercise-card stagger-item" ${index === 0 ? 'data-expanded="true"' : ''}>
                    <div class="ss-exercise-card-head">
                        <div class="ss-exercise-thumb" aria-hidden="true">${info.icon}</div>
                        <div>
                            <div class="ss-exercise-name">${safeText(exercise.name || 'Exercise')}</div>
                            <div class="ss-exercise-subtitle">${safeText(info.muscles || 'Full Body')}</div>
                        </div>
                        <span class="ss-difficulty-badge ${difficultyClass}">${safeText(info.difficulty)}</span>
                    </div>
                    ${cautionBanner}

                    <div class="ss-chip-row" aria-label="Workout metrics">
                        <span class="ss-exercise-chip">${sets} Sets</span>
                        <span class="ss-exercise-chip">${safeText(reps)} Reps</span>
                        <span class="ss-exercise-chip">${safeText(rest)} Rest</span>
                        <span class="ss-exercise-chip">${calories} kcal</span>
                    </div>

                    <div class="ss-chip-row d-flex justify-content-between align-items-center">
                        <span class="ss-exercise-chip">${safeText(targetMuscles)}</span>
                        <button type="button" class="btn btn-sm ${completed ? 'btn-success' : 'btn-outline-success'} rounded-pill toggle-exercise-btn" data-day="${safeText(day)}" data-index="${realIndex >= 0 ? realIndex : index}" data-completed="${completed ? 'true' : 'false'}">
                            <i class="fa-solid ${completed ? 'fa-circle-check' : 'fa-circle'} me-1"></i> ${completed ? 'Completed' : 'Mark Complete'}
                        </button>
                    </div>

                    <details class="ss-exercise-details" ${index === 0 ? 'open' : ''}>
                        <summary><i class="fa-solid fa-chevron-down"></i> View details</summary>
                        <div class="ss-exercise-details-grid">
                            <div class="ss-exercise-detail-block">
                                <span>Instructions</span>
                                <strong>${safeText(info.instructions)}</strong>
                            </div>
                            <div class="ss-exercise-detail-block">
                                <span>Common mistakes</span>
                                <strong>${safeText(info.mistakes)}</strong>
                            </div>
                            <div class="ss-exercise-detail-block">
                                <span>Target muscles</span>
                                <strong>${safeText(info.primary)} / ${safeText(info.secondary)}</strong>
                            </div>
                            <div class="ss-exercise-detail-block">
                                <span>Equipment needed</span>
                                <strong>${safeText(info.equipment)}</strong>
                            </div>
                        </div>
                        <div class="ss-exercise-detail-block mt-3">
                            <span>Alternatives</span>
                            <strong>${safeText(alternateList)}</strong>
                        </div>
                    </details>

                    <div class="ss-exercise-tip">
                        <strong>AI Coach Tip</strong><br>
                        ${safeText(info.tip)}
                    </div>
                </article>
            `;
        }).join('');

        animateReveal(list.querySelectorAll('.stagger-item'), 70);
    }

    // Delegated listener for Exercise Completion Toggle
    const exerciseCardsList = dashboardGet('exerciseCardsList');
    if (exerciseCardsList) {
        exerciseCardsList.addEventListener('click', (e) => {
            const btn = e.target.closest('.toggle-exercise-btn');
            if (!btn || !activeProfileId) return;
            const day = btn.getAttribute('data-day');
            const exerciseIndex = parseInt(btn.getAttribute('data-index'), 10);
            const currentlyCompleted = btn.getAttribute('data-completed') === 'true';

            fetch('/api/workout/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    profile_id: activeProfileId,
                    day: day,
                    exercise_index: exerciseIndex,
                    completed: !currentlyCompleted
                })
            })
            .then(res => res.json())
            .then(resData => {
                if (resData.workout) {
                    if (currentProfileSnapshot) currentProfileSnapshot.workout = resData.workout;
                    renderWorkoutSchedule(resData.workout, day);
                    showToast(!currentlyCompleted ? "Exercise marked completed!" : "Exercise marked queued.");
                }
            })
            .catch(err => console.error("Error toggling exercise:", err));
        });
    }

    // ----------------------------------------------------
    // API Call: Create Profile Submit
    // ----------------------------------------------------
    function handleFormSubmit(e) {
        e.preventDefault();
        if (!validateStep(currentStep)) return;

        const payload = {
            name: dashboardGet('name').value,
            age: dashboardGet('age').value,
            gender: dashboardGet('gender').value,
            height: dashboardGet('height').value,
            weight: dashboardGet('weight').value,
            fitness_goal: dashboardGet('fitness_goal').value,
            activity_level: dashboardGet('activity_level').value,
            workout_experience: dashboardGet('workout_experience').value,
            water_intake: dashboardGet('water_intake').value,
            sleep_hours: dashboardGet('sleep_hours').value,
            diet_preference: dashboardGet('diet_preference').value,
            medical_conditions: dashboardGet('medical_conditions').value,
            injuries: dashboardGet('injuries').value,
            allergies: dashboardGet('allergies').value
        };

        showToast("Generating personalized plans...");

        fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => {
            if (!res.ok) return res.json().then(err => { throw new Error(err.error || 'Server error') });
            return res.json();
        })
        .then(data => {
            showToast("Fitness profile created successfully!");
            setupForm.reset();
            loadUserProfilesList().then(() => {
                if (headerProfileSelect) {
                    headerProfileSelect.value = data.profile_id;
                    loadProfileDetails(data.profile_id);
                }
            });
        })
        .catch(err => alert("Failed to generate profile: " + err.message));
    }

    // ----------------------------------------------------
    // API Call: Daily Logs & Charts Rendering
    // ----------------------------------------------------
    const progressForm = dashboardGet('progressForm');
    if (progressForm) {
        progressForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!activeProfileId) return;

            const payload = {
                profile_id: activeProfileId,
                log_date: dashboardGet('logDate').value,
                weight: dashboardGet('logWeight').value,
                water_intake: dashboardGet('logWater').value,
                sleep_hours: dashboardGet('logSleep').value,
                calories_consumed: dashboardGet('logCalConsumed').value,
                calories_burned: dashboardGet('logCalBurned').value
            };

            fetch('/api/progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                const msg = dashboardGet('progressStatusMsg');
                msg.className = "alert alert-success mt-3 border border-white-10";
                msg.textContent = "Progress successfully logged!";
                msg.classList.remove('hidden');
                
                showToast("Daily metrics saved!");
                loadProgressLogs(activeProfileId);
                
                setTimeout(() => msg.classList.add('hidden'), 3000);
            })
            .catch(err => {
                const msg = dashboardGet('progressStatusMsg');
                msg.className = "alert alert-danger mt-3 border border-white-10";
                msg.textContent = "Error: " + err.message;
                msg.classList.remove('hidden');
            });
        });
    }

    let latestProgressAnalysis = null;
    let latestProgressPredictions = null;

    function loadProgressLogs(profileId) {
        Promise.all([
            fetch(`/api/progress/${profileId}`).then(res => res.json()),
            fetch(`/api/progress/analyze/${profileId}`).then(res => res.json()).catch(() => null),
            fetch(`/api/progress/predict/${profileId}`).then(res => res.json()).catch(() => null)
        ]).then(([history, analysis, mlPredict]) => {
            latestProgressAnalysis = analysis;
            latestProgressPredictions = mlPredict?.predictions || null;
            renderProgressDashboard(history);
        });
    }

    function renderProgressDashboard(history) {
        const normalized = normalizeProgressHistory(history);
        progressHistoryCache = normalized;

        const profile = currentProfileSnapshot || {};
        const user = profile.user || {};
        const goals = profile.goals || {};
        const filtered = getFilteredProgressHistory(normalized, progressRange);
        const chartHistory = filtered.length > 0 ? filtered : [{
            log_date: new Date().toISOString().split('T')[0],
            weight: toNumber(user.weight, 0),
            water_intake: toNumber(user.water_intake, 0),
            sleep_hours: toNumber(user.sleep_hours, 0),
            calories_consumed: toNumber(goals.target_calories, 0),
            calories_burned: 0
        }];
        const latest = getLatestEntry(filtered) || getLatestEntry(normalized) || chartHistory[0];
        const first = filtered[0] || normalized[0] || latest;
        const targetCalories = toNumber(goals.target_calories, toNumber(user.weight, 2000));
        const targetWater = Math.max(1, toNumber(user.hydration_target_l || user.water_intake, 3));
        const targetSleep = Math.max(1, toNumber(user.sleep_hours, 8));
        const currentWeight = toNumber(latest?.weight, toNumber(user.weight, 0));
        const startWeight = toNumber(first?.weight, currentWeight);
        const goalWeight = latestProgressPredictions && latestProgressPredictions['90_days']
            ? toNumber(latestProgressPredictions['90_days'], determineGoalWeight(user, currentWeight))
            : determineGoalWeight(user, currentWeight);
        const latestWater = toNumber(latest?.water_intake, targetWater);
        const latestSleep = toNumber(latest?.sleep_hours, targetSleep);
        const latestConsumed = toNumber(latest?.calories_consumed, targetCalories);
        const latestBurned = toNumber(latest?.calories_burned, 0);
        const calorieBalance = Math.round(latestConsumed - latestBurned);
        const waterPct = clampValue((latestWater / targetWater) * 100, 0, 100);
        const sleepPct = clampValue((latestSleep / targetSleep) * 100, 0, 100);
        const balancePct = clampValue(100 - (Math.abs(calorieBalance - targetCalories) / Math.max(targetCalories, 1) * 100), 0, 100);
        const loggingStreak = calculateLoggingStreak(normalized);
        const workoutDays = normalized.filter((entry) => toNumber(entry.calories_burned, 0) > 0).length;

        const workoutStreakBadge = dashboardGet('workoutStreakBadge');
        const workoutConsistencyBadge = dashboardGet('workoutConsistencyBadge');
        if (workoutStreakBadge) {
            workoutStreakBadge.innerHTML = `<i class="fa-solid fa-fire"></i> ${loggingStreak}-Day Streak`;
        }
        if (workoutConsistencyBadge) {
            const consistencyLabel = loggingStreak >= 5 ? 'High Consistency' : loggingStreak >= 2 ? 'Building Momentum' : 'Start Logging';
            workoutConsistencyBadge.innerHTML = `<i class="fa-solid fa-bolt"></i> ${consistencyLabel}`;
        }

        const averageWater = normalized.length ? normalized.reduce((sum, entry) => sum + toNumber(entry.water_intake, 0), 0) / normalized.length : latestWater;
        const averageSleep = normalized.length ? normalized.reduce((sum, entry) => sum + toNumber(entry.sleep_hours, 0), 0) / normalized.length : latestSleep;
        const waterGoalProgress = clampValue((averageWater / targetWater) * 100, 0, 100);
        const sleepGoalProgress = clampValue((averageSleep / targetSleep) * 100, 0, 100);
        const weightGoalProgress = goalWeight === currentWeight
            ? 100
            : (goalWeight < startWeight
                ? clampValue(((startWeight - currentWeight) / Math.max(startWeight - goalWeight, 0.1)) * 100, 0, 100)
                : clampValue(((currentWeight - startWeight) / Math.max(goalWeight - startWeight, 0.1)) * 100, 0, 100));

        const bmi = toNumber(goals.bmi, user.height ? (currentWeight / ((toNumber(user.height, 165) / 100) ** 2)) : 0);
        const bodyFatPercent = estimateBodyFatPercent(user, bmi);
        const muscleMassPercent = estimateMuscleMassPercent(bodyFatPercent);
        const recoveryScore = Math.round(clampValue((sleepPct * 0.55) + (waterPct * 0.45), 0, 100));
        const fitnessScore = clampValue(58 + (workoutDays * 4) + (loggingStreak * 1.5), 0, 100);
        const nutritionScore = clampValue(balancePct, 0, 100);
        const hydrationScore = clampValue(waterPct, 0, 100);
        const sleepScore = clampValue(sleepPct, 0, 100);
        const healthScore = Math.round((nutritionScore + fitnessScore + sleepScore + hydrationScore) / 4);
        const healthLabel = getProgressScoreLabel(healthScore);
        const progressWindowLabel = getRangeLabel(progressRange);
        const weightDelta = currentWeight - startWeight;
        const weekLabel = progressRange === 'year' ? 'year' : progressRange === 'month' ? 'month' : 'week';
        const weightTrendText = weightDelta < 0
            ? `↓ ${Math.abs(weightDelta).toFixed(1)} kg this ${weekLabel}`
            : weightDelta > 0
                ? `↑ ${Math.abs(weightDelta).toFixed(1)} kg this ${weekLabel}`
                : `→ Stable this ${weekLabel}`;

        dashboardGet('progressWeightValue').textContent = `${currentWeight.toFixed(1).replace(/\.0$/, '')} kg`;
        dashboardGet('progressWeightTrend').textContent = weightTrendText;
        dashboardGet('progressWeightBadge').textContent = weightDelta < 0 ? 'Trending down' : weightDelta > 0 ? 'Trending up' : 'Stable';
        dashboardGet('progressWeightBadge').className = `ss-kpi-badge ${weightDelta < 0 ? 'success' : weightDelta > 0 ? 'warning' : 'info'}`;
        dashboardGet('progressWaterValue').textContent = `${latestWater.toFixed(1).replace(/\.0$/, '')} / ${targetWater.toFixed(1).replace(/\.0$/, '')} L`;
        dashboardGet('progressWaterTrend').textContent = `${Math.round(waterPct)}% Complete`;
        dashboardGet('progressWaterBadge').textContent = waterPct >= 80 ? 'On track' : 'Needs attention';
        dashboardGet('progressWaterBadge').className = `ss-kpi-badge ${waterPct >= 80 ? 'success' : 'warning'}`;
        dashboardGet('progressSleepValue').textContent = `${latestSleep.toFixed(1).replace(/\.0$/, '')} hrs`;
        dashboardGet('progressSleepTrend').textContent = latestSleep >= targetSleep ? 'Excellent' : 'Below target';
        dashboardGet('progressSleepBadge').textContent = latestSleep >= targetSleep ? 'Recovered' : 'Needs rest';
        dashboardGet('progressSleepBadge').className = `ss-kpi-badge ${latestSleep >= targetSleep ? 'success' : 'warning'}`;
        dashboardGet('progressCaloriesValue').textContent = `${calorieBalance.toLocaleString()} kcal`;
        dashboardGet('progressCaloriesTrend').textContent = Math.abs(calorieBalance - targetCalories) <= 150 ? 'Within Target' : 'Off target';
        dashboardGet('progressCaloriesBadge').textContent = Math.abs(calorieBalance - targetCalories) <= 150 ? 'On track' : 'Adjust intake';
        dashboardGet('progressCaloriesBadge').className = `ss-kpi-badge ${Math.abs(calorieBalance - targetCalories) <= 150 ? 'success' : 'warning'}`;

        animateCountTo(dashboardGet('healthScoreValue'), healthScore, ' / 100', 0, 720);
        dashboardGet('healthScoreLabel').textContent = healthLabel;
        animateCountTo(dashboardGet('bodyCurrentWeight'), currentWeight, ' kg', 1, 720);
        dashboardGet('bodyGoalWeight').textContent = `${goalWeight.toFixed(1).replace(/\.0$/, '')} kg`;
        dashboardGet('bodyBMI').textContent = bmi ? bmi.toFixed(2) : '--';
        dashboardGet('bodyFatPct').textContent = `${bodyFatPercent.toFixed(1).replace(/\.0$/, '')}%`;
        dashboardGet('bodyMuscleMass').textContent = `${muscleMassPercent.toFixed(1).replace(/\.0$/, '')}%`;
        dashboardGet('bodyRecovery').textContent = `${recoveryScore}/100`;
        dashboardGet('waterProgressValue').textContent = `${Math.round(waterPct)}%`;
        dashboardGet('waterProgressCopy').textContent = `${latestWater.toFixed(1).replace(/\.0$/, '')} / ${targetWater.toFixed(1).replace(/\.0$/, '')} L`;
        dashboardGet('sleepProgressValue').textContent = `${latestSleep.toFixed(1).replace(/\.0$/, '')} hrs`;
        dashboardGet('sleepProgressCopy').textContent = latestSleep >= targetSleep ? 'Excellent recovery' : 'Needs more rest';
        dashboardGet('weightGoalLabel').textContent = `${currentWeight.toFixed(1).replace(/\.0$/, '')}kg → ${goalWeight.toFixed(1).replace(/\.0$/, '')}kg`;
        dashboardGet('hydrationGoalLabel').textContent = `${latestWater.toFixed(1).replace(/\.0$/, '')} / ${targetWater.toFixed(1).replace(/\.0$/, '')} L`;
        dashboardGet('sleepGoalLabel').textContent = `${latestSleep.toFixed(1).replace(/\.0$/, '')} / ${targetSleep.toFixed(1).replace(/\.0$/, '')} hrs`;
        dashboardGet('weightGoalPercent').textContent = `${Math.round(weightGoalProgress)}%`;
        dashboardGet('hydrationGoalPercent').textContent = `${Math.round(waterGoalProgress)}%`;
        dashboardGet('sleepGoalPercent').textContent = `${Math.round(sleepGoalProgress)}%`;
        dashboardGet('weightGoalFill').style.width = `${weightGoalProgress}%`;
        dashboardGet('hydrationGoalFill').style.width = `${waterGoalProgress}%`;
        dashboardGet('sleepGoalFill').style.width = `${sleepGoalProgress}%`;
        dashboardGet('scoreNutrition').textContent = `${Math.round(nutritionScore)}`;
        dashboardGet('scoreFitness').textContent = `${Math.round(fitnessScore)}`;
        dashboardGet('scoreSleep').textContent = `${Math.round(sleepScore)}`;
        dashboardGet('scoreHydration').textContent = `${Math.round(hydrationScore)}`;

        const radialOffset = 565 - (565 * healthScore / 100);
        const healthRing = dashboardGet('healthScoreRing');
        if (healthRing) healthRing.style.strokeDashoffset = `${radialOffset}`;
        const waterRing = dashboardGet('waterRadial');
        if (waterRing) waterRing.style.strokeDashoffset = `${565 - (565 * waterPct / 100)}`;
        const sleepRing = dashboardGet('sleepRadial');
        if (sleepRing) sleepRing.style.strokeDashoffset = `${565 - (565 * sleepPct / 100)}`;

        dashboardGet('milestoneStart').innerHTML = `<i class="fa-solid fa-seedling"></i> Start ${startWeight.toFixed(1).replace(/\.0$/, '')} kg`;
        dashboardGet('milestoneCurrent').innerHTML = `<i class="fa-solid fa-location-dot"></i> Current ${currentWeight.toFixed(1).replace(/\.0$/, '')} kg`;
        dashboardGet('milestoneGoal').innerHTML = `<i class="fa-solid fa-flag-checkered"></i> 90d ML Target ${goalWeight.toFixed(1).replace(/\.0$/, '')} kg`;

        const weightSparkline = dashboardGet('progressSparklineWeight');
        const waterSparkline = dashboardGet('progressSparklineWater');
        const sleepSparkline = dashboardGet('progressSparklineSleep');
        const caloriesSparkline = dashboardGet('progressSparklineCalories');
        renderSparkline(weightSparkline, filtered.map((entry) => entry.weight), chartPalette.primary, chartPalette.mutedFill);
        renderSparkline(waterSparkline, filtered.map((entry) => entry.water_intake), chartPalette.info, 'rgba(59, 130, 246, 0.12)');
        renderSparkline(sleepSparkline, filtered.map((entry) => entry.sleep_hours), chartPalette.accent, chartPalette.mutedFill);
        renderSparkline(caloriesSparkline, filtered.map((entry) => entry.calories_consumed), chartPalette.warning, 'rgba(245, 158, 11, 0.12)');

        const mcpVelocity = latestProgressAnalysis && latestProgressAnalysis.weekly_velocity_kg !== undefined
            ? `Weekly velocity: ${latestProgressAnalysis.weekly_velocity_kg > 0 ? '+' : ''}${latestProgressAnalysis.weekly_velocity_kg} kg/wk.`
            : '';
        const mlForecastText = latestProgressPredictions
            ? `ML Forecast: ${latestProgressPredictions['7_days']} kg (7d), ${latestProgressPredictions['30_days']} kg (30d), ${latestProgressPredictions['90_days']} kg (90d).`
            : '';
        const insightWeight = weightDelta < 0
            ? `You lost ${Math.abs(weightDelta).toFixed(1).replace(/\.0$/, '')} kg over the selected period. ${mcpVelocity}`
            : weightDelta > 0
                ? `Your weight changed by +${weightDelta.toFixed(1).replace(/\.0$/, '')} kg. ${mcpVelocity}`
                : `Your weight is stable across the selected period. ${mcpVelocity}`;
        const insightRecommendation = mlForecastText || (waterPct < 80
            ? `Increase water intake by ${Math.max(1, Math.ceil(targetWater - latestWater)).toFixed(0)} L/day to improve recovery and energy.`
            : 'Keep protein and recovery habits consistent to preserve momentum.');
        const mcpAlerts = Array.isArray(latestProgressAnalysis?.alerts) && latestProgressAnalysis.alerts.length > 0
            ? latestProgressAnalysis.alerts.join(' ')
            : ((waterPct < 70 || sleepPct < 75 || Math.abs(calorieBalance - targetCalories) > 300)
                ? `Water or recovery dipped below target in the selected period. Review the flagged metrics.`
                : 'Progress MCP Audit: All compliance and safety metrics within healthy bounds.');

        dashboardGet('progressInsightPrimary').textContent = insightWeight;
        dashboardGet('progressInsightSecondary').textContent = insightRecommendation;
        dashboardGet('progressInsightWarning').textContent = mcpAlerts;

        const activityTimeline = dashboardGet('activityTimeline');
        if (activityTimeline) {
            const recentEntries = normalized.slice(-3).reverse();
            activityTimeline.innerHTML = recentEntries.length > 0
                ? recentEntries.map((entry) => {
                    const actions = [
                        `Logged weight ${toNumber(entry.weight, currentWeight).toFixed(1).replace(/\.0$/, '')} kg`
                    ];
                    if (toNumber(entry.calories_burned, 0) > 0) {
                        actions.push(`Completed workout (${Math.round(entry.calories_burned)} kcal burned)`);
                    }
                    if (toNumber(entry.water_intake, 0) >= targetWater) {
                        actions.push('Reached water goal');
                    }
                    if (toNumber(entry.sleep_hours, 0) >= targetSleep) {
                        actions.push(`Slept ${toNumber(entry.sleep_hours, 0).toFixed(1).replace(/\.0$/, '')} hours`);
                    }
                    return `
                        <div class="ss-timeline-item">
                            <time>${formatDayLabel(entry.parsedDate)}</time>
                            <strong>${entry.parsedDate.toLocaleDateString(undefined, { weekday: 'long' })}</strong>
                            <ul>
                                ${actions.map((action) => `<li>✓ ${action}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }).join('')
                : '<div class="ss-timeline-item"><strong>No progress entries yet.</strong><p class="mb-0 mt-2 text-secondary">Start logging to see recent activity here.</p></div>';
        }

        renderProgressCharts(chartHistory);
        dashboardGet('progressRangeToggle')?.querySelectorAll('.btn').forEach((btn) => {
            btn.classList.toggle('active', btn.getAttribute('data-range') === progressRange);
        });
        dashboardGet('progressRangeToggle') && (dashboardGet('progressRangeToggle').title = progressWindowLabel);
    }

    function renderProgressCharts(history) {
        const dates = history.map((entry) => entry.log_date);
        const weights = history.map((entry) => toNumber(entry.weight, 0));
        const waters = history.map((entry) => toNumber(entry.water_intake, 0));
        const sleeps = history.map((entry) => toNumber(entry.sleep_hours, 0));
        const profile = currentProfileSnapshot || {};
        const fallbackTarget = determineGoalWeight(profile.user || {}, toNumber(weights[weights.length - 1], 0));
        const targetWeight = latestProgressPredictions && latestProgressPredictions['90_days']
            ? toNumber(latestProgressPredictions['90_days'], fallbackTarget)
            : fallbackTarget;
        const goalLine = dates.map(() => targetWeight);
        const projectedLine = dates.length > 1
            ? dates.map((_, index) => weights[0] + (((targetWeight - weights[0]) / (dates.length - 1)) * index))
            : [targetWeight];

        const gridColor = 'rgba(0,0,0,0.06)';
        const textColor = '#52606d';

        if (weightChart) weightChart.destroy();
        if (lifestyleChart) lifestyleChart.destroy();

        const ctxW = dashboardGet('weightChart')?.getContext('2d');
        if (ctxW) {
            weightChart = new Chart(ctxW, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [
                        {
                            label: 'Weight (kg)',
                            data: weights,
                            borderColor: chartPalette.primary,
                            backgroundColor: chartPalette.mutedFill,
                            borderWidth: 2.8,
                            fill: true,
                            tension: 0.35,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: '#ffffff',
                            pointBorderColor: chartPalette.primary
                        },
                        {
                            label: 'Goal line',
                            data: goalLine,
                            borderColor: '#64748B',
                            borderDash: [6, 6],
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        },
                        {
                            label: 'Projected target',
                            data: projectedLine,
                            borderColor: chartPalette.warning,
                            borderDash: [4, 6],
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: textColor,
                                font: { family: 'Inter, sans-serif' }
                            }
                        }
                    },
                    scales: {
                        x: { grid: { color: gridColor }, ticks: { color: textColor } },
                        y: { grid: { color: gridColor }, ticks: { color: textColor } }
                    }
                }
            });
        }

        const maxWater = waters.length ? Math.max(...waters.map((value) => parseFloat(value) || 0)) : 1;
        const maxSleep = sleeps.length ? Math.max(...sleeps.map((value) => parseFloat(value) || 0)) : 1;
        const suggestedWaterMax = Math.max(2, Math.ceil(maxWater * 1.3));
        const suggestedSleepMax = Math.max(8, Math.ceil(maxSleep * 1.4));

        const ctxL = dashboardGet('lifestyleChart')?.getContext('2d');
        if (ctxL) {
            lifestyleChart = new Chart(ctxL, {
                data: {
                    labels: dates,
                    datasets: [
                        {
                            type: 'bar',
                            label: 'Water (L)',
                            data: waters,
                            backgroundColor: chartPalette.info,
                            borderRadius: 8,
                            yAxisID: 'y',
                            order: 1,
                            barPercentage: 0.6,
                            categoryPercentage: 0.6,
                            borderSkipped: false
                        },
                        {
                            type: 'line',
                            label: 'Sleep (hrs)',
                            data: sleeps,
                            borderColor: chartPalette.primary,
                            borderWidth: 2.5,
                            backgroundColor: chartPalette.mutedFill,
                            fill: false,
                            yAxisID: 'y1',
                            order: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: '#ffffff',
                            pointBorderColor: chartPalette.primary,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: textColor,
                                font: { family: 'Inter, sans-serif' }
                            }
                        }
                    },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: textColor } },
                        y: {
                            type: 'linear',
                            position: 'left',
                            grid: { color: gridColor },
                            ticks: { color: textColor },
                            title: { display: true, text: 'Water (L)', color: textColor },
                            beginAtZero: true,
                            suggestedMax: suggestedWaterMax
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            grid: { display: false },
                            ticks: { color: textColor },
                            title: { display: true, text: 'Sleep (Hours)', color: textColor },
                            beginAtZero: true,
                            suggestedMax: suggestedSleepMax
                        }
                    }
                }
            });
        }
    }

    // ----------------------------------------------------
    // Star Rating Toggle & Feedback Submit
    // ----------------------------------------------------
    const starSelector = dashboardGet('starRatingSelector');
    let ratingValue = 5;

    if (starSelector) {
        starSelector.addEventListener('click', (e) => {
            if (e.target.classList.contains('star-btn')) {
                const val = parseInt(e.target.getAttribute('data-value'));
                ratingValue = val;
                dashboardGet('selectedRatingVal').value = val;
                updateStarsUI(val);
            }
        });
    }

    function updateStarsUI(val) {
        const stars = starSelector.querySelectorAll('.star-btn');
        stars.forEach((star, idx) => {
            if (idx < val) {
                star.className = 'fa-solid fa-star star-btn fs-3 text-body';
            } else {
                star.className = 'fa-regular fa-star star-btn fs-3 text-secondary';
            }
        });
    }

    if (starSelector) {
        updateStarsUI(ratingValue);
    }

    const feedbackForm = dashboardGet('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!activeProfileId) return;

            const payload = {
                profile_id: activeProfileId,
                rating: ratingValue,
                comments: dashboardGet('feedbackComments').value
            };

            fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                const msg = dashboardGet('feedbackStatusMsg');
                msg.className = "alert alert-success mt-3 border border-white-10";
                msg.textContent = "Review successfully submitted!";
                msg.classList.remove('hidden');
                
                dashboardGet('feedbackComments').value = "";
                ratingValue = 5;
                updateStarsUI(5);
                
                showToast("Feedback submitted!");
                loadFeedbackTimeline(activeProfileId);
                
                setTimeout(() => msg.classList.add('hidden'), 3000);
            })
            .catch(err => {
                const msg = dashboardGet('feedbackStatusMsg');
                msg.className = "alert alert-danger mt-3 border border-white-10";
                msg.textContent = "Submission failed: " + err.message;
                msg.classList.remove('hidden');
            });
        });
    }

    function loadFeedbackTimeline(profileId) {
        fetch(`/api/feedback/${profileId}`)
            .then(res => res.json())
            .then(reviews => {
                const timeline = dashboardGet('feedbackTimeline');
                timeline.innerHTML = "";
                
                if (reviews.length === 0) {
                    timeline.innerHTML = '<p class="text-secondary small italic text-center p-4">No reviews recorded yet for this profile.</p>';
                    return;
                }

                reviews.forEach(r => {
                    let starsHtml = "";
                    for (let i = 1; i <= 5; i++) {
                        if (i <= r.rating) starsHtml += '<i class="fa-solid fa-star text-warning"></i>';
                        else starsHtml += '<i class="fa-regular fa-star text-secondary"></i>';
                    }
                    
                    const block = document.createElement('div');
                    block.className = "p-3 bg-glass-compact border border-white-10 rounded-3 stagger-item";
                    block.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center mb-1.5">
                            <div class="small-stars d-flex gap-0.5">${starsHtml}</div>
                            <span class="text-secondary small" style="font-size: 0.75rem;">${r.log_date}</span>
                        </div>
                        <p class="mb-0 text-white small" style="line-height: 1.4;">${r.comments || 'No comment provided.'}</p>
                    `;
                    timeline.appendChild(block);
                });
                animateReveal(timeline.querySelectorAll('.stagger-item'), 60);
            })
            .catch(err => console.error("Error loading reviews:", err));
    }

    // ----------------------------------------------------
    // AI Health Coach Chatbot (RAG + MCP)
    // ----------------------------------------------------
    const chatbotForm = dashboardGet('chatbotForm');
    const chatbotInput = dashboardGet('chatbotInput');
    const chatbotMessages = dashboardGet('chatbotMessages');

    function appendChatMessage(role, text, sourceTag = '') {
        if (!chatbotMessages) return;
        const wrapper = document.createElement('div');
        wrapper.className = 'p-3 rounded-3 border';
        if (role === 'user') {
            wrapper.style.background = '#ecfdf5';
            wrapper.style.borderColor = '#a7f3d0';
            wrapper.style.alignSelf = 'flex-end';
            wrapper.style.maxWidth = '85%';
            wrapper.innerHTML = `<div class="fw-bold small text-success mb-1"><i class="fa-solid fa-user me-1"></i> You</div><p class="mb-0 small text-dark"></p>`;
            wrapper.querySelector('p').textContent = text;
        } else {
            wrapper.style.background = '#ffffff';
            wrapper.style.borderColor = '#e2e8f0';
            wrapper.style.maxWidth = '92%';
            const srcBadge = sourceTag ? `<span class="badge bg-light text-secondary border ms-2">${sourceTag}</span>` : '';
            wrapper.innerHTML = `<div class="fw-bold small text-success mb-1"><i class="fa-solid fa-robot me-1"></i> Sehat Saathi Coach ${srcBadge}</div><p class="mb-0 small text-secondary" style="white-space: pre-line;"></p>`;
            wrapper.querySelector('p').textContent = text;
        }
        chatbotMessages.appendChild(wrapper);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function sendChatbotMessage(messageText) {
        if (!messageText || !messageText.trim()) return;
        appendChatMessage('user', messageText.trim());
        if (chatbotInput) chatbotInput.value = '';

        fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile_id: activeProfileId,
                message: messageText.trim()
            })
        })
        .then(res => res.json())
        .then(data => {
            appendChatMessage('bot', data.reply || 'Unable to generate response right now.', data.source || 'RAG MCP');
        })
        .catch(err => {
            appendChatMessage('bot', 'Error connecting to AI Health Coach: ' + err.message, 'Error');
        });
    }

    if (chatbotForm) {
        chatbotForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendChatbotMessage(chatbotInput?.value || '');
        });
    }

    document.querySelectorAll('.chatbot-quick-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            if (prompt) sendChatbotMessage(prompt);
        });
    });

    // ----------------------------------------------------
    // Dashboard Search Filter
    // ----------------------------------------------------
    const dashboardSearchInput = dashboardGet('dashboardSearchInput');
    if (dashboardSearchInput) {
        dashboardSearchInput.addEventListener('input', (e) => {
            const query = (e.target.value || '').trim().toLowerCase();
            document.querySelectorAll('#mealsList .ss-meal-card').forEach(card => {
                const text = card.textContent.toLowerCase();
                card.parentElement.style.display = (!query || text.includes(query)) ? '' : 'none';
            });
            document.querySelectorAll('#exerciseCardsList .ss-exercise-card').forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = (!query || text.includes(query)) ? '' : 'none';
            });
        });
    }

    // ----------------------------------------------------
    // Toast Alert Notification
    // ----------------------------------------------------
    function showToast(message) {
        const toastEl = dashboardGet('customToast');
        const msgEl = dashboardGet('toastMessage');
        if (toastEl && msgEl) {
            msgEl.textContent = message;
            const bsToast = new bootstrap.Toast(toastEl);
            bsToast.show();
        }
    }
});


