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
              su.norm, su.nfold, su.form_key, su.normalize_sanskrit):
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
