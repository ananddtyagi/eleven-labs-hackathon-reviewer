const fs = require('fs');
const path = require('path');

const directoryPath = path.join(__dirname, 'eleven-labs-ai-review/src/content/complete_project_review_data');
const outputPath = path.join(__dirname, 'eleven-labs-ai-review/src/contentc/index.js');

fs.readdir(directoryPath, (err, files) => {
  if (err) {
    return console.log('Unable to scan directory: ' + err);
  }

  const imports = files
    .filter(file => file.endsWith('.json'))
    .map(file => {
      const variableName = path.basename(file, '.json').replace(/-/g, '_');
      return `import ${variableName} from './complete_project_review_data/${file}';`;
    });

  const exportStatement = `export default [${files
    .filter(file => file.endsWith('.json'))
    .map(file => path.basename(file, '.json').replace(/-/g, '_'))
    .join(', ')}];`;

  const content = `${imports.join('\n')}\n\n${exportStatement}\n`;

  fs.writeFileSync(outputPath, content, 'utf8');
  console.log('Index file generated successfully.');
});