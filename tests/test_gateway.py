import asyncio
from blobhell.tools.shell import run_command

def test_subprocess_timeout(tmp_path):
    result = asyncio.run(run_command(["sh", "-c", "sleep 2"], tmp_path, {"PATH": "/usr/bin:/bin"}, .02))
    assert result.timed_out and result.exit_code is None

