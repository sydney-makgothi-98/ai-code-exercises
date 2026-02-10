// Sorting function
// Verification notes:
// 1) Collaborative Solution Verification: compared expected merge behavior (append remaining
//    elements from either side) against the current logic and identified incorrect index updates.
// 2) Learning Through Alternative Approaches: cross-checked with an alternative reference merge
//    implementation (iterative merge) to confirm correct index increments and tail-copy behavior.
// 3) Developing a Critical Eye: traced a minimal counterexample (left=[1], right=[2,3]) and
//    observed that the loop never progresses on the left, revealing the bug.
// What we learned: tail-merge loops must advance the same pointer they read from, and merge logic
// should be validated with small, edge-case arrays.
function mergeSort(arr) {
  if (arr.length <= 1) return arr;

  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));

  return merge(left, right);
}

function merge(left, right) {
  let result = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    if (left[i] < right[j]) {
      result.push(left[i]);
      i++;
    } else {
      result.push(right[j]);
      j++;
    }
  }

  // Bug: Only one of these loops will execute
  while (i < left.length) {
    result.push(left[i]);
    i++;
  }

  while (j < right.length) {
    result.push(right[j]);
    j++;
  }

  return result;
}