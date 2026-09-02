# -*- coding: utf-8 -*-
"""Targeted unit tests for the documented Sanskrit pitfalls — the reasons these helpers must
NOT be re-implemented ad hoc per repo. Run: pytest tests/test_units.py."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import sanskrit_util as su  # noqa: E402

ACUTE = '́'


def test_to_slp1_digraphs():
    assert su.to_slp1('aiśvarya') == 'ESvarya'      # ai -> E (one phoneme), ś -> S
    assert su.to_slp1('auṣadha') == 'OzaDa'
    assert su.to_slp1('saṃskṛta') == 'saMskfta'


def test_slp1_roundtrip_iast():
    for w in ['śiva', 'kṛṣṇa', 'jñāna', 'rājan', 'saṃskṛta']:
        assert su.from_slp1(su.to_slp1(w)) == w


def test_form_key_preserves_length():
    # length is meaningful here: krānta (PPP) != kranta
    assert su.form_key('krānta') != su.form_key('kranta')


def test_form_key_folds_anusvara_to_homorganic():
    assert su.form_key('krāṃta') == su.form_key('krānta')   # anusvāra == homorganic nasal


def test_form_key_folds_word_final_anusvara_to_m():
    # Sanskrit writes word-final -m as anusvāra before a consonant and as -m in pausa, so
    # these are one word in two spellings and MUST share a key (H3911). Before the fix the
    # anusvāra went to 'n' while the real 'm' was untouched, so they never collided and
    # every anusvāra-final attestation read as un-generated.
    assert su.form_key('rasaṃ') == su.form_key('rasam') == 'rasam'
    assert su.form_key('phalaṁ') == su.form_key('phalam')   # ṁ spelling too
    assert su.form_key('iyaṃ') == su.form_key('iyam')


def test_form_key_final_n_stays_distinct_from_final_m():
    # The fix must not over-fold: final -n and final -m are different endings.
    assert su.form_key('rājan') != su.form_key('rājam')
    assert su.form_key('rājan') == 'rājan'


def test_form_key_medial_anusvara_still_folds_to_n():
    # the final-position rule must not disturb the general homorganic fold
    assert su.form_key('saṃskṛta') == su.form_key('sanskṛta')
    assert su.form_key('saṃskṛtam') == 'sanskṛtam'          # both rules, one word


def test_form_key_drops_visarga_and_vowel_accent():
    assert su.form_key('rāmaḥ') == 'rāma'                   # nom-sg visarga stripped
    assert su.form_key('dev' + 'a' + ACUTE) == 'deva'      # pitch accent on a vowel dropped


def test_form_key_keeps_sibilant_not_accent():
    # ś == s + U+0301 (same codepoint as the acute); must NOT be mistaken for an accent
    assert su.form_key('śas') == 'śas'
    assert 'ś' in su.form_key('śiva')


def test_norm_is_diacritic_insensitive_but_length_blind():
    assert su.norm('Śiva') == su.norm('shiva'.replace('sh', 'ś'))  # case + diacritic folded
    assert su.norm('rājan') == 'rajan'
    assert su.norm('  Agni  ') == 'agni'                   # trims + lowercases


def test_norm_is_devanagari_aware():
    assert su.norm('धर्म') == 'dharma'                      # transliterates first


def test_deva_to_slp1_basic():
    assert su.deva_to_slp1('अग्नि') == 'agni'
    assert su.deva_to_slp1('धर्म') == 'Darma'               # virāma conjunct + inherent 'a'
    assert su.deva_to_slp1('कृष्ण') == 'kfzRa'
    assert su.deva_to_slp1('अऽपि') == 'api'                 # avagraha dropped


def test_deva_to_slp1_retroflex_lla_not_vocalic_l():
    # ळ (U+0933, retroflex ḻa) -> 'L', NOT 'x'. The IAST round-trip to_slp1(deva_to_iast(·))
    # gets this WRONG (ळ and vocalic ḷ both render as IAST ḷ/U+1E37 -> 'x'); deva_to_slp1 must not.
    assert su.deva_to_slp1('ळ') == 'La'
    assert su.deva_to_slp1('अग्निमीळे') == 'agnimILe'        # RV 1.1.1 incipit
    assert su.to_slp1(su.deva_to_iast('ळ')) == 'xa'         # documents the collision deva_to_slp1 fixes
    # vocalic ḷ (ऌ vowel / ◌ॢ mātrā) stays 'x' — the two must remain distinct
    assert su.deva_to_slp1('ऌ') == 'x'
    assert su.deva_to_slp1('कॢप्त') == 'kxpta'
    assert su.deva_to_slp1('ळ') != su.deva_to_slp1('ऌ')


def test_deva_to_slp1_is_from_slp1_roundtrip_partner():
    # from_slp1 ∘ deva_to_slp1 yields proper IAST: ळ -> ḻ (U+1E3B, line-below), the distinct glyph
    # SLP1 reserves for retroflex ḻa, while ऌ -> ḷ (U+1E37, dot-below) for vocalic ḷ.
    assert su.from_slp1(su.deva_to_slp1('ळ')) == 'ḻa'      # U+1E3B + a
    assert su.from_slp1(su.deva_to_slp1('ऌ')) == 'ḷ'       # U+1E37


def test_nfold_folds_nasals_only_as_fallback():
    assert su.nfold('saṃ') == su.nfold('san')              # anusvāra reaches homorganic
    assert su.norm('am') != su.norm('an')                  # exact key keeps am/an distinct


def test_normalize_sanskrit_is_lossy_ascii():
    assert su.normalize_sanskrit('Śiva') == 'siva'
    assert su.normalize_sanskrit('kṛṣṇa') == 'krsna'       # length+retroflex collapsed to ASCII


def test_empty_and_none_safe():
    for f in (su.to_slp1, su.from_slp1, su.deva_to_iast, su.deva_to_slp1, su.iast_to_devanagari,
              su.norm, su.nfold, su.form_key, su.normalize_sanskrit,
              su.slp1_to_devanagari, su.slp1_simplify):
        assert f('') == ''
        assert f(None) == ''
    assert su.to_roman([]) == []
    assert su.to_roman([11]) == []                         # out-of-range dropped


# ---- SLP1-side API ----
def test_slp1_alphabet_constants():
    assert su.SLP1_VOWELS == 'aAiIuUfFxXeEoO'
    assert su.SLP1_MARKS == 'MH~'
    assert su.SLP1_CONSONANTS == 'kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL'
    assert su.SLP1_ALPHABET == su.SLP1_VOWELS + su.SLP1_MARKS + su.SLP1_CONSONANTS


def test_strip_slp1_accents():
    assert su.strip_slp1_accents('a/MSa\\') == 'aMSa'       # udātta + anudātta
    assert su.strip_slp1_accents('Si^va~') == 'Siva'        # svarita + candrabindu


def test_slp1_norm_headword_key():
    assert su.slp1_norm('agni2') == 'agni'                  # trailing homonym index
    assert su.slp1_norm('a/MSa') == 'aMSa'                  # accent stripped
    assert su.slp1_norm('Siva') == 'Siva'                   # case PRESERVED (S = ś, phonemic)
    assert su.slp1_norm('  deva  ') == 'deva'
    assert su.slp1_norm('') == '' and su.slp1_norm(None) == ''


def test_slp1_form_key_folds_like_form_key():
    assert su.slp1_form_key('aMSaH') == su.slp1_form_key('anSa')   # anusvāra==homorganic n, visarga dropped
    assert su.slp1_form_key('rAmaH') == 'rāma'
    assert su.slp1_form_key('kfzRa') == su.form_key(su.from_slp1('kfzRa'))


def test_manuscript_m_to_M():
    # ṁ (U+1E41, m-with-dot-above) -> M — the named SamudraManthanam sanscript-drop blocker.
    assert su.to_slp1('sa' + 'ṁ') == 'saM'
    assert su.to_slp1('saṁskṛta') == 'saMskfta'                    # == the ṃ (U+1E43) spelling
    assert su.to_slp1('saṁskṛta') == su.to_slp1('saṃskṛta')
    assert su.form_key('saṁskṛta') == su.form_key('saṃskṛta')      # NFD path folds both to n too


def test_iast_to_devanagari_fixed_h1394():
    # Regresses the H1394 fix: iast_to_devanagari re-implemented as the to_slp1 ->
    # slp1_to_devanagari composition. The previous naive longest-key-first character
    # substitution never applied virāma/mātrā and was wrong on all 9 of these words
    # (e.g. 'ka' -> 'कअ' instead of 'क').
    cases = {
        'ka': 'क',
        'kṣa': 'क्ष',
        'rāma': 'राम',
        'agni': 'अग्नि',
        'tvam': 'त्वम्',
        'śrī': 'श्री',
        'buddha': 'बुद्ध',
        'dharma': 'धर्म',
        'saṃskṛta': 'संस्कृत',
    }
    for iast, deva in cases.items():
        assert su.iast_to_devanagari(iast) == deva
    # D1 ṁ round-trip check: ṁ (U+1E41) must render the same anusvāra as ṃ (U+1E43)
    assert su.iast_to_devanagari('ṁ') == su.iast_to_devanagari('ṃ') == 'ं'


def test_slp1_to_devanagari_basic():
    assert su.slp1_to_devanagari('Darma') == 'धर्म'                # virāma conjunct + inherent 'a'
    assert su.slp1_to_devanagari('agni') == 'अग्नि'
    assert su.slp1_to_devanagari('kfzRa') == 'कृष्ण'
    assert su.slp1_to_devanagari('rAmaH') == 'रामः'               # visarga
    assert su.slp1_to_devanagari('aMSa') == 'अंश'                 # anusvāra
    assert su.slp1_to_devanagari('La') == 'ळ'                     # Vedic retroflex ḻa
    assert su.slp1_to_devanagari('k') == 'क्'                     # trailing bare consonant -> virāma


def test_slp1_to_devanagari_roundtrips_deva_to_slp1():
    # the pair is lossless for canonical SLP1 (exhaustively checked in tools/gen_vectors.py over
    # the alphabet + 1000 real MW headwords); assert the contract on a spread here.
    for s in ['agni', 'Darma', 'kfzRa', 'saMskftam', 'jYAna', 'budDa', 'aMSaH', 'agnimILe', 'La']:
        assert su.deva_to_slp1(su.slp1_to_devanagari(s)) == s
    # documented NOT round-trip stable (matches deva_to_slp1): candrabindu folds to anusvāra,
    # avagraha is dropped — pin the one-way behaviour so a regression is visible.
    assert su.slp1_to_devanagari('a~') == 'अँ'                    # candrabindu rendered...
    assert su.deva_to_slp1('अँ') == 'aM'                          # ...but folds back to anusvāra
    assert su.slp1_to_devanagari("ta'") == 'तऽ'                   # avagraha rendered...
    assert su.deva_to_slp1('तऽ') == 'ta'                          # ...but deva_to_slp1 drops it


def test_slp1_simplify_folds_all_to_ascii():
    assert su.slp1_simplify('guRa') == 'guna'                     # R=ṇ -> n (NOT 'gūna'!) the trap
    assert su.slp1_simplify('kfzRa') == 'krsna'                   # f->r, z->s, R->n
    assert su.slp1_simplify('EkSvarya') == 'aiksvarya'            # E->ai, S->s
    assert su.slp1_simplify('BAva') == 'bhava'                    # B->bh, A->a
    assert su.slp1_simplify('agniH') == 'agni'                    # visarga dropped
    # lossy extreme: distinctions slp1_norm / slp1_form_key keep are gone here
    assert su.slp1_simplify('Siva') == su.slp1_simplify('siva')


def test_source_line_to_iast_per_dict_markup():
    # Same literals as js/test/units.test.mjs — locks JS == Python.
    assert su.source_line_to_iast('{#aBAga#}¦, <lex>f.</lex> {#A#} <ls>TB. 6,7,5</ls>.<info n="x"/>', 'pw') \
        == 'abhāga, f. ā TB. 6,7,5.'                               # PW/PWG/AP/WIL: {#…#}
    assert su.source_line_to_iast('{#aBAga#}¦ {%ohne Antheil%}. <ls>RV. 1,2,3</ls>', 'pwg') \
        == 'abhāga ohne Antheil. RV. 1,2,3'                        # meaning {%…%} kept as-is
    assert su.source_line_to_iast('<hom>1.</hom> <s>aBAga</s> ¦ <lex>mfn.</lex> without a share', 'mw') \
        == '1. abhāga mfn. without a share'                        # MW: <s>…</s>
    assert su.source_line_to_iast('aBAga¦ pu0 na BAgaH aBAve na0 ta0 . 1 BAgABAve .', 'vcp') \
        == 'abhāga pu0 na bhāgaḥ abhāve na0 ta0. 1 bhāgābhāve.'    # VCP/SKD: whole-line prose
    assert su.source_line_to_iast('abdaH¦, puM, (abati sImAnaM rakzati aba', 'skd') \
        == 'abdaḥ, puṃ, (abati sīmānaṃ rakṣati aba'
    assert su.source_line_to_iast('', 'mw') == ''
    assert su.source_line_to_iast(None, 'mw') == ''
    assert su.source_text_to_iast('{#aBAga#}¦\n{#A#}', 'pw') == 'abhāga\nā'  # multi-line


if __name__ == '__main__':
    import traceback
    funcs = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    ok = 0
    for t in funcs:
        try:
            t(); ok += 1
        except Exception:
            print(f'FAIL {t.__name__}'); traceback.print_exc()
    print(f'{ok}/{len(funcs)} unit tests passed')
