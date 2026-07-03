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

// deva_to_slp1: ळ (U+0933, retroflex ḻa) -> 'L', NOT 'x'. to_slp1(deva_to_iast(·)) gets this wrong
// (ळ and vocalic ḷ both render as IAST ḷ/U+1E37 -> 'x'); the direct transcode must keep them apart.
assert.equal(su.deva_to_slp1('अग्नि'), 'agni');
assert.equal(su.deva_to_slp1('धर्म'), 'Darma');
assert.equal(su.deva_to_slp1('अऽपि'), 'api');               // avagraha dropped
assert.equal(su.deva_to_slp1('ळ'), 'La');
assert.equal(su.deva_to_slp1('अग्निमीळे'), 'agnimILe');      // RV 1.1.1 incipit
assert.equal(su.to_slp1(su.deva_to_iast('ळ')), 'xa');       // the collision deva_to_slp1 fixes
assert.equal(su.deva_to_slp1('ऌ'), 'x');                    // vocalic ḷ stays 'x'
assert.equal(su.deva_to_slp1('कॢप्त'), 'kxpta');
assert.notEqual(su.deva_to_slp1('ळ'), su.deva_to_slp1('ऌ'));
assert.equal(su.from_slp1(su.deva_to_slp1('ळ')), 'ḻa');     // round-trip partner: U+1E3B
assert.equal(su.deva_to_slp1(''), '');
assert.equal(su.deva_to_slp1(null), '');

// ṁ (U+1E41, m-with-dot-above) -> M — the named SamudraManthanam sanscript-drop blocker
assert.equal(su.to_slp1('sa' + 'ṁ'), 'saM');
assert.equal(su.to_slp1('saṁskṛta'), 'saMskfta');
assert.equal(su.to_slp1('saṁskṛta'), su.to_slp1('saṃskṛta'));
assert.equal(su.form_key('saṁskṛta'), su.form_key('saṃskṛta'));

// slp1_to_devanagari: real transcode (virāma conjuncts + mātrās), round-trip partner of deva_to_slp1
assert.equal(su.slp1_to_devanagari('Darma'), 'धर्म');
assert.equal(su.slp1_to_devanagari('agni'), 'अग्नि');
assert.equal(su.slp1_to_devanagari('kfzRa'), 'कृष्ण');
assert.equal(su.slp1_to_devanagari('rAmaH'), 'रामः');
assert.equal(su.slp1_to_devanagari('aMSa'), 'अंश');
assert.equal(su.slp1_to_devanagari('La'), 'ळ');
assert.equal(su.slp1_to_devanagari('k'), 'क्');                 // trailing bare consonant -> virāma
for (const s of ['agni', 'Darma', 'kfzRa', 'saMskftam', 'jYAna', 'budDa', 'aMSaH', 'agnimILe', 'La']) {
  assert.equal(su.deva_to_slp1(su.slp1_to_devanagari(s)), s);   // lossless for canonical SLP1
}
// documented NOT round-trip stable (matches deva_to_slp1): candrabindu -> anusvāra, avagraha dropped
assert.equal(su.slp1_to_devanagari('a~'), 'अँ');
assert.equal(su.deva_to_slp1('अँ'), 'aM');
assert.equal(su.slp1_to_devanagari("ta'"), 'तऽ');
assert.equal(su.deva_to_slp1('तऽ'), 'ta');
assert.equal(su.slp1_to_devanagari(''), '');
assert.equal(su.slp1_to_devanagari(null), '');

// slp1_simplify: fuzzy-match key, folds ALL SLP1 distinctions to plain ASCII
assert.equal(su.slp1_simplify('guRa'), 'guna');                 // R=ṇ -> n (NOT 'gūna'!) the trap
assert.equal(su.slp1_simplify('kfzRa'), 'krsna');
assert.equal(su.slp1_simplify('EkSvarya'), 'aiksvarya');
assert.equal(su.slp1_simplify('BAva'), 'bhava');
assert.equal(su.slp1_simplify('agniH'), 'agni');
assert.equal(su.slp1_simplify('Siva'), su.slp1_simplify('siva'));
assert.equal(su.slp1_simplify(''), '');
assert.equal(su.slp1_simplify(null), '');

console.log('OK: sanskrit-util SLP1 unit tests passed (JS == Python literals)');
