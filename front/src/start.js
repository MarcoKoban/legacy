const fs = require('fs');
const readline = require('readline');
const { spawn, execSync } = require('child_process');

// Generate git info before starting
try {
  console.log('🔄 Generating git info...');
  execSync('node src/scripts/generate-git-info.js', { stdio: 'inherit' });
} catch (error) {
  console.warn('⚠️ Could not generate git info:', error.message);
}

const languages = Object.freeze({
  FR: 'fr',
  EN: 'en',
  ES: 'es',
  FI: 'fi',
  CO: 'co',
  DE: 'de',
  IT: 'it',
  LV: 'lv',
  SV: 'sv'
})

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const promptMessage = fs.readFileSync('./src/assets/lang_prompt.txt', 'utf-8');
console.log(promptMessage);

rl.question('? ', (answer) => {
  let lang = answer.trim().toLowerCase();
  if (!Object.values(languages).includes(lang)) {
    console.log('Invalid choice, defaulting to EN.');
    lang = 'en';
  }
  // Write the selected language to lang.txt
  fs.writeFileSync('./src/assets/translate/lang.txt', lang);

  // New session marker
  const bootId = Date.now().toString();
  fs.writeFileSync('./src/assets/translate/boot.txt', bootId);
  rl.close();

  // Start Angular dev server on port 2316
  const ngPath = require.resolve('@angular/cli/bin/ng');
  const ng = spawn('node', [ngPath, 'serve'], { stdio: 'inherit' });
  ng.on('close', code => process.exit(code));
});