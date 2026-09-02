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

// H3911: word-final anusvāra is underlyingly /m/ — Sanskrit writes final -m as anusvāra
// before a consonant and as -m in pausa, so these are one word in two spellings and must
// share a key. Before the fix the anusvāra went to 'n' while the real 'm' was untouched, so
// they never collided and every anusvāra-final attestation read as un-generated.
assert.equal(su.form_key('rasaṃ'), su.form_key('rasam'));
assert.equal(su.form_key('rasaṃ'), 'rasam');
assert.equal(su.form_key('phalaṁ'), su.form_key('phalam'));
assert.equal(su.form_key('iyaṃ'), su.form_key('iyam'));
// but the fix must not over-fold: final -n and final -m are different endings
assert.notEqual(su.form_key('rājan'), su.form_key('rājam'));
assert.equal(su.form_key('rājan'), 'rājan');
// and the general homorganic fold is undisturbed
assert.equal(su.form_key('saṃskṛta'), su.form_key('sanskṛta'));
assert.equal(su.form_key('saṃskṛtam'), 'sanskṛtam');

// H1394: iast_to_devanagari re-implemented as the to_slp1 -> slp1_to_devanagari composition.
// The previous naive longest-key-first character substitution never applied virāma/mātrā and
// was wrong on all 9 of these words (e.g. 'ka' -> 'कअ' instead of 'क').
assert.equal(su.iast_to_devanagari('ka'), 'क');
assert.equal(su.iast_to_devanagari('kṣa'), 'क्ष');
assert.equal(su.iast_to_devanagari('rāma'), 'राम');
assert.equal(su.iast_to_devanagari('agni'), 'अग्नि');
assert.equal(su.iast_to_devanagari('tvam'), 'त्वम्');
assert.equal(su.iast_to_devanagari('śrī'), 'श्री');
assert.equal(su.iast_to_devanagari('buddha'), 'बुद्ध');
assert.equal(su.iast_to_devanagari('dharma'), 'धर्म');
assert.equal(su.iast_to_devanagari('saṃskṛta'), 'संस्कृत');
// D1 ṁ round-trip check: ṁ (U+1E41) must render the same anusvāra as ṃ (U+1E43)
assert.equal(su.iast_to_devanagari('ṁ'), su.iast_to_devanagari('ṃ'));
assert.equal(su.iast_to_devanagari('ṁ'), 'ं');

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

// source_line_to_iast: CDSL raw source line -> readable IAST, per-dict markup
assert.equal(su.source_line_to_iast('{#aBAga#}¦, <lex>f.</lex> {#A#} <ls>TB. 6,7,5</ls>.<info n="x"/>', 'pw'),
  'abhāga, f. ā TB. 6,7,5.');                                    // PW/PWG/AP/WIL: {#…#}
assert.equal(su.source_line_to_iast('{#aBAga#}¦ {%ohne Antheil%}. <ls>RV. 1,2,3</ls>', 'pwg'),
  'abhāga ohne Antheil. RV. 1,2,3');                             // meaning {%…%} kept as-is
assert.equal(su.source_line_to_iast('<hom>1.</hom> <s>aBAga</s> ¦ <lex>mfn.</lex> without a share', 'mw'),
  '1. abhāga mfn. without a share');                             // MW: <s>…</s>
assert.equal(su.source_line_to_iast('aBAga¦ pu0 na BAgaH aBAve na0 ta0 . 1 BAgABAve .', 'vcp'),
  'abhāga pu0 na bhāgaḥ abhāve na0 ta0. 1 bhāgābhāve.');         // VCP/SKD: whole-line prose
assert.equal(su.source_line_to_iast('abdaH¦, puM, (abati sImAnaM rakzati aba', 'skd'),
  'abdaḥ, puṃ, (abati sīmānaṃ rakṣati aba');
assert.equal(su.source_line_to_iast('', 'mw'), '');
assert.equal(su.source_line_to_iast(null, 'mw'), '');
assert.equal(su.source_text_to_iast('{#aBAga#}¦\n{#A#}', 'pw'), 'abhāga\nā');  // multi-line preserves breaks

console.log('OK: sanskrit-util SLP1 unit tests passed (JS == Python literals)');
