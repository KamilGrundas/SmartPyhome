import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type ComputerPublic, ComputersService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const MAC_RE = /^([0-9A-Fa-f]{2}[:\-]){5}([0-9A-Fa-f]{2})$/

const formSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }).max(255),
  mac_address: z
    .string()
    .min(1, { message: "MAC address is required" })
    .regex(MAC_RE, { message: "Format: XX:XX:XX:XX:XX:XX" }),
  ip_address: z.string().max(45).optional().or(z.literal("")),
  description: z.string().max(255).optional().or(z.literal("")),
})

type FormData = z.infer<typeof formSchema>

interface EditComputerProps {
  computer: ComputerPublic
  onSuccess: () => void
}

const EditComputer = ({ computer, onSuccess }: EditComputerProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      name: computer.name,
      mac_address: computer.mac_address,
      ip_address: computer.ip_address ?? "",
      description: computer.description ?? "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      ComputersService.updateComputer({
        id: computer.id,
        requestBody: {
          name: data.name,
          mac_address: data.mac_address,
          ip_address: data.ip_address || null,
          description: data.description || null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Computer updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["computers"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Pencil />
        Edit
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
            <DialogHeader>
              <DialogTitle>Edit Computer</DialogTitle>
              <DialogDescription>Update the computer details.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="mac_address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>MAC Address <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input className="font-mono" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="ip_address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>IP / Broadcast Address</FormLabel>
                    <FormControl><Input className="font-mono" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>Cancel</Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>Save</LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default EditComputer
