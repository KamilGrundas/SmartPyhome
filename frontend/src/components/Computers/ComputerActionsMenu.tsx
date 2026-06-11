import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { ComputerPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteComputer from "./DeleteComputer"
import EditComputer from "./EditComputer"

interface ComputerActionsMenuProps {
  computer: ComputerPublic
}

export const ComputerActionsMenu = ({ computer }: ComputerActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditComputer computer={computer} onSuccess={() => setOpen(false)} />
        <DeleteComputer id={computer.id} name={computer.name} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
