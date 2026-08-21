import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.alignment import (
    align_sequences,
    calculate_gc_content,
    validate_sequence,
    calculate_e_value,
    calculate_bit_score,
    _empty_alignment_result
)


class TestAlignSequences:
    def test_identical_sequences(self):
        result = align_sequences("ATCGATCG", "ATCGATCG")
        assert result['identity'] == 100.0
        assert result['gaps'] == 0
        assert result['matches'] == 8
        assert result['mismatches'] == 0
        assert result['score'] > 0
        assert result['error'] is None

    def test_single_mismatch(self):
        result = align_sequences("ATCGATCG", "ATCGTTCG")
        assert result['identity'] == pytest.approx(87.5, abs=0.1)
        assert result['gaps'] == 0
        assert result['matches'] == 7
        assert result['mismatches'] == 1
        assert result['error'] is None

    def test_insertion_in_query(self):
        result = align_sequences("ATCGATCG", "ATCGAATCG")
        assert result['identity'] == 100.0
        assert result['gaps'] == 1
        assert result['matches'] == 8
        assert result['error'] is None

    def test_deletion_in_query(self):
        result = align_sequences("ATCGATCG", "ATCATCG")
        assert result['identity'] == 100.0
        assert result['gaps'] == 1
        assert result['matches'] == 7
        assert result['error'] is None

    def test_multiple_mutations(self):
        result = align_sequences("ATCGATCGATCG", "ATCATCGTTCG")
        assert result['identity'] > 80.0
        assert result['gaps'] >= 1
        assert result['error'] is None

    def test_invalid_reference(self):
        result = align_sequences("INVALID", "ATCG")
        assert result['error'] is not None
        assert result['score'] == 0

    def test_invalid_query(self):
        result = align_sequences("ATCG", "INVALID")
        assert result['error'] is not None
        assert result['score'] == 0

    def test_empty_reference(self):
        result = align_sequences("", "ATCG")
        assert result['error'] is not None

    def test_empty_query(self):
        result = align_sequences("ATCG", "")
        assert result['error'] is not None

    def test_long_sequences(self):
        ref = "ATCG" * 1000
        query = "ATCG" * 1000
        result = align_sequences(ref, query)
        assert result['identity'] == 100.0
        assert result['error'] is None

    def test_scoring_scheme_in_output(self):
        result = align_sequences("ATCG", "ATCG")
        assert 'BLASTN' in result['scoring_scheme']

    def test_e_value_calculation(self):
        result = align_sequences("ATCGATCG", "ATCGATCG")
        assert result['e_value'] >= 0
        assert result['e_value'] < 1e10

    def test_bit_score_calculation(self):
        result = align_sequences("ATCGATCG", "ATCGATCG")
        assert result['bit_score'] > 0

    def test_coverage_calculation(self):
        result = align_sequences("ATCGATCG", "ATCGATCG")
        assert result['coverage'] == 100.0

    def test_alignment_lengths(self):
        result = align_sequences("ATCGATCG", "ATCGATCG")
        assert result['query_length'] == 8
        assert result['reference_length'] == 8
        assert result['alignment_length'] > 0


class TestCalculateGCContent:
    def test_all_at(self):
        assert calculate_gc_content("ATATAT") == 0

    def test_all_gc(self):
        assert calculate_gc_content("GCGCGC") == 100

    def test_mixed(self):
        assert calculate_gc_content("ATCG") == 50

    def test_with_n(self):
        assert calculate_gc_content("ATCGNN") == 50

    def test_empty(self):
        assert calculate_gc_content("") == 0

    def test_lowercase(self):
        assert calculate_gc_content("atcg") == 50


class TestValidateSequence:
    def test_valid_dna(self):
        valid, _ = validate_sequence("ATCGATCG")
        assert valid

    def test_valid_with_ambiguous(self):
        valid, _ = validate_sequence("ATCGNRYSWKMBDHV")
        assert valid

    def test_invalid_char(self):
        valid, error = validate_sequence("ATCGXYZ")
        assert not valid
        assert "X" in error and "Z" in error

    def test_empty(self):
        valid, _ = validate_sequence("")
        assert valid

    def test_lowercase(self):
        valid, _ = validate_sequence("atcg")
        assert valid


class TestCalculateEValue:
    def test_high_score(self):
        e_val = calculate_e_value(100, 100)
        assert e_val >= 0

    def test_low_score(self):
        e_val = calculate_e_value(10, 100)
        assert e_val > 0

    def test_zero_score(self):
        e_val = calculate_e_value(0, 100)
        assert e_val == float('inf')

    def test_negative_score(self):
        e_val = calculate_e_value(-5, 100)
        assert e_val == float('inf')


class TestCalculateBitScore:
    def test_positive_score(self):
        bit_score = calculate_bit_score(50)
        assert bit_score > 0

    def test_zero_score(self):
        bit_score = calculate_bit_score(0)
        assert bit_score == 0


class TestEmptyAlignmentResult:
    def test_empty_result(self):
        result = _empty_alignment_result("test error")
        assert result['score'] == 0
        assert result['identity'] == 0.0
        assert result['error'] == "test error"

    def test_empty_result_no_error(self):
        result = _empty_alignment_result()
        assert result['error'] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
