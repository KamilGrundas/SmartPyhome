import type { ColumnDef } from "@tanstack/react-table"
import { useMutation } from "@tanstack/react-query"
import { Zap } from "lucide-react"

import type { ComputerPublic } from "@/client"
import { ComputersService } from "@/client"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { ComputerActionsMenu } from "./ComputerActionsMenu"

function WakeButton({ computer }: { computer: ComputerPublic }) {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => ComputersService.wakeComputer({ id: computer.id }),
    onSuccess: (data) => showSuccessToast(data.message),
    onError: handleError.bind(showErrorToast),
  })

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="text-yellow-500 border-yellow-500/30 hover:bg-yellow-500/10 hover:text-yellow-400"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
          >
            <Zap className="size-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Wake up</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

export const columns: ColumnDef<ComputerPublic>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.name}</span>
    ),
  },
  {
    accessorKey: "mac_address",
    header: "MAC Address",
    cell: ({ row }) => (
      <span className="font-mono text-sm text-muted-foreground">
        {row.original.mac_address}
      </span>
    ),
  },
  {
    accessorKey: "ip_address",
    header: "IP Address",
    cell: ({ row }) => (
      <span className="font-mono text-sm text-muted-foreground">
        {row.original.ip_address || "—"}
      </span>
    ),
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => (
      <span className="text-muted-foreground text-sm">
        {row.original.description || "—"}
      </span>
    ),
  },
  {
    id: "wake",
    header: () => <span className="sr-only">Wake</span>,
    cell: ({ row }) => <WakeButton computer={row.original} />,
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <ComputerActionsMenu computer={row.original} />
      </div>
    ),
  },
]
