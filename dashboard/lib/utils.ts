export function cn(...c: (string | false | undefined)[]) {
  return c.filter(Boolean).join(" ");
}
