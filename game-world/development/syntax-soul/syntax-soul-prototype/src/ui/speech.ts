import { CadenceMode, Soul } from "../core/types";
import { deriveStats } from "../core/engine";

export function canSpeak(): boolean {
  return !!(window.speechSynthesis && window.SpeechSynthesisUtterance);
}

export function speakBar(bar: string, soul: Soul, cadence: CadenceMode): void {
  if (!canSpeak()) return;
  const stats = deriveStats(soul).total;

  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(bar);

  const cadenceRate = cadence === "DOUBLE_TIME" ? 1.45 : cadence === "HALF_TIME" ? 0.95 : 1.08;
  u.rate = Math.max(0.85, Math.min(1.8, cadenceRate + stats.flow / 220));
  u.pitch = Math.max(0.55, Math.min(1.2, 1.0 - stats.aggression / 220));
  u.volume = 0.9;

  window.speechSynthesis.speak(u);
}
