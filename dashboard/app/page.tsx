import { Suspense } from "react";
import { connection } from "next/server";
import { supabase } from "@/lib/supabase";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

async function Data() {
  await connection();
  const [shoots, queue] = await Promise.all([
    supabase.from("shoots").select("id,client_name,status,amount,shoot_date,deadline").order("shoot_date", { ascending: false }).limit(50),
    supabase.from("work_queue").select("id,item_number,title,status").order("item_number").limit(50),
  ]);

  return (
    <>

      <Card>
        <CardHeader><CardTitle>Shoots ({shoots.data?.length ?? 0})</CardTitle></CardHeader>
        <CardContent>
          {shoots.error && <p className="text-red-600">{shoots.error.message}</p>}
          <Table>
            <TableHeader><TableRow><TableHead>Client</TableHead><TableHead>Status</TableHead><TableHead>Amount</TableHead><TableHead>Shoot date</TableHead><TableHead>Deadline</TableHead></TableRow></TableHeader>
            <TableBody>
              {shoots.data?.map((s) => (
                <TableRow key={s.id}><TableCell>{s.client_name}</TableCell><TableCell>{s.status}</TableCell><TableCell>{s.amount}</TableCell><TableCell>{s.shoot_date}</TableCell><TableCell>{s.deadline}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Work queue ({queue.data?.length ?? 0})</CardTitle></CardHeader>
        <CardContent>
          {queue.error && <p className="text-red-600">{queue.error.message}</p>}
          <Table>
            <TableHeader><TableRow><TableHead>#</TableHead><TableHead>Title</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {queue.data?.map((q) => (
                <TableRow key={q.id}><TableCell>{q.item_number}</TableCell><TableCell>{q.title}</TableCell><TableCell>{q.status}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  );
}

export default function Home() {
  return (
    <main className="mx-auto max-w-4xl space-y-6 p-6">
      <h1 className="text-2xl font-bold">Dashboard — connectivity test</h1>
      <Suspense fallback={<p>Loading…</p>}><Data /></Suspense>
    </main>
  );
}
