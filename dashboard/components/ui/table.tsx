import { cn } from "@/lib/utils";

export const Table = (p: React.ComponentProps<"table">) => <table className="w-full text-sm" {...p} />;
export const TableHeader = (p: React.ComponentProps<"thead">) => <thead className="border-b text-left text-neutral-500" {...p} />;
export const TableBody = (p: React.ComponentProps<"tbody">) => <tbody {...p} />;
export const TableRow = (p: React.ComponentProps<"tr">) => <tr className="border-b last:border-0" {...p} />;
export const TableHead = ({ className, ...p }: React.ComponentProps<"th">) => <th className={cn("py-2 pr-4 font-medium", className)} {...p} />;
export const TableCell = ({ className, ...p }: React.ComponentProps<"td">) => <td className={cn("py-2 pr-4", className)} {...p} />;
