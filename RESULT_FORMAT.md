# Result 形式

`result.json` は run の最終判定を表す。必須 field は benchmark、task、task_version、run_id、model、agent_adapter、result、leaderboard_eligible、contamination_status、human_technical_hints、時間・turn・tool/build/reboot/failed experiment 数、checkpoints、judge である。

`result` は PASS / FAIL / ERROR。Agent の自己申告値は格納しても採点に使わない。公開 reference は check を満たしても `leaderboard_eligible=false` のままである。token/quota は vendor 差があるため optional metadata とする。judge.checks は check ごとの status、mode、evidence、message を保持する。

