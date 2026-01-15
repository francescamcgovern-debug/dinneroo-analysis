# Feedback Report

**Deliverable:** DELIVERABLES/incoming/dish_analysis_colleague.pptx
**Reviewed:** 2026-01-12
**Overall Status:** CRITICAL ISSUES

## Summary

| Category | Status | Issues |
|----------|--------|--------|
| Data Accuracy | ❌ | 10 |
| Conflicting Stories | ✅ | 0 |
| Evidence Standards | ❌ | 12 |
| Triangulation Violations | ❌ | 1 |
| Data Source Misuse | ✅ | 0 |
| Survivorship Bias | ✅ | 0 |
| Stated vs Revealed | ✅ | 0 |
| Anti-Replication | ✅ | 10 |
| Methodology Drift | ✅ | 6 |

## Issues

1. **Critical — Data Accuracy** (Slide 7): Deck claim drifts from Cursor truth: cuisines_min
   - Evidence: Deck: 4+ cuisines (4.0+) vs Cursor: 5 (config/mvp_thresholds.json:mvp_criteria.cuisines_min.value)
   - Recommendation: Update deck to use cuisines_min=5+ (Cursor target).

2. **Critical — Data Accuracy** (Slide 7): Deck claim drifts from Cursor truth: dishes_min
   - Evidence: Deck: 10+ dishes (10.0+) vs Cursor: 21 (config/mvp_thresholds.json:mvp_criteria.dishes_min.value)
   - Recommendation: Update deck to use dishes_min=21+ (Cursor target).

3. **Critical — Data Accuracy** (Slide 7): Deck claim drifts from Cursor truth: dish_group_demand_boosters.dishes
   - Evidence: Deck: Katsu, Sushi, Pho, Biryani, Pizza, Pasta, Lasagne, Protein & Veg () vs Cursor: See config/mvp_thresholds.json:dish_types.* (config/mvp_thresholds.json:dish_types)
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

4. **Critical — Data Accuracy** (Slide 7): Deck claim drifts from Cursor truth: dish_group_preference_drivers.dishes
   - Evidence: Deck: Shepherd's Pie, Grain Bowl, Fajitas, Quesadillas, Shawarma, Rice Bowl, Fried Rice, East Asian Curry () vs Cursor: See config/mvp_thresholds.json:dish_types.* (config/mvp_thresholds.json:dish_types)
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

5. **Critical — Data Accuracy** (Slide 9): Deck claim drifts from Cursor truth: cuisines_min
   - Evidence: Deck: 4+ cuisines (4.0+) vs Cursor: 5 (config/mvp_thresholds.json:mvp_criteria.cuisines_min.value)
   - Recommendation: Update deck to use cuisines_min=5+ (Cursor target).

6. **Critical — Data Accuracy** (Slide 9): Deck claim drifts from Cursor truth: dishes_min
   - Evidence: Deck: 10+ dishes (10.0+) vs Cursor: 21 (config/mvp_thresholds.json:mvp_criteria.dishes_min.value)
   - Recommendation: Update deck to use dishes_min=21+ (Cursor target).

7. **Critical — Data Accuracy** (Slide 10): Deck claim drifts from Cursor truth: dish_group_demand_boosters.dishes
   - Evidence: Deck: Katsu, Sushi, Pho, Biryani, Pizza, Pasta, Lasagne, Protein & Veg () vs Cursor: See config/mvp_thresholds.json:dish_types.* (config/mvp_thresholds.json:dish_types)
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

8. **Critical — Data Accuracy** (Slide 10): Deck claim drifts from Cursor truth: dish_group_preference_drivers.dishes
   - Evidence: Deck: Shepherd's Pie, Grain Bowl, Rice Bowl, Fried Rice, East Asian Curry, Fajitas, Quesadillas, Shawarma () vs Cursor: See config/mvp_thresholds.json:dish_types.* (config/mvp_thresholds.json:dish_types)
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

9. **Critical — Data Accuracy** (Slide 11): Deck claim drifts from Cursor truth: scoring_inputs_list
   - Evidence: Deck: Deck lists demand indicators (avg sales per dish, % zones top3, open-text requests) and preference indicators (rating, meal satisfaction, repeat intent, family suitability). () vs Cursor: {"family_performers": ["adult_satisfaction", "fussy_eater_friendly", "kids_happy", "orders_per_zone", "portions_adequate"], "couple_performers": ["adult_appeal", "adult_satisfaction", "orders_per_zone", "rating"], "recruitment_priorities": ["framework_score", "fussy_eater_friendly", "gap_score", "latent_demand_mentions", "non_dinneroo_demand_proxy", "partner_capability"]} (config/scoring_framework_v3.json:lists.*.factors)
   - Recommendation: If the deck should reflect Cursor scoring, replace the stated inputs with the segment-specific factor sets and cite where each factor is sourced (survey/orders/latent demand).

