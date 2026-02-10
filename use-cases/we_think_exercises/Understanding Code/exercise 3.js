function calculateStatsForKey(userData, key) {
  let total = 0;
  for (let i = 0; i < userData.length; i++) {
    total += userData[i][key];
  }
  const average = total / userData.length;

  let highest = userData[0][key];
  for (let i = 1; i < userData.length; i++) {
    if (userData[i][key] > highest) {
      highest = userData[i][key];
    }
  }

  return { average, highest };
}

function calculateUserStatistics(userData) {
  const ageStats = calculateStatsForKey(userData, 'age');
  const incomeStats = calculateStatsForKey(userData, 'income');
  const scoreStats = calculateStatsForKey(userData, 'score');

  return {
    age: ageStats,
    income: incomeStats,
    score: scoreStats
  };
}