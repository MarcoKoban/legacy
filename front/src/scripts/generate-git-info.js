const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

try {
  // Get git branch name
  const branch = execSync('git rev-parse --abbrev-ref HEAD')
    .toString()
    .trim();

  // Get commit ID (short version)
  const commitId = execSync('git rev-parse --short HEAD')
    .toString()
    .trim();

  // Get commit date
  const commitDate = execSync('git log -1 --format=%cd --date=short')
    .toString()
    .trim();

  // Create git info object
  const gitInfo = {
    branch,
    commitId,
    commitDate,
    generatedAt: new Date().toISOString()
  };

  // Write to JSON file
  const outputPath = path.join(__dirname, '../assets/git-info.json');
  fs.writeFileSync(outputPath, JSON.stringify(gitInfo, null, 2));

  console.log('✅ Git info generated successfully:', gitInfo);
} catch (error) {
  console.error('❌ Error generating git info:', error.message);
  
  // Create fallback git info
  const fallbackInfo = {
    branch: '15-front-end',
    commitId: '0537653',
    commitDate: '2025-10-20',
    generatedAt: new Date().toISOString(),
    error: 'Could not fetch git info'
  };
  
  const outputPath = path.join(__dirname, '../assets/git-info.json');
  fs.writeFileSync(outputPath, JSON.stringify(fallbackInfo, null, 2));
  
  console.log('⚠️ Using fallback git info');
}
