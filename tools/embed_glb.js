#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const projectRoot = path.resolve(__dirname, '..');
const glbPath = path.join(projectRoot, 'rainy_konbini.glb');
const outPath = path.join(projectRoot, 'viewer', 'scene_data.js');

if (!fs.existsSync(glbPath)) {
  console.error('Missing model: ' + glbPath);
  process.exit(1);
}

const glb = fs.readFileSync(glbPath);
const base64 = glb.toString('base64');
fs.writeFileSync(outPath, 'window.__GLB_B64="' + base64 + '";\n', 'utf8');

const mb = (glb.length / 1024 / 1024).toFixed(1);
console.log('Wrote ' + outPath);
console.log('GLB: ' + mb + ' MB, embedded Base64: ' + (base64.length / 1024 / 1024).toFixed(1) + ' MB');
