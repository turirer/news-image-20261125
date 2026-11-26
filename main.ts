// Entry point for the news-image-20261125 bounty (Node, standard library only).
//
// The picture for this entry is the entry.png committed beside this file.
// At grading time the harness expects the program to leave that picture at
// $MAKEFUN_OUTPUT_DIR/entry.png (falling back to /output when the variable
// is unset). Before copying, the file is sanity-checked: it must exist and
// start with the eight-byte PNG signature, otherwise we fail loudly instead
// of handing the judge a broken file. The copied size is printed so the run
// log shows exactly what was delivered.

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

const source = new URL('./entry.png', import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

const head = readFileSync(source).subarray(0, PNG_SIGNATURE.length);
if (!head.equals(PNG_SIGNATURE)) {
  throw new Error('entry.png does not start with the PNG signature');
}

copyFileSync(source, target);

const { size } = statSync(target);
console.log(`entry.png copied to ${target} (${size} bytes)`);
