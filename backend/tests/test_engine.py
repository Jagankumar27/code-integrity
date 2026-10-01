import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.analyzers.similarity import analyze_batch
A = "a = 10\nb = 20\nresult = a + b\nprint(result)\n"
B = "# renamed\nx = 10\ny = 20\ntotal = x + y\nprint(total)\n"
C = "class Q:\n    def __init__(self):\n        self.items = []\n    def push(self, v):\n        self.items.append(v)\n"
def test_renamed_variables_detected():
    r = analyze_batch([{"id": 1, "filename": "a.py", "code": A}, {"id": 2, "filename": "b.py", "code": B},
                       {"id": 3, "filename": "c.py", "code": C}])
    d = {(x["a"], x["b"]): x for x in r}
    assert d[(1, 2)]["structural"] > 95 and d[(1, 2)]["token"] > 95
    assert d[(1, 2)]["overall"] > d[(1, 3)]["overall"] + 20
    assert any(e["title"].startswith("Similar structure despite") for e in d[(1, 2)]["explanations"])
if __name__ == "__main__":
    test_renamed_variables_detected(); print("ok")
