// Unit tests for the SLP1-side API. The constants are NOT exercised by the vector harness
// (it only calls functions), so assert them here against the SAME literals as the Python
// suite (py/tests/test_units.py) — that locks JS == Python for the constants too.
import assert from 'node:assert/strict';
import * as su from '../index.mjs';

// SLP1 character-class constants (must match Python exactly)
assert.equal(su.SLP1_VOWELS, 'aAiIuUfFxXeEoO');
assert.equal(su.SLP1_MARKS, 'MH~');
assert.equal(su.SLP1_CONSONANTS, 'kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL');
assert.equal(su.SLP1_ALPHABET, su.SLP1_VOWELS + su.SLP1_MARKS + su.SLP1_CONSONANTS);

// strip_slp1_accents: / \ ^ ~
assert.equal(su.strip_slp1_accents('a/MSa\\'), 'aMSa');
assert.equal(su.strip_slp1_accents('Si^va~'), 'Siva');

// slp1_norm: CDSL headword key — accents + trailing homonym digits stripped, case PRESERVED
assert.equal(su.slp1_norm('agni2'), 'agni');
assert.equal(su.slp1_norm('a/MSa'), 'aMSa');
assert.equal(su.slp1_norm('Siva'), 'Siva');         // S = ś kept (phonemic)
assert.equal(su.slp1_norm('  deva  '), 'deva');
assert.equal(su.slp1_norm(''), '');
assert.equal(su.slp1_norm(null), '');

// slp1_form_key: length-preserving compare key (folds nasals/visarga via form_key)
assert.equal(su.slp1_form_key('aMSaH'), su.slp1_form_key('anSa'));
assert.equal(su.slp1_form_key('rAmaH'), 'rāma');
assert.equal(su.slp1_form_key('kfzRa'), su.form_key(su.from_slp1('kfzRa')));

console.log('OK: sanskrit-util SLP1 unit tests passed (JS == Python literals)');
