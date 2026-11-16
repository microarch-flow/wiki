"""Check the published NoC trace example against its stated contract."""

import copy
from pathlib import Path
import re
import unittest


ARTICLE = (Path(__file__).resolve().parents[2] / "series/interconnect/NOC"
           / "07-evaluation-methodology/trace-generation-worked-example.md")


class NocTraceExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        match = re.search(r"```python\n(.*?)\n```", ARTICLE.read_text(encoding="utf-8"), re.DOTALL)
        if match is None:
            raise AssertionError("published Python example is missing")
        cls.module = {"__name__": "noc_trace_example"}
        exec(compile(match.group(1), str(ARTICLE), "exec"), cls.module)

    def test_example_counts_and_self_check(self):
        trace = self.module["make_trace"]()
        self.module["check_example"](trace)
        self.assertEqual(len(trace["events"]), 115)
        self.assertEqual(self.module["count_traffic"](trace, "shared")["wire_byte_hop"], 251660160)
        self.assertEqual(self.module["count_traffic"](trace, "unicast")["wire_byte_hop"], 452988288)

    def test_small_tree_and_unicast_accounting(self):
        trace = {"schema": "noc-workload-v1", "events": [{
            "kind": "flow", "id": "one", "release_time": 0, "depends_on": [],
            "src_node": 0, "dst_set": [0, 1, 3], "traffic_class": "STREAM", "payload_bytes": 16,
        }]}
        self.module["validate_trace"](trace)
        shared = self.module["count_traffic"](trace, "shared")
        unicast = self.module["count_traffic"](trace, "unicast")
        self.assertEqual((shared["consumer_payload"], shared["local_payload"]), (48, 16))
        self.assertEqual((shared["injection_payload"], shared["wire_byte_hop"]), (16, 96))
        self.assertEqual((unicast["injection_payload"], unicast["wire_byte_hop"]), (32, 128))

    def test_rejects_invalid_fields_and_dependencies(self):
        baseline = self.module["make_trace"]()
        compute_index = next(i for i, e in enumerate(baseline["events"]) if e["id"] == "C0_0_0")
        changes = [
            (0, "src_node", -1),
            (compute_index, "node", -1),
            (0, "traffic_class", "UNKNOWN"),
            (0, "traffic_class", []),
            (0, "release_time", -1),
            (0, "release_time", True),
            (0, "payload_bytes", 0),
            (0, "dst_set", [0, 0]),
            (0, "depends_on", ["missing"]),
            (0, "depends_on", ["C0_0_0"]),
            (1, "id", baseline["events"][0]["id"]),
        ]
        for index, field, value in changes:
            with self.subTest(index=index, field=field, value=value):
                trace = copy.deepcopy(baseline)
                trace["events"][index][field] = value
                with self.assertRaises(ValueError):
                    self.module["validate_trace"](trace)


if __name__ == "__main__":
    unittest.main()
