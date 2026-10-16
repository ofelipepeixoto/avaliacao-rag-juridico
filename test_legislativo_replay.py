# Copyright (c) 2026 Carlos Felipe
# SPDX-License-Identifier: MIT
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('legislative_replay',ROOT/'experiments/legislativo/replay.py')
replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
PACKAGE=ROOT/'experiments/legislativo/fixture-package.json'
SHA='1d9034bdd2d6448c35733664099cb0e25709fb89e282db809e1c0ebe3171e347'


class LegislativeReplayTest(unittest.TestCase):
    def setUp(self):self.package=replay.load_package(PACKAGE,SHA)

    def test_consumes_pinned_fixture_without_promoting_legal_quality(self):
        result=replay.review(self.package)
        self.assertFalse(result['legal_correctness_verified'])
        self.assertFalse(result['authorization_to_execute'])
        self.assertEqual(sum(m['total'] for m in result['metrics_by_split'].values()),54)
        self.assertEqual(result['metrics_by_split']['test']['precision_at_1'],1)

    def test_hash_mismatch_and_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):replay.load_package(PACKAGE,'0'*64)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.json';path.write_text('{"x":1,"x":2}')
            with self.assertRaises(ValueError):replay.load_package(path,'0'*64)

    def test_source_and_case_hash_changes_rejected(self):
        for key in ['text','expected']:
            package=copy.deepcopy(self.package)
            if key=='text':package['corpus'][0]['text']='altered'
            else:package['cases'][0]['expected']=None
            with self.assertRaises(ValueError):replay.review(package)

    def test_fabricated_citation_approval_is_not_accepted(self):
        self.package['replay']['rows'][0]['citation']['review_status']='approved'
        with self.assertRaises(ValueError):replay.review(self.package)

    def test_wrong_version_and_house_are_rejected(self):
        self.package['replay']['rows'][0]['obtido']=self.package['corpus'][1]['id']
        with self.assertRaises(ValueError):replay.review(self.package)
        self.package=replay.load_package(PACKAGE,SHA)
        self.package['replay']['rows'][0]['obtido']=self.package['corpus'][4]['id']
        with self.assertRaises(ValueError):replay.review(self.package)

    def test_missing_or_duplicated_case_cannot_inflate_metrics(self):
        for mode in ['missing','duplicate']:
            package=copy.deepcopy(self.package)
            if mode=='missing':package['replay']['rows'].pop()
            else:package['replay']['rows'].append(package['replay']['rows'][0])
            with self.assertRaises(ValueError):replay.review(package)

    def test_cross_split_family_is_rejected_even_with_rebound_hash(self):
        self.package['corpus'][1]['split']='test'
        self.package['replay']['corpus_sha256']=hashlib.sha256(replay.canonical(self.package['corpus'])).hexdigest()
        with self.assertRaises(ValueError):replay.review(self.package)

if __name__=='__main__':unittest.main()
