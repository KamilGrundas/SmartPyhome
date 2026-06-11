import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Monitor } from "lucide-react"
import { Suspense } from "react"

import { ComputersService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddComputer from "@/components/Computers/AddComputer"
import { columns } from "@/components/Computers/columns"
import PendingComputers from "@/components/Pending/PendingComputers"

function getComputersQueryOptions() {
  return {
    queryFn: () => ComputersService.readComputers({ skip: 0, limit: 100 }),
    queryKey: ["computers"],
  }
}

export const Route = createFileRoute("/_layout/computers")({
  component: Computers,
  head: () => ({
    meta: [{ title: "Computers - SmartPyhome" }],
  }),
})

function ComputersTableContent() {
  const { data: computers } = useSuspenseQuery(getComputersQueryOptions())

  if (computers.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Monitor className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No computers yet</h3>
        <p className="text-muted-foreground">Add a computer to wake it up remotely</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={computers.data} />
}

function Computers() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Computers</h1>
          <p className="text-muted-foreground">Wake your computers remotely via Wake-on-LAN</p>
        </div>
        <AddComputer />
      </div>
      <Suspense fallback={<PendingComputers />}>
        <ComputersTableContent />
      </Suspense>
    </div>
  )
}
