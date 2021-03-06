"""The block testing module ..."""
import copy

import pytest

from casper.blockchain.block import Block
from casper.blockchain.blockchain_protocol import BlockchainProtocol
from casper.justification import Justification
from casper.validator import Validator

from simulations.testing_language import TestLangCBC


def test_equality_of_copies_off_genesis(validator):
    block = Block(None, Justification(), validator)

    shallow_copy = copy.copy(block)
    deep_copy = copy.deepcopy(block)

    assert block == shallow_copy
    assert block == deep_copy
    assert shallow_copy == deep_copy


def test_equality_of_copies_of_non_genesis(report):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
    test_lang = TestLangCBC({0: 10, 1: 11}, BlockchainProtocol, report)
    test_lang.parse(test_string)

    for block in test_lang.blocks:
        shallow_copy = copy.copy(block)
        deep_copy = copy.deepcopy(block)

        assert block == shallow_copy
        assert block == deep_copy
        assert shallow_copy == deep_copy


def test_non_equality_of_copies_off_genesis():
    validator_0 = Validator("v0", 10)
    validator_1 = Validator("v1", 11)

    block_0 = Block(None, Justification(), validator_0)
    block_1 = Block(None, Justification(), validator_1)

    assert block_0 != block_1


def test_unique_block_creation_in_test_lang(report):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
    test_lang = TestLangCBC({0: 10, 1: 11}, BlockchainProtocol, report)
    test_lang.parse(test_string)

    num_equal = 0
    for block in test_lang.blocks:
        for block1 in test_lang.blocks:
            if block1 == block:
                num_equal += 1
                continue

            assert block != block1

    assert num_equal == len(test_lang.blocks)


def test_is_in_blockchain__separate_genesis():
    validator_0 = Validator("v0", 10)
    validator_1 = Validator("v1", 11)

    block_0 = Block(None, Justification(), validator_0)
    block_1 = Block(None, Justification(), validator_1)

    assert not block_0.is_in_blockchain(block_1)
    assert not block_1.is_in_blockchain(block_0)


def test_is_in_blockchain__test_lang(report):
    test_string = "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D"
    test_lang = TestLangCBC({0: 11, 1: 10}, BlockchainProtocol, report)
    test_lang.parse(test_string)

    prev = test_lang.blocks['A']
    for b in ['B', 'C', 'D']:
        block = test_lang.blocks[b]
        assert prev.is_in_blockchain(block)
        assert not block.is_in_blockchain(prev)

        prev = block


@pytest.mark.parametrize(
    'test_string, weights, block_heights',
    [
        (
            "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D",
            {0: 11, 1: 10},
            {"A": 2, "B": 3, "C": 4, "D": 5}
        ),
        (
            "B0-A S1-A B1-B S0-B B0-C S1-C B1-D S0-D H0-D",
            {0: 1, 1: 10},
            {"A": 2, "B": 2, "C": 3, "D": 4}
        ),
        (
            "B0-A S1-A B0-B S1-B B1-C S0-C S2-C B2-D S0-D B0-E B1-F S0-F H0-E",
            {0: 11, 1: 10, 2: 500},
            {"A": 2, "B": 3, "C": 4, "D": 2, "E": 3, "F": 5}
        ),
    ]
)
def test_block_height(report, test_string, weights, block_heights):
    test_lang = TestLangCBC(weights, BlockchainProtocol, report)
    test_lang.parse(test_string)

    for block_name in block_heights:
        block = test_lang.blocks[block_name]
        assert block.height == block_heights[block_name]
