"""把仍有效的11项低层主机契约脚本纳入统一make test，不执行AM或RTL。"""

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "test-completion.py", "test-dma-poll.py", "test-fixture-diagnostics.py",
    "test-log.py", "test-plic-address.py", "test-progress.py", "test-result-report.py",
    "test-runtime-wait.py", "test-stage-reference.py", "test-v2-memory.py",
    "test-verify-silent-elf.py",
)


class LowLevelHostContracts(unittest.TestCase):
    def test_lowlevel_contract_scripts(self):
        build = ROOT / "build/host-tests"
        temporary = build / "temporary"
        temporary.mkdir(parents=True, exist_ok=True)
        environment = dict(os.environ, TMPDIR=str(temporary))
        for script in SCRIPTS:
            with self.subTest(script=script):
                result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)],
                                        cwd=ROOT, env=environment, text=True, capture_output=True)
                (build / (script.removesuffix(".py") + ".log")).write_text(result.stdout + result.stderr)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
