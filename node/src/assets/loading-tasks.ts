/** One step of the loading screen: building a scene, compiling shaders, fetching a file... */
export type LoadingTask = () => void | Promise<void>;

/**
 * Runs `tasks` in order and reports real progress (ENG-108): 0 before the first task, then
 * `done / total` after each one. `yieldToBrowser` runs before each task so the progress bar
 * can be painted between steps.
 */
export async function runLoadingTasks(
  tasks: readonly LoadingTask[],
  onProgress: (progress: number) => void,
  yieldToBrowser: () => Promise<void>,
): Promise<void> {
  onProgress(0);
  for (const [i, task] of tasks.entries()) {
    await yieldToBrowser();
    await task();
    onProgress((i + 1) / tasks.length);
  }
  if (tasks.length === 0) onProgress(1);
}
