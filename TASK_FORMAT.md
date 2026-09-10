# Task 形式

task directory は `task.yaml` と `initial_prompt.md` を必須とし、private judge 設定は agent-visible context の外で Runner が読む。`task.yaml` は id、version、visibility、contamination status、leaderboard eligibility、target、software、objective、human policy、limits、tools、judge config path を持つ。

相対 path は task directory 基準で正規化し、directory 外参照を拒否する。公開 prompt に root cause、hidden check、reference patch を含めない。proprietary artifact は同梱せず、必要なら identifier/hash と外部 provisioning 要件だけを書く。

check は id、type、mode、required、説明と type 固有 config を持つ。mode は `automatic`、`semi-automatic`、`future`。future check は実装済みを装わず、required なら evidence がない限り FAIL になる。

