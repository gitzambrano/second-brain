from check_gaps import is_gap_candidate


def test_single_generic_capitalized_word_is_not_a_gap_candidate():
    assert not is_gap_candidate("Engenheiro", {"nome-proprio"})
    assert not is_gap_candidate("Físico", {"nome-proprio"})
    assert not is_gap_candidate("Substituindo", {"nome-proprio"})
    assert not is_gap_candidate("Esses", {"nome-proprio"})


def test_explicit_or_multiword_signals_remain_gap_candidates():
    assert is_gap_candidate("Demonio de Laplace", {"nome-proprio"})
    assert is_gap_candidate("Laplace", {"negrito"})
    assert is_gap_candidate("Teoria Especial", {"link-externo"})
