const fs = require('fs');
const path = require('path');

// Read the coverage-final.json file
const coveragePath = path.join(__dirname, '..', 'coverage', 'coverage-final.json');
const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf-8'));

// Component categories
const categories = {
  pages: {},
  components: {},
  utils: {},
  store: {},
  api: {}
};

// Compile stats for each file
Object.entries(coverage).forEach(([filePath, data]) => {
  // Skip non-source files
  if (!filePath.includes('src/')) return;
  
  // Determine category
  let category = 'other';
  if (filePath.includes('/pages/')) category = 'pages';
  else if (filePath.includes('/components/')) category = 'components';
  else if (filePath.includes('/utils/')) category = 'utils';
  else if (filePath.includes('/store/')) category = 'store';
  else if (filePath.includes('/api/')) category = 'api';

  // Get file name
  const fileName = path.basename(filePath);

  // Calculate coverage percentages
  const stats = {
    statements: {
      covered: data.s ? Object.values(data.s).filter(v => v > 0).length : 0,
      total: data.s ? Object.keys(data.s).length : 0
    },
    branches: {
      covered: data.b ? Object.values(data.b).flat().filter(v => v > 0).length : 0,
      total: data.b ? Object.values(data.b).flat().length : 0
    },
    functions: {
      covered: data.f ? Object.values(data.f).filter(v => v > 0).length : 0,
      total: data.f ? Object.keys(data.f).length : 0
    },
    lines: {
      covered: data.l ? Object.values(data.l).filter(v => v > 0).length : 0,
      total: data.l ? Object.keys(data.l).length : 0
    }
  };

  categories[category][fileName] = stats;
});

// Calculate percentages and format output
let output = '# Frontend Test Coverage Report\n\n';

Object.entries(categories).forEach(([category, files]) => {
  if (Object.keys(files).length === 0) return;

  output += `## ${category.charAt(0).toUpperCase() + category.slice(1)}\n\n`;
  output += '| File | Statements | Branches | Functions | Lines |\n';
  output += '|------|------------|-----------|------------|-------|\n';

  Object.entries(files).forEach(([file, stats]) => {
    const formatPercentage = (covered, total) => {
      if (total === 0) return 'N/A';
      return `${((covered / total) * 100).toFixed(2)}% (${covered}/${total})`;
    };

    output += `| ${file} | `;
    output += `${formatPercentage(stats.statements.covered, stats.statements.total)} | `;
    output += `${formatPercentage(stats.branches.covered, stats.branches.total)} | `;
    output += `${formatPercentage(stats.functions.covered, stats.functions.total)} | `;
    output += `${formatPercentage(stats.lines.covered, stats.lines.total)} |\n`;
  });

  output += '\n';
});

// Write the report
fs.writeFileSync(path.join(__dirname, '..', 'coverage-report.md'), output);
console.log('Coverage report generated: coverage-report.md');