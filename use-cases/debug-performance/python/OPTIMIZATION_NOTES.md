# Optimization Notes: Product Combination Search

## Summary
The original implementation evaluated every product against every other product and then scanned the growing results list to prevent duplicate pairs. This caused quadratic-to-cubic behavior as input size grew.

## What Changed
1. **Single-pass pair enumeration**
   - Changed the nested loops to iterate `j` from `i + 1` instead of across the full list.
   - This ensures each pair is evaluated exactly once and removes the need for duplicate checks.

2. **Removed expensive duplicate scanning**
   - The `any(...)` scan over the `results` list was removed.
   - Duplicate prevention is now guaranteed by the loop structure, which is $O(n^2)$ instead of potential $O(n^3)$.

3. **Reduced repeated work**
   - Precomputed `lower_bound`, `upper_bound`, and `total_products` outside loops.
   - Cached `product1` and `price1` per outer loop iteration.
   - Added `progress_step` parameter so progress logging can be tuned or disabled.

## Performance Impact (Big‑O)
- **Before:**
  - Pair generation: $O(n^2)$
  - Duplicate scan in `results`: up to $O(n)$ per pair
  - **Worst case:** $O(n^3)$

- **After:**
  - Pair generation: $O(n^2)$
  - No duplicate scan
  - **Overall:** $O(n^2)$

## Design Patterns / Practices Applied
- **Single Responsibility:** Pair enumeration now focuses only on creating valid pairs; duplicate detection is removed.
- **Algorithmic Optimization:** Reduced overall complexity by restructuring iteration order.
- **Configurable Behavior:** `progress_step` allows turning logging on/off without code changes.

## Next Possible Enhancements
- **Two‑sum with buckets or sorting:** If you can sort by price, you could reduce work further by pruning based on bounds.
- **Parallelization:** For very large inputs, chunk the list and process in parallel.
- **Memory optimization:** Yield pairs as a generator instead of storing all results if full list isn’t needed.

## How to Measure Improvements
- Use `cProfile` to compare total time before and after.
- Use `line_profiler` to confirm hot loops were reduced.
- Use `timeit` for focused micro‑benchmarks.
