import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type ComputerCreate, ComputersService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
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

const AddComputer = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: { name: "", mac_address: "", ip_address: "", description: "" },
  })

  const mutation = useMutation({
    mutationFn: (data: ComputerCreate) =>
      ComputersService.createComputer({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Computer added successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["computers"] }),
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate({
      name: data.name,
      mac_address: data.mac_address,
      ip_address: data.ip_address || null,
      description: data.description || null,
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Add Computer
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Computer</DialogTitle>
          <DialogDescription>
            Enter the computer details to enable Wake-on-LAN.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name <span className="text-destructive">*</span></FormLabel>
                    <FormControl>
                      <Input placeholder="My Desktop" {...field} />
                    </FormControl>
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
                    <FormControl>
                      <Input placeholder="AA:BB:CC:DD:EE:FF" className="font-mono" {...field} />
                    </FormControl>
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
                    <FormControl>
                      <Input placeholder="192.168.1.255" className="font-mono" {...field} />
                    </FormControl>
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
                    <FormControl>
                      <Input placeholder="Optional note" {...field} />
                    </FormControl>
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

export default AddComputer