10. **Critical — Data Accuracy** (Slide 12): Deck claim drifts from Cursor truth: scoring_method_index_to_1_mean
   - Evidence: Deck: Demand strength calculated by indexing metrics to avg=1 and taking mean; same for Cx preference (deck footnote). () vs Cursor: percentile_based (config/scoring_framework_v3.json:scoring_method.type)
   - Recommendation: If the deck should reflect Cursor scoring, replace the indexing/mean method description with percentile-based 1–5 scoring and list-specific weighted factors.

11. **Warning — Evidence Standards** (Slide 7): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Core Drivers coverage target = 100.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

12. **Warning — Evidence Standards** (Slide 7): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Demand Boosters coverage target = 75.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

13. **Warning — Evidence Standards** (Slide 7): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Preference Drivers coverage target = 50.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

14. **Warning — Evidence Standards** (Slide 9): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Deck: % of active zones meeting partners threshold = 70.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

15. **Warning — Evidence Standards** (Slide 9): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Deck: % of active zones meeting cuisines threshold = 54.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

16. **Warning — Evidence Standards** (Slide 9): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Deck: % of active zones meeting dishes threshold = 54.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

17. **Warning — Evidence Standards** (Slide 9): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Deck: % of active zones meeting all 3 thresholds = 41.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

18. **Warning — Evidence Standards** (Slide 10): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Noodles group coverage target = 100.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

19. **Warning — Evidence Standards** (Slide 10): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Katsu group coverage target = 75.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

20. **Warning — Evidence Standards** (Slide 10): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Shepherd group coverage target = 50.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

21. **Warning — Evidence Standards** (Slide 10): Percent claim lacks a clear denominator + traceable source export
   - Evidence: Claim: Pastry Pie group coverage target = 0.0% (no established Cursor export linked).
   - Recommendation: Add denominator (zone count type: total/supply/live/analysis), sample size n, and provenance to an exported file (or label as deck-calculated).

22. **Warning — Triangulation Violations** (Slide 11): Deck references pre-launch stated-preference signals; triangulation requirements must be explicit
   - Evidence: Deck mentions pre-launch research / suitability. Cursor rules require triangulation with behavioral data.
   - Recommendation: Add explicit triangulation note + avoid using OG/pre-launch as sole basis for recommendations.

23. **Info — Anti-Replication** (Slide 3): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

24. **Info — Anti-Replication** (Slide 4): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

25. **Info — Anti-Replication** (Slide 5): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

26. **Info — Methodology Drift** (Slide 7): Scoring methodology described in deck differs from Cursor scoring config
   - Evidence: Deck metric: dish_group_demand_boosters.dishes; Cursor source: config/mvp_thresholds.json:dish_types
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

27. **Info — Methodology Drift** (Slide 7): Scoring methodology described in deck differs from Cursor scoring config
   - Evidence: Deck metric: dish_group_preference_drivers.dishes; Cursor source: config/mvp_thresholds.json:dish_types
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

28. **Info — Methodology Drift** (Slide 10): Scoring methodology described in deck differs from Cursor scoring config
   - Evidence: Deck metric: dish_group_demand_boosters.dishes; Cursor source: config/mvp_thresholds.json:dish_types
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

29. **Info — Methodology Drift** (Slide 10): Scoring methodology described in deck differs from Cursor scoring config
   - Evidence: Deck metric: dish_group_preference_drivers.dishes; Cursor source: config/mvp_thresholds.json:dish_types
   - Recommendation: Reconcile dish group assignments to match config/mvp_thresholds.json dish_types categories (Anna taxonomy).

30. **Info — Methodology Drift** (Slide 11): Scoring methodology described in deck differs from Cursor scoring config
   - Evidence: Deck metric: scoring_inputs_list; Cursor source: config/scoring_framework_v3.json:lists.*.factors
   - Recommendation: If the deck should reflect Cursor scoring, replace the stated inputs with the segment-specific factor sets and cite where each factor is sourced (survey/orders/latent demand).

31. **Info — Methodology Drift** (Slide 12): Scoring methodology described in deck differs from Cursor scoring config
   - Evidence: Deck metric: scoring_method_index_to_1_mean; Cursor source: config/scoring_framework_v3.json:scoring_method.type
   - Recommendation: If the deck should reflect Cursor scoring, replace the indexing/mean method description with percentile-based 1–5 scoring and list-specific weighted factors.

32. **Info — Anti-Replication** (Slide 14): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

33. **Info — Anti-Replication** (Slide 15): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

34. **Info — Anti-Replication** (Slide 16): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

35. **Info — Anti-Replication** (Slide 17): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

36. **Info — Anti-Replication** (Slide 18): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

37. **Info — Anti-Replication** (Slide 21): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

38. **Info — Anti-Replication** (Slide 24): Deck uses an 'As at' date; ensure it matches data freshness and exported run date
   - Evidence: Slide contains: 'As at ...' but no provenance link to pipeline run or file dates.
   - Recommendation: Add a footnote or appendix line citing data extract date and source file(s).

39. **Info — Evidence Standards** (All slides): Zone denominators must be explicit in any % statements
   - Evidence: Canonical counts (dashboard_metrics.json): total=1306, supply_with_partners=434, live_with_orders=201.
   - Recommendation: For any % zone metric in the deck, explicitly state which denominator is used.
