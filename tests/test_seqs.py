# -*- coding: UTF-8 -*-

import unittest
from collections import OrderedDict, Counter, deque, defaultdict

import clj as c


def test_infinite_range():
    """
    Test generator that fails if its 10k-th element is consumed.
    """
    n = 0
    while True:
        yield n
        n += 1
        assert n <= 10000


class TestSeqs(unittest.TestCase):

    def test_distinct(self):
        self.assertIsNotNone(c.distinct(test_infinite_range()))
        self.assertEquals([], list(c.distinct([])))
        self.assertEquals([1], list(c.distinct([1])))
        self.assertEquals([1, 2, 3, 4], list(c.distinct([1, 2, 3, 4])))
        self.assertEquals([2, 1, 3], list(c.distinct([2, 1, 3, 1, 2, 3])))

    def test_filter(self):
        self.assertIsNotNone(c.filter(lambda _: True, test_infinite_range()))

    def test_remove(self):
        self.assertIsNotNone(c.remove(lambda _: False, test_infinite_range()))
        self.assertEquals([], list(c.remove(lambda _: True, [])))
        self.assertEquals([], list(c.remove(lambda _: True, [1, 2, 3, 4])))
        self.assertEquals([1, 2, 3], list(c.remove(lambda _: False, [1, 2, 3])))
        self.assertEquals([1, 3], list(c.remove(lambda x: x == 2, [1, 2, 3])))

    def test_keep(self):
        self.assertIsNotNone(c.keep(lambda _: False, test_infinite_range()))
        self.assertEquals([], list(c.keep(lambda _: True, [])))
        self.assertEquals([], list(c.keep(lambda _: None, [])))
        self.assertEquals([], list(c.keep(lambda _: None, [1, 2, 3])))
        self.assertEquals([False, False], list(c.keep(lambda _: False, [1, 2])))
        self.assertEquals([1, 2], list(c.keep(lambda x: x, [1, None, 2])))

    def test_keep_indexed(self):
        self.assertIsNotNone(c.keep_indexed(lambda a, b: False, test_infinite_range()))

        def f(i, e): return e if i % 2 == 0 else None

        self.assertEquals(["a", "c"],
                          list(c.keep_indexed(f, ["a", "b", "c", "d"])))

    def test_cons(self):
        self.assertIsNotNone(c.cons(1, test_infinite_range()))
        self.assertEquals(1, c.first(c.cons(1, test_infinite_range())))
        self.assertEquals([1], list(c.cons(1, [])))
        self.assertEquals([[]], list(c.cons([], [])))
        self.assertEquals([5, 1], list(c.cons(5, [1])))

    def test_concat(self):
        self.assertIsNotNone(c.concat(test_infinite_range()))
        self.assertIsNotNone(c.concat(
            test_infinite_range(), test_infinite_range()))
        self.assertEquals([], list(c.concat()))
        self.assertEquals([], list(c.concat([])))
        self.assertEquals([], list(c.concat([], [], [], [])))
        self.assertEquals([1, 2], list(c.concat([1, 2], [])))
        self.assertEquals([1, 2, 3], list(c.concat([1, 2], [3])))

    def test_map(self):
        self.assertIsNotNone(c.map(lambda e: e, test_infinite_range()))
        self.assertEqual([1, 2, 3], list(c.map(lambda e: e + 1, range(3))))

        def plus(*xs):
            return sum(xs)

        self.assertEqual([9, 12], list(c.map(plus, [1, 2, 3], [2, 3, 4, 5], [6, 7])))

    def test_mapcat(self):
        def f(s): return s.split(",")

        self.assertEquals(["a", "b", "c", "d"],
                          list(c.mapcat(f, ["a,b", "c,d"])))

        g = c.mapcat(reversed, [[3, 2, 1, 0], [6, 5, 4], [9, 8, 7]])
        self.assertEquals(list(range(10)), list(g))
        self.assertIsNotNone(lambda _: test_infinite_range(), [1, 2, 3])

    def test_cycle(self):
        self.assertEqual([1, 2, 3, 1, 2, 3, 1, 2],
                         list(c.take(8, c.cycle([1, 2, 3]))))
        self.assertEqual([1, 2, 1, 2],
                         list(c.take(4, c.cycle(x for x in range(1, 3)))))
        self.assertIsNotNone(c.cycle(test_infinite_range()))

    def test_interleave(self):
        self.assertIsNotNone(c.interleave(
            test_infinite_range(), test_infinite_range()))
        self.assertEqual([1, 2, 3, 1, 2, 3, 1],
                         list(c.take(7,
                                     c.interleave(c.repeat(1),
                                                  c.repeat(2),
                                                  c.repeat(3)))))

        self.assertEquals([0, 500, 1, 501],
                          list(c.interleave(range(2), range(500, 1000))))

        self.assertEquals([500, 0, 501, 1],
                          list(c.interleave(range(500, 1000), range(2))))

    def test_interpose(self):
        self.assertIsNotNone(c.interpose(42, test_infinite_range()))
        self.assertEqual([], list(c.interpose(",", [])))
        self.assertEqual(["foo"], list(c.interpose(",", ["foo"])))
        self.assertEqual(["foo", ", ", "bar"],
                         list(c.interpose(", ", ["foo", "bar"])))

    def test_rest(self):
        self.assertIsNotNone(c.rest(test_infinite_range()))
        self.assertEquals([], list(c.rest([])))
        self.assertEquals([], list(c.rest([1])))
        self.assertEquals([2, 3, 4], list(c.rest([1, 2, 3, 4])))

    def test_drop(self):
        self.assertIsNotNone(c.drop(10, test_infinite_range()))
        self.assertEquals([], list(c.drop(0, [])))
        self.assertEquals([], list(c.drop(1000, [])))
        self.assertEquals([], list(c.drop(1000, [1, 2, 3, 4])))
        self.assertEquals([1, 2, 3, 4], list(c.drop(0, [1, 2, 3, 4])))
        self.assertEquals([1, 2, 3, 4], list(c.drop(-3, [1, 2, 3, 4])))
        self.assertEquals([4], list(c.drop(3, [1, 2, 3, 4])))

    def test_drop_while(self):
        self.assertIsNotNone(c.drop_while(lambda _: True, test_infinite_range()))
        self.assertEquals([], list(c.drop_while(lambda _: True, [])))
        self.assertEquals([], list(c.drop_while(lambda _: True, [1, 2, 3])))
        self.assertEquals([3, 1],
                          list(c.drop_while(lambda n: n < 3, [1, 2, 3, 1])))

    def test_take(self):
        self.assertIsNotNone(c.take(int(1e12), test_infinite_range()))
        self.assertEquals([], list(c.take(40, [])))
        self.assertEquals([], list(c.take(0, [1, 2, 3])))
        self.assertEquals([1, 2], list(c.take(2, [1, 2, 3])))
        self.assertEquals([1, 2, 3], list(c.take(3, [1, 2, 3])))
        self.assertEquals([1, 2, 3], list(c.take(4, [1, 2, 3])))

        els = []

        def _gen():
            for x in range(10):
                els.append(x)
                yield x

        c.dorun(c.take(0, _gen()))
        self.assertEquals([], els)

        self.assertEquals(els, list(c.take(5, _gen())))

    def test_take_nth(self):
        ls = [42, 25, 17, 1, 34, 87]
        self.assertEquals([1, 1, 1], list(c.take(3, c.take_nth(0, [1, 2]))))
        self.assertEquals([1, 1, 1], list(c.take(3, c.take_nth(-1, [1, 2]))))
        self.assertEquals(ls, list(c.take_nth(1, ls)))
        self.assertEquals(ls, list(c.take_nth(2, c.interleave(ls, range(20)))))

    def test_take_while(self):
        self.assertIsNotNone(c.take_while(lambda _: True, test_infinite_range()))
        self.assertEquals([], list(c.take_while(lambda _: True, [])))
        self.assertEquals([], list(c.take_while(lambda _: False, [1, 2, 3])))
        self.assertEquals([1, 2],
                          list(c.take_while(lambda n: n < 3, [1, 2, 3, 1])))

    def test_butlast(self):
        self.assertIsNotNone(c.butlast(test_infinite_range()))
        self.assertEquals([], list(c.butlast([])))
        self.assertEquals([], list(c.butlast([1])))
        self.assertEquals([1], list(c.butlast([1, 2])))
        self.assertEquals([1, 2, 3], list(c.butlast([1, 2, 3, 4])))

    def test_drop_last(self):
        self.assertEquals([], list(c.drop_last(0, [])))
        self.assertEquals([], list(c.drop_last(1, [])))
        self.assertEquals([], list(c.drop_last(1000, [])))
        self.assertEquals([1, 2], list(c.drop_last(-1, [1, 2])))
        self.assertEquals([1, 2], list(c.drop_last(-5, [1, 2])))
        self.assertEquals([], list(c.drop_last(2, [1, 2])))
        self.assertEquals([1, 2], list(c.drop_last(3, [1, 2, 3, 4, 5])))

    def test_flatten(self):
        self.assertEquals([], list(c.flatten([])))
        self.assertEquals([], list(c.flatten([[], [[[[], []], []]]])))
        self.assertEquals([1, 2, 3, 4],
                          list(c.flatten([[], [1, [[[], [2, 3]], []], 4]])))
        self.assertEquals(["foo", "bar"], list(c.flatten(["foo", "bar"])))

        self.assertEquals([0, 1, 2],
                          list(c.take(3, c.flatten(c.range()))),
                          "infinite generator")
        self.assertEquals([0, 1, 2],
                          list(c.take(3, c.flatten(c.range() for _ in c.range()))),
                          "infinite generator of infinite generators")
        self.assertEquals([1, 0, 1],
                          list(c.take(3, c.flatten([[1], c.range(), 42, c.range()]))),
                          "mix of single elements and infinite generators")

        """
        deep_list = ["foo"]
        for _ in range(200):
            deep_list = [[[[[deep_list]]]]]

        self.assertEquals(["foo"], list(c.flatten(deep_list)), "deep list")
        """

    def test_reverse(self):
        self.assertEquals([], list(c.reverse([])))
        self.assertEquals([3, 2, 1], list(c.reverse([1, 2, 3])))
        self.assertEquals([2, 1, 0], list(c.reverse(c.range(3))))

    def test_shuffle(self):
        self.assertEquals([], list(c.shuffle([])))
        self.assertEquals([], list(c.shuffle(c.range(0))))
        self.assertEquals([1, 2, 3], sorted(list(c.shuffle({1, 2, 3}))))

        ls = [1, 2, 3, 4]
        ls_orig = ls[:]
        self.assertEquals(ls, list(sorted(c.shuffle(ls))))
        self.assertEquals(ls_orig, ls)  # ensure it's not modified

    def test_split_at(self):
        self.assertEquals([[], []], list(map(list, c.split_at(0, []))))
        self.assertEquals([[], []], list(map(list, c.split_at(1, []))))
        self.assertEquals([[1], [2, 3]], list(map(list, c.split_at(1, [1, 2, 3]))))

        gen = (e for e in range(1, 7))
        self.assertEquals([[1, 2, 3], [4, 5, 6]], list(map(list, c.split_at(3, gen))))
        self.assertEquals([0, 1], list(c.split_at(2, test_infinite_range())[0]))

    def test_split_with(self):
        self.assertEquals([[], []],
                          list(map(list, c.split_with(lambda _: True, []))))
        self.assertEquals([[], []],
                          list(map(list, c.split_with(lambda _: False, []))))
        self.assertEquals([[1, 2], [3, 4, 3, 2, 1]],
                          list(map(list, c.split_with(lambda n: n < 3,
                                                      [1, 2, 3, 4, 3, 2, 1]))))

        gen = (e for e in range(1, 5))
        self.assertEquals([[1], [2, 3, 4]],
                          list(map(list, c.split_with(lambda n: n % 2 == 1, gen))))

        self.assertEquals([0, 1], list(c.split_with(lambda n: n < 2,
                                                    test_infinite_range())[0]))

    def test_replace(self):
        self.assertIsNotNone(c.replace({0: 1}, test_infinite_range()))
        self.assertEquals([], list(c.replace({}, [])))
        self.assertEquals([], list(c.replace({"a": "b"}, [])))
        self.assertEquals(["b"], list(c.replace({"a": "b"}, ["b"])))
        self.assertEquals(["b"], list(c.replace({"a": "b"}, ["a"])))
        self.assertEquals(["c"], list(c.replace({"a": "b"}, ["c"])))
        self.assertEquals(["b"], list(c.replace({"a": "b",
                                                 "b": "c"}, ["a"])))

    def test_map_indexed(self):
        self.assertIsNotNone(c.map_indexed(lambda i, e: e, test_infinite_range()))
        self.assertEquals([], list(c.map_indexed(lambda i, e: 42, [])))
        self.assertEquals([0, 1, 2],
                          list(c.map_indexed(lambda i, e: i, [5, 3, 1])))
        self.assertEquals([5, 4, 3],
                          list(c.map_indexed(lambda i, e: i + e, [5, 3, 1])))

    def test_first(self):
        self.assertEquals(None, c.first([]))
        self.assertEquals(42, c.first([42]))
        self.assertEquals(42, c.first([42, 1, 2, 3]))
        self.assertEquals(0, c.first(test_infinite_range()))

    def test_ffirst(self):
        self.assertEquals(None, c.ffirst([]))
        self.assertEquals(None, c.ffirst([[]]))
        self.assertEquals(42, c.ffirst([[42, 1], 2]))

    def test_nfirst(self):
        self.assertEquals([], list(c.nfirst([])))
        self.assertEquals([], list(c.nfirst([[]])))
        self.assertEquals([2, 3], list(c.nfirst([[1, 2, 3], 4])))

    def test_second(self):
        self.assertEquals(None, c.second([]))
        self.assertEquals(None, c.second([42]))
        self.assertEquals(1, c.second([42, 1, 2, 3]))
        self.assertEquals(1, c.second(test_infinite_range()))

    def test_nth(self):
        nope = object()
        self.assertEquals(nope, c.nth([], 0, nope))
        self.assertEquals(nope, c.nth([1, 2, 3, 4], -1, nope))
        self.assertEquals(nope, c.nth(c.range(999999999), -2, nope))
        self.assertEquals(nope, c.nth([], 1, nope))

        self.assertEquals(1, c.nth([42, 1, 2, 3], 1))
        self.assertEquals(7, c.nth([42, 1, 2, 3], 6, 7))

        self.assertEquals(20, c.nth(test_infinite_range(), 20))

    def test_last(self):
        self.assertEquals(None, c.last([]))
        self.assertEquals(1, c.last([1]))
        self.assertEquals(2, c.last([1, 2]))

    def test_zipmap(self):
        self.assertEquals({}, c.zipmap([], []))
        self.assertEquals({}, c.zipmap([], test_infinite_range()))
        self.assertEquals({}, c.zipmap(test_infinite_range(), []))
        self.assertEquals({"a": 1}, c.zipmap(("a",), [1]))
        self.assertEquals({"a": 1, "b": 2},
                          c.zipmap(["b", "a"], [2, 1]))

    def test_group_by(self):
        self.assertEquals({}, c.group_by(lambda e: e % 10, []))
        self.assertEquals({1: [1]}, c.group_by(lambda e: e % 10, [1]))
        self.assertEquals({1: [1, 5001], 3: [3]},
                          c.group_by(lambda e: e % 10, [1, 5001, 3]))

    def test_some(self):
        self.assertEquals(None, c.some(lambda e: True, []))
        self.assertEquals(None, c.some(lambda e: False, []))
        self.assertEquals(None, c.some({5}, []))
        self.assertEquals(None, c.some(lambda e: False, [1, 2, 3]))
        self.assertEquals(None, c.some({4, 5, 6}, [1, 2, 3]))
        self.assertEquals(2, c.some({4, 5, 6, 2}, [1, 2, 3]))
        self.assertEquals(None, c.some(lambda e: e > 4, [1, 2, 3]))
        self.assertEquals(2, c.some(lambda e: e > 1, [1, 2, 3]))

    def test_is_seq(self):
        self.assertFalse(c.is_seq(None))
        self.assertFalse(c.is_seq(42))
        self.assertFalse(c.is_seq(True))

        self.assertFalse(c.is_seq({42}))
        self.assertFalse(c.is_seq({42: 1}))
        self.assertFalse(c.is_seq(test_infinite_range()))

        self.assertTrue(c.is_seq([]))
        self.assertTrue(c.is_seq(()))

    def test_every(self):
        self.assertTrue(c.every(lambda e: e < 5, []))
        self.assertTrue(c.every(lambda e: e < 5, [1, 2, 3, 4]))
        self.assertFalse(c.every(lambda e: e < 5, [1, 2, 3, 4, 5]))

        self.assertTrue(c.every({1, 2, 3}, [1, 1, 3, 2, 3, 1, 2]))
        self.assertFalse(c.every({1, 2, 3}, [1, 1, 3, 4, 3, 1, 2]))

    def test_not_every(self):
        self.assertFalse(c.not_every(lambda e: e < 5, []))
        self.assertFalse(c.not_every(lambda e: e < 5, [1, 2, 3, 4]))
        self.assertTrue(c.not_every(lambda e: e < 5, [1, 2, 3, 4, 5]))

        self.assertFalse(c.not_every({1, 2, 3}, [1, 1, 3, 2, 3, 1, 2]))
        self.assertTrue(c.not_every({1, 2, 3}, [1, 1, 3, 4, 3, 1, 2]))

    def test_not_any(self):
        self.assertTrue(c.not_any(lambda e: e < 5, []))
        self.assertTrue(c.not_any(lambda e: e < 5, [6, 7, 8]))
        self.assertFalse(c.not_any(lambda e: e < 5, [6, 7, 8, 1]))

    def test_dorun(self):
        els = []

        def _gen():
            for x in range(10):
                els.append(x)
                yield x

        self.assertEquals(els, [])
        self.assertEquals(None, c.dorun(_gen()))
        self.assertEquals(els, list(range(10)))

    def test_repeatedly(self):
        els = []

        def add_el():
            els.append(42)

        c.dorun(c.take(3, c.repeatedly(add_el)))
        self.assertEquals([42, 42, 42], els)

        els = []
        c.dorun(c.repeatedly(add_el, 2))
        self.assertEquals([42, 42], els)

    def test_iterate(self):
        def inc(x): return x + 1

        self.assertEquals(10, c.nth(c.iterate(inc, 0), 10))

    def test_repeat(self):
        self.assertEquals([2, 2, 2], list(c.take(3, c.repeat(2))))
        self.assertEquals([2, 2, 2], list(c.repeat(2, 3)))
        self.assertEquals([], list(c.repeat(2, 0)))
        self.assertEquals([], list(c.repeat(2, -1)))

    def test_range(self):
        self.assertEquals([], list(c.range(2, 1)))
        self.assertEquals([2], list(c.range(2, 1, -1)))
        self.assertEquals([0, 1, 2, 3], list(c.range(4)))
        self.assertEquals([0, 1, 2, 3], list(c.take(4, test_infinite_range())))

    def test_count(self):
        self.assertEquals(10, c.count("qwertyuiop"))
        self.assertEquals(0, c.count([]))
        self.assertEquals(0, c.count(()))
        self.assertEquals(0, c.count({}))
        self.assertEquals(1, c.count({"foo": "bar"}))
        self.assertEquals(10, c.count(c.take(10, test_infinite_range())))

        class Uniterable:
            def __iter__(self):
                raise RuntimeError("boom!")

            def __len__(self):
                return 42

        self.assertEquals(42, c.count(Uniterable()))

    def test_tree_seq(self):
        def boom(_):
            raise RuntimeError("boom!")

        self.assertEquals([42],
                          list(c.tree_seq(lambda _: False, boom, 42)))

        t = [[1, 2, [3]], [4]]
        self.assertEquals([t, [1, 2, [3]], 1, 2, [3], 3, [4], 4],
                          list(c.tree_seq(c.is_seq, c.identity, t)))

        t = ["C", ["l", ["o"], ["j"]], ["u", ["r"]], ["e"]]
        self.assertEquals(["C", "l", "o", "j", "u", "r", "e"],
                          list(map(c.first, c.tree_seq(c.rest, c.rest, t))))

    def test_dedupe(self):
        self.assertEquals([], list(c.dedupe([])))
        self.assertEquals([1], list(c.dedupe([1])))
        self.assertEquals([1, 2], list(c.dedupe([1, 2])))
        self.assertEquals([1], list(c.dedupe([1, 1])))
        self.assertEquals([1], list(c.dedupe([1, 1, 1])))
        self.assertEquals([1, 2, 1], list(c.dedupe([1, 1, 2, 2, 1])))

    def test_empty(self):
        self.assertEquals([], c.empty([]))
        self.assertEquals([], c.empty([1, 2, 3]))
        self.assertEquals((), c.empty(()))
        self.assertEquals((), c.empty((1, 2, 3)))
        self.assertEquals({}, c.empty({}))
        self.assertEquals({}, c.empty({"a": 42}))
        self.assertEquals(set(), c.empty(set()))
        self.assertEquals(set(), c.empty({1, 2}))

        for e in ([], (), {}, set(), defaultdict(), deque(), Counter(),
                  OrderedDict()):
            self.assertEquals(e, c.empty(e))

        import re

        for x in (0, 42, None, True, False, lambda: 1, re, self):
            self.assertIsNone(c.empty(x))

    def test_partition(self):
        for n in (1, 2, 1000, -3, 0):
            self.assertSequenceEqual([], list(c.partition([], n)))

        for n in (0, -1, -200):
            self.assertSequenceEqual([], list(c.partition([1, 2, 3, 4], n)))

        self.assertSequenceEqual([[1], [2], [3]], list((c.partition([1, 2, 3], 1))))
        self.assertSequenceEqual([[1, 2]], list((c.partition([1, 2, 3], 2))))
        self.assertSequenceEqual([[1, 2], [3, 4]], list((c.partition([1, 2, 3, 4], 2))))
        self.assertSequenceEqual([[1, 2, 3]], list((c.partition([1, 2, 3], 3))))

        # pad
        self.assertSequenceEqual([[1], [2], [3]], list((c.partition([1, 2, 3], 1, pad=[4]))))
        self.assertSequenceEqual([[1, 2], [3, 4]], list((c.partition([1, 2, 3], 2, pad=[4]))))
        self.assertSequenceEqual([[1, 2], [3, 4]], list((c.partition([1, 2, 3, 4], 2, pad=[5]))))
        self.assertSequenceEqual([[1, 2, 3]], list((c.partition([1, 2, 3], 3, pad=[4]))))

        self.assertSequenceEqual([[1, 2, 3], [4, 5]], list((c.partition([1, 2, 3, 4], 3, pad=[5]))))
        self.assertSequenceEqual([[1, 2, 3], [4, 5, 6]], list((c.partition([1, 2, 3, 4], 3, pad=[5, 6]))))

    def test_partition_by(self):
        self.assertSequenceEqual([], list(c.partition_by(c.is_odd, [])))
        self.assertSequenceEqual([[{"a": 2}], [False]], list(c.partition_by(c.identity, [{"a": 2}, False])))

        # From the examples on https://clojuredocs.org/clojure.core/partition-by
        # (partition-by #(= 3 %) [1 2 3 4 5]) ; => ((1 2) (3) (4 5))
        self.assertSequenceEqual(
            [[1, 2], [3], [4, 5]],
            list(c.partition_by(lambda x: x == 3, [1, 2, 3, 4, 5]))
        )

        # (partition-by odd? [1 1 1 2 2 3 3])  ; => ((1 1 1) (2 2) (3 3))
        self.assertSequenceEqual(
            [[1, 1, 1], [2, 2], [3, 3]],
            list(c.partition_by(c.is_odd, [1, 1, 1, 2, 2, 3, 3]))
        )

        # (partition-by even? [1 1 1 2 2 3 3]) ; => ((1 1 1) (2 2) (3 3))
        self.assertSequenceEqual(
            [[1, 1, 1], [2, 2], [3, 3]],
            list(c.partition_by(c.is_even, [1, 1, 1, 2, 2, 3, 3]))
        )

        # (partition-by identity "Leeeeeerrroyyy") ; => ((\L) (\e \e \e \e \e \e) (\r \r \r) (\o) (\y \y \y))
        self.assertSequenceEqual(
            [["L"], ["e"] * 6, ["r"] * 3, ["o"], ["y"] * 3],
            list(c.partition_by(c.identity, "Leeeeeerrroyyy"))
        )

        # (partition-by identity "ABBA") ; => ((\A) (\B \B) (\A))
        self.assertSequenceEqual(
            [["A"], ["B", "B"], ["A"]], list(c.partition_by(c.identity, "ABBA"))
        )
