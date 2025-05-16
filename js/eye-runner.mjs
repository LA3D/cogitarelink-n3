import { readFileSync } from 'node:fs';
import { stdin } from 'node:process';
import { n3reasoner } from 'eyereasoner';

/** Expect JSON on stdin: { dataPath, rulesPath, queryPath|null } */
const input = JSON.parse(await new Promise(resolve => {
  let buf = '';
  stdin.setEncoding('utf8');
  stdin.on('data', d => buf += d);
  stdin.on('end', () => resolve(buf));
}));

const data = readFileSync(input.dataPath, 'utf8');
const rules = readFileSync(input.rulesPath, 'utf8');
const query = input.queryPath ? readFileSync(input.queryPath, 'utf8') : undefined;

const result = await n3reasoner(`${data}\n${rules}`, query);
process.stdout.write(result);