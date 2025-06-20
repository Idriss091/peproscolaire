const fs = require('fs');
const path = require('path');

console.log('🔍 Checking TypeScript files for "eval" keyword usage...\n');

// Read the grades.ts file
const gradesPath = path.join(__dirname, 'peproscolaire-ui/src/stores/grades.ts');
const content = fs.readFileSync(gradesPath, 'utf8');

// Check for 'eval' usage as a variable name
const lines = content.split('\n');
let evalUsageFound = false;
const evalPattern = /\beval\s*=>/;

lines.forEach((line, index) => {
    if (evalPattern.test(line)) {
        console.log(`❌ Line ${index + 1}: Found 'eval' keyword usage: ${line.trim()}`);
        evalUsageFound = true;
    }
});

if (!evalUsageFound) {
    console.log('✅ No "eval" keyword usage found in grades.ts');
} else {
    console.log('\n❌ "eval" keyword is still being used as a variable name');
    process.exit(1);
}

// Check for 'evaluation' usage instead
const evaluationPattern = /\bevaluation\s*=>/;
let evaluationCount = 0;

lines.forEach((line) => {
    if (evaluationPattern.test(line)) {
        evaluationCount++;
    }
});

console.log(`✅ Found ${evaluationCount} instances of 'evaluation' arrow function parameter`);
console.log('\n🎉 TypeScript file has been successfully fixed!');