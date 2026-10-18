import { cn } from "@/lib/utils";

export function Card({ className, ...p }: React.ComponentProps<"div">) {
  return <div className={cn("rounded-xl border bg-white text-neutral-900 shadow-sm", className)} {...p} />;
}
export function CardHeader({ className, ...p }: React.ComponentProps<"div">) {
  return <div className={cn("p-6 pb-2", className)} {...p} />;
}
export function CardTitle({ className, ...p }: React.ComponentProps<"h2">) {
  return <h2 className={cn("text-lg font-semibold", className)} {...p} />;
}
export function CardContent({ className, ...p }: React.ComponentProps<"div">) {
  return <div className={cn("p-6 pt-2", className)} {...p} />;
}
