export const allowedAudioExtensions = [".mp3", ".wav", ".m4a"] as const;

export function isAllowedAudioFileName(fileName: string) {
  const lowerName = fileName.toLowerCase();
  return allowedAudioExtensions.some((extension) => lowerName.endsWith(extension));
}
