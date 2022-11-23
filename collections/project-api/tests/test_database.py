from asr_evaluation.metrics.compute_metrics import MetricType, get_stats
from asr_evaluation.configs import EngineResults
from pytest import approx
import random
import uuid


def percent_or_none(value, num_tokens):
    """Return a percentage value or None if num_tokens is zero."""
    if num_tokens == 0:
        return None
    else:
        return 100 * value / num_tokens


def test_experiment_results(mock_experiment, db_query):
    """Test the queries to experiment_results by creating random data, inserting them into the
    test database and checking that the output of the queries to experiment_results match the
    expectations.
    """
    random.seed(41)

    num_shards = 50
    exp = mock_experiment()

    assert exp.experiment_id is not None

    for _ in range(num_shards):
        shard_id = str(uuid.uuid4())
        hypothesis = str(uuid.uuid4())
        best_ground_truth_id = str(uuid.uuid4())
        metric_type = random.choice(list(MetricType))
        engine_results = EngineResults()

        metric_stats = {
            "num_tokens_hypothesis": random.randint(0, 50),
            "num_tokens_reference": random.randint(0, 50),
            "corr": random.randint(0, 50),
            "err": random.randint(0, 50),
            "del": random.randint(0, 50),
            "ins": random.randint(0, 50),
            "sub": random.randint(0, 50),
        }

        oov_results = {
            "del": random.randint(0, 50),
            "ins": random.randint(0, 50),
            "subs_in_gt": random.randint(0, 50),
            "subs_in_both": random.randint(0, 50),
            "subs_in_hyp": random.randint(0, 50),
            "words": str(uuid.uuid4()),
        }
        hint_results = {
            "hint_number": random.randint(0, 50),
            "hint_in_ref": random.randint(0, 50),
            "hint_missed": random.randint(0, 50),
        }

        exp.db_save_metric_results(
            shard_id=shard_id,
            experiment_id=exp.experiment_id,
            hypothesis=hypothesis,
            metric_type=metric_type,
            best_ground_truth_id=best_ground_truth_id,
            metric_stats=metric_stats,
            engine_results=engine_results,
        )

        exp.save_oov_speech_hints(
            shard_id=shard_id,
            experiment_id=exp.experiment_id,
            hypothesis=hypothesis,
            metric_type=metric_type,
            best_ground_truth_id=best_ground_truth_id,
            oov_results=oov_results,
            hint_results=hint_results,
            engine_results=engine_results,
        )

        check_experiment_results = (
            "SELECT * FROM experiment_results "
            "WHERE experiment_id = %s AND audio_shard_id = %s;"
        )

        results = db_query(
            sql=check_experiment_results,
            args=[exp.experiment_id, shard_id],
        )

        if metric_type == MetricType.WER_NORMALIZED:
            assert len(results) == 1
        else:
            assert len(results) == 0
            continue

        res = results[0]

        assert res["corr_abs"] == metric_stats["corr"]
        assert res["err_abs"] == metric_stats["err"]
        assert res["ins_abs"] == metric_stats["ins"]
        assert res["del_abs"] == metric_stats["del"]
        assert res["sub_abs"] == metric_stats["sub"]
        assert res["corr_per"] == approx(
            percent_or_none(res["corr_abs"], metric_stats["num_tokens_reference"])
        )
        assert res["err_per"] == approx(
            percent_or_none(res["err_abs"], metric_stats["num_tokens_reference"])
        )
        assert res["ins_per"] == approx(
            percent_or_none(res["ins_abs"], metric_stats["num_tokens_reference"])
        )
        assert res["del_per"] == approx(
            percent_or_none(res["del_abs"], metric_stats["num_tokens_reference"])
        )
        assert res["sub_per"] == approx(
            percent_or_none(res["sub_abs"], metric_stats["num_tokens_reference"])
        )

        if metric_type.need_oov_speech_hints():
            assert res["oov_del_abs"] == oov_results["del"]
            assert res["oov_ins_abs"] == oov_results["ins"]
            assert res["oov_sub_abs"] == oov_results["subs_in_gt"]
            assert res["oov_sub_gt_hyp_abs"] == oov_results["subs_in_both"]
            assert res["oov_sub_hyp_abs"] == oov_results["subs_in_hyp"]
            assert res["oov_words"] == oov_results["words"]

            assert res["hints"] == hint_results["hint_number"]
            assert res["hint_in_ref"] == hint_results["hint_in_ref"]
            assert res["hint_missed"] == hint_results["hint_missed"]
        else:
            assert res["oov_del_abs"] is None
            assert res["oov_ins_abs"] is None
            assert res["oov_sub_abs"] is None
            assert res["oov_sub_gt_hyp_abs"] is None
            assert res["oov_sub_hyp_abs"] is None


def test_ground_truth_relative_wer(mock_experiment, db_query):
    """Test 'compute_relative_wer' by randomly generating a number of test-cases
    and checking that the output of a query to 'ground_truth_relative_wer' match
    the expected values.
    """
    random.seed(41)

    num_shards = 50
    exp = mock_experiment()

    assert exp.experiment_id is not None

    alphabet = "abcdefghijklmnopqrstuvwxyz"

    def random_sentence():
        return " ".join(
            [
                "".join([random.choice(alphabet) for i in range(random.randint(1, 8))])
                for j in range(random.randint(1, 20))
            ]
        )

    for _ in range(num_shards):
        audio_id = str(uuid.uuid4())
        ground_truth_id_1, ground_truth_id_2 = sorted(
            [str(uuid.uuid4()), str(uuid.uuid4())]
        )

        ground_truth_1 = random_sentence()
        ground_truth_2 = random_sentence()
        metric_type = random.choice(
            [MetricType.WER_NORMALIZED, MetricType.WER_CP_NORMALIZED]
        )

        ground_truths = {
            ground_truth_id_1: ground_truth_1,
            ground_truth_id_2: ground_truth_2,
        }

        exp.compute_relative_wer(
            audio_id=audio_id,
            ground_truths=ground_truths,
            metric=metric_type,
        )

        fetch_results = (
            "SELECT * FROM ground_truth_relative_wer "
            "WHERE gt_id1 = %s AND gt_id2 = %s;"
        )

        results = db_query(
            sql=fetch_results,
            args=[ground_truth_id_1, ground_truth_id_2],
        )

        if metric_type == MetricType.WER_NORMALIZED:
            assert len(results) == 1
        else:
            assert len(results) == 0
            continue

        res = results[0]

        expected_wer = get_stats(
            ref_transcript=ground_truth_1,
            hyp_transcript=ground_truth_2,
            language_code=exp.language_code,
            metric_type=metric_type,
        )

        assert res["corr_abs"] == expected_wer["corr"]
        assert res["err_abs"] == expected_wer["err"]
        assert res["del_abs"] == expected_wer["del"]
        assert res["sub_abs"] == expected_wer["sub"]
        assert res["ins_abs"] == expected_wer["ins"]

        assert res["corr_per"] == approx(
            percent_or_none(expected_wer["corr"], expected_wer["num_tokens_reference"])
        )
        assert res["err_per"] == approx(
            percent_or_none(expected_wer["err"], expected_wer["num_tokens_reference"])
        )
        assert res["ins_per"] == approx(
            percent_or_none(expected_wer["ins"], expected_wer["num_tokens_reference"])
        )
        assert res["del_per"] == approx(
            percent_or_none(expected_wer["del"], expected_wer["num_tokens_reference"])
        )
        assert res["sub_per"] == approx(
            percent_or_none(expected_wer["sub"], expected_wer["num_tokens_reference"])
        )
