# Phase 13: Perf — Discussion Log

**Date:** 2026-10-27
**Areas offered:** Who measures / Where loading time goes / In-play freeze fix / Button lag handling
**Areas selected:** Where loading time goes, In-play freeze fix

| Question                                        | Options                                                  | Choice                |
| ----------------------------------------------- | -------------------------------------------------------- | --------------------- |
| When should heavy level work happen?            | Per level, yielding / All at boot / Hybrid               | Per level, yielding   |
| How are terrain and props produced during play? | Time-sliced streaming / Whole level at load / Web Worker | Time-sliced streaming |
| Shader warm-up before play?                     | Yes, during loading / Only if measured                   | Yes, during loading   |

Not discussed (Claude's discretion): measurement responsibility, button lag handling.
