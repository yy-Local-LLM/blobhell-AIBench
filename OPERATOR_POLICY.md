# オペレーターポリシー

原則は「人間はデバッグしない。ハードウェアが判定する」である。

許可される行為は、未自動化の物理操作、要求された直接観測の忠実な報告、接続・切断・再起動、および harness が取得不能な raw output の転記に限る。すべて `human_operator_action` として記録する。

ログの解釈、コマンド・原因・修正案の提案、過去 run の知識、reference solution、仮説の正否は伝えてはならない。OMX、Stagefright、ACodec、VCODEC、buffer count、DPB、kernel ABI 等へ誘導することも禁止する。technical hint count が 0 でない run は有効な PASS にならない。

観測報告は「画面が黒い」「再生時間表示が進んだ」のように依頼された事実だけを返し、推論を添えない。迷った場合は回答せず、拒否した事実を記録する。

