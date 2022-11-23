"""test get_oov_word_count """
from asr_evaluation.out_of_vocabulary import get_oov_results

from asr_evaluation.metrics.compute_metrics import get_stats
from asr_evaluation.metrics.compute_metrics import MetricType


def test_get_oov_word_count_3del():
    """Test get_oov_results"""
    dictionary = {
        "this",
        "is",
        "delete",
        "a",
    }

    ref = "this is a oovtest delete oovtest1"
    hyp = "this is a [...] delete [...]"
    stats = get_stats(ref, hyp, "en", MetricType.WER_NORMALIZED)
    actual = get_oov_results(stats, dictionary)

    expected = {
        "all_oov_words": "one,oovtest,oovtest",
        "words": "one,oovtest,oovtest",
        "subs_in_gt": 0,
        "subs_in_hyp": 0,
        "subs_in_both": 0,
        "ins": 0,
        "del": 3,
    }

    assert actual == expected


def test_get_oov_word_count_4test():
    """Test get_oov_results"""
    dictionary = {
        "this",
        "is",
        "delete",
        "a",
    }

    ref = "this is a oovtest delete s3 and q4"
    hyp = "this is a [...] delete [...]"
    stats = get_stats(ref, hyp, "en", MetricType.WER_NORMALIZED)
    actual = get_oov_results(stats, dictionary)

    expected = {
        "all_oov_words": "one,oovtest,oovtest",
        "words": "one,oovtest,oovtest",
        "subs_in_gt": 0,
        "subs_in_hyp": 0,
        "subs_in_both": 0,
        "ins": 0,
        "del": 3,
    }

    assert actual == expected


def test_get_oov_word_count_2oov():
    """Test get_oov_results"""
    dictionary = {
        "this",
        "is",
        "delete",
        "a",
    }

    ref = "this is a oovtest delete gabamudi"
    hyp = "this is a [...] delete gabamudi"
    stats = get_stats(ref, hyp, "en", MetricType.WER_NORMALIZED)
    actual = get_oov_results(stats, dictionary)

    expected = {
        "all_oov_words": "oovtest",
        "words": "gabamudi,oovtest",
        "subs_in_gt": 0,
        "subs_in_hyp": 0,
        "subs_in_both": 0,
        "ins": 0,
        "del": 1,
    }

    assert actual == expected


def test_get_oov_word_count_3oov():
    """Test get_oov_results"""
    dictionary = {
        "this",
        "is",
        "delete",
        "a",
        "and",
    }

    ref = "this is a oovtest and delete gabamudi"
    hyp = "this is a suboov and insertoov delete gabamudi"
    stats = get_stats(ref, hyp, "en", MetricType.WER_NORMALIZED)
    actual = get_oov_results(stats, dictionary)

    expected = {
        "all_oov_words": "insertoov,oovtest,suboov",
        "words": "gabamudi,oovtest",
        "subs_in_gt": 1,
        "subs_in_hyp": 1,
        "subs_in_both": 1,
        "ins": 1,
        "del": 0,
    }

    assert actual == expected
