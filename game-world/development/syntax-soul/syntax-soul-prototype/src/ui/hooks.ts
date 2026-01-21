import { useEffect, useState } from "react";

export function useLocalStorageState<T>(key: string, fallback: T): [T, (v: T) => void, () => void] {
  const [value, setValue] = useState<T>(() => {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return fallback;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  const reset = () => setValue(fallback);
  return [value, setValue, reset];
}
