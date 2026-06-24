import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import type { ColumnDef } from "@tanstack/react-table"
import {
  CheckCircle,
  CreditCard,
  EllipsisVertical,
  Layers,
  MapPin,
  Pencil,
  Plus,
  ScrollText,
  Settings2,
  Trash2,
  XCircle,
} from "lucide-react"
import { Suspense, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type AccessCardPublic,
  type AccessGroupPublic,
  type AccessLogPublic,
  type AccessPointPublic,
  AccessService,
  UsersService,
} from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

// ── Route ─────────────────────────────────────────────────────────────────────

const tabValues = ["cards", "groups", "locations", "logs"] as const
type TabValue = (typeof tabValues)[number]

export const Route = createFileRoute("/_layout/access-cards")({
  validateSearch: (search: Record<string, unknown>) => ({
    tab: (tabValues.includes(search.tab as TabValue) ? search.tab : "cards") as TabValue,
  }),
  component: AccessCards,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!user.is_superuser) {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Access Cards - SmartPyhome" }],
  }),
})

// ── Query helpers ─────────────────────────────────────────────────────────────

function getCardsQueryOptions() {
  return {
    queryFn: () => AccessService.listCards({ skip: 0, limit: 500 }),
    queryKey: ["access-cards"],
  }
}

function getGroupsQueryOptions() {
  return {
    queryFn: () => AccessService.listGroups({ skip: 0, limit: 500 }),
    queryKey: ["access-groups"],
  }
}

function getPointsQueryOptions() {
  return {
    queryFn: () => AccessService.listPoints({ skip: 0, limit: 500 }),
    queryKey: ["access-points"],
  }
}

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 500 }),
    queryKey: ["users"],
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CARDS TAB
// ═══════════════════════════════════════════════════════════════════════════════

const cardFormSchema = z.object({
  label: z.string().min(1, { message: "Label is required" }).max(255),
  uid: z.string().min(1, { message: "UID is required" }).max(50),
  user_id: z.string().nullable().optional(),
  is_active: z.boolean(),
})

type CardFormData = z.infer<typeof cardFormSchema>

// ── Add Card ──────────────────────────────────────────────────────────────────

function AddCard() {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const form = useForm<CardFormData>({
    resolver: zodResolver(cardFormSchema),
    mode: "onBlur",
    defaultValues: { label: "", uid: "", user_id: null, is_active: true },
  })

  const mutation = useMutation({
    mutationFn: (data: CardFormData) =>
      AccessService.createCard({
        requestBody: {
          label: data.label,
          uid: data.uid,
          user_id: data.user_id || null,
          is_active: data.is_active,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Card added successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-cards"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Add Card
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Access Card</DialogTitle>
          <DialogDescription>Register a new RFID card in the system.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="label"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Label <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input placeholder="Front door card" {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="uid"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>UID <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input placeholder="AA:BB:CC:DD" className="font-mono" {...field} /></FormControl>
                    <FormDescription>RFID card UID, e.g. AA:BB:CC:DD</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="user_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Assign to User</FormLabel>
                    <Select
                      onValueChange={(v) => field.onChange(v === "__none__" ? null : v)}
                      value={field.value ?? "__none__"}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="No user" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="__none__">— No user —</SelectItem>
                        {users.data.map((u) => (
                          <SelectItem key={u.id} value={u.id}>
                            {u.username}{u.full_name ? ` (${u.full_name})` : ""}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex items-center gap-3 space-y-0">
                    <FormControl>
                      <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                    <FormLabel className="font-normal">Active</FormLabel>
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

// ── Edit Card ─────────────────────────────────────────────────────────────────

function EditCard({ card, onSuccess }: { card: AccessCardPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const form = useForm<CardFormData>({
    resolver: zodResolver(cardFormSchema),
    mode: "onBlur",
    defaultValues: {
      label: card.label,
      uid: card.uid,
      user_id: card.user_id ?? null,
      is_active: card.is_active,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: CardFormData) =>
      AccessService.updateCard({
        cardId: card.id,
        requestBody: {
          label: data.label,
          uid: data.uid,
          user_id: data.user_id || null,
          is_active: data.is_active,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Card updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-cards"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Pencil />
        Edit Card
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Card</DialogTitle>
          <DialogDescription>Update the card details.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="label"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Label <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="uid"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>UID <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input className="font-mono" {...field} /></FormControl>
                    <FormDescription>RFID card UID, e.g. AA:BB:CC:DD</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="user_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Assign to User</FormLabel>
                    <Select
                      onValueChange={(v) => field.onChange(v === "__none__" ? null : v)}
                      value={field.value ?? "__none__"}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="No user" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="__none__">— No user —</SelectItem>
                        {users.data.map((u) => (
                          <SelectItem key={u.id} value={u.id}>
                            {u.username}{u.full_name ? ` (${u.full_name})` : ""}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex items-center gap-3 space-y-0">
                    <FormControl>
                      <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                    </FormControl>
                    <FormLabel className="font-normal">Active</FormLabel>
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

// ── Delete Card ───────────────────────────────────────────────────────────────

function DeleteCard({ card, onSuccess }: { card: AccessCardPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => AccessService.deleteCard({ cardId: card.id }),
    onSuccess: () => {
      showSuccessToast("Card deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-cards"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
        className="text-destructive focus:text-destructive"
      >
        <Trash2 />
        Delete
      </DropdownMenuItem>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Card</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete <strong>{card.label}</strong>? This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>Cancel</Button>
          </DialogClose>
          <LoadingButton
            variant="destructive"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Manage Card Access ────────────────────────────────────────────────────────

function ManageCardAccess({ card, onSuccess }: { card: AccessCardPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const { data: pointsData } = useSuspenseQuery(getPointsQueryOptions())
  const { data: groupsData } = useSuspenseQuery(getGroupsQueryOptions())

  const togglePoint = useMutation({
    mutationFn: ({ pointId, add }: { pointId: string; add: boolean }) =>
      add
        ? AccessService.addCardPoint({ cardId: card.id, pointId })
        : AccessService.removeCardPoint({ cardId: card.id, pointId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["access-cards"] }),
    onError: handleError.bind(showErrorToast),
  })

  const toggleGroup = useMutation({
    mutationFn: ({ groupId, add }: { groupId: string; add: boolean }) =>
      add
        ? AccessService.addCardGroup({ cardId: card.id, groupId })
        : AccessService.removeCardGroup({ cardId: card.id, groupId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["access-cards"] }),
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Settings2 />
        Manage Access
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Manage Access — {card.label}</DialogTitle>
          <DialogDescription>
            Assign direct access points and groups to this card.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-6 py-4">
          <div>
            <p className="text-sm font-medium mb-2">Direct Access Points</p>
            <div className="flex flex-col gap-2">
              {pointsData.data.length === 0 && (
                <p className="text-sm text-muted-foreground">No locations defined yet.</p>
              )}
              {pointsData.data.map((pt) => {
                const checked = card.access_point_ids.includes(pt.id)
                return (
                  <label key={pt.id} className="flex items-center gap-2 cursor-pointer">
                    <Checkbox
                      checked={checked}
                      onCheckedChange={(val) =>
                        togglePoint.mutate({ pointId: pt.id, add: !!val })
                      }
                    />
                    <span className="text-sm">{pt.name}</span>
                    {pt.description && (
                      <span className="text-xs text-muted-foreground">— {pt.description}</span>
                    )}
                  </label>
                )
              })}
            </div>
          </div>
          <div>
            <p className="text-sm font-medium mb-2">Groups</p>
            <div className="flex flex-col gap-2">
              {groupsData.data.length === 0 && (
                <p className="text-sm text-muted-foreground">No groups defined yet.</p>
              )}
              {groupsData.data.map((g) => {
                const checked = card.group_ids.includes(g.id)
                return (
                  <label key={g.id} className="flex items-center gap-2 cursor-pointer">
                    <Checkbox
                      checked={checked}
                      onCheckedChange={(val) =>
                        toggleGroup.mutate({ groupId: g.id, add: !!val })
                      }
                    />
                    <span className="text-sm">{g.name}</span>
                    {g.description && (
                      <span className="text-xs text-muted-foreground">— {g.description}</span>
                    )}
                  </label>
                )
              })}
            </div>
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button onClick={() => { onSuccess(); setIsOpen(false) }}>Done</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Card Actions Menu ─────────────────────────────────────────────────────────

function CardActionsMenu({ card }: { card: AccessCardPublic }) {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditCard card={card} onSuccess={() => setOpen(false)} />
        <ManageCardAccess card={card} onSuccess={() => setOpen(false)} />
        <DeleteCard card={card} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// ── Cards Table ───────────────────────────────────────────────────────────────

function CardsTableContent() {
  const { data: cards } = useSuspenseQuery(getCardsQueryOptions())
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const userMap = new Map(users.data.map((u) => [u.id, u.username]))

  const columns: ColumnDef<AccessCardPublic>[] = [
    {
      accessorKey: "label",
      header: "Label",
      cell: ({ row }) => <span className="font-medium">{row.original.label}</span>,
    },
    {
      accessorKey: "uid",
      header: "UID",
      cell: ({ row }) => (
        <span className="font-mono text-sm text-muted-foreground">{row.original.uid}</span>
      ),
    },
    {
      accessorKey: "user_id",
      header: "User",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.user_id ? (userMap.get(row.original.user_id) ?? "—") : "—"}
        </span>
      ),
    },
    {
      accessorKey: "is_active",
      header: "Active",
      cell: ({ row }) =>
        row.original.is_active ? (
          <Badge variant="default">Active</Badge>
        ) : (
          <Badge variant="secondary">Inactive</Badge>
        ),
    },
    {
      id: "access_points",
      header: "Access Points",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.access_point_ids.length}
        </span>
      ),
    },
    {
      id: "groups",
      header: "Groups",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.group_ids.length}
        </span>
      ),
    },
    {
      id: "actions",
      header: () => <span className="sr-only">Actions</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">
          <CardActionsMenu card={row.original} />
        </div>
      ),
    },
  ]

  if (cards.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <CreditCard className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No cards yet</h3>
        <p className="text-muted-foreground">Add an RFID card to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={cards.data} />
}

function CardsTab() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <Suspense fallback={<Skeleton className="h-10 w-28" />}>
          <AddCard />
        </Suspense>
      </div>
      <Suspense fallback={<Skeleton className="h-48 w-full" />}>
        <CardsTableContent />
      </Suspense>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// GROUPS TAB
// ═══════════════════════════════════════════════════════════════════════════════

const groupFormSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }).max(255),
  description: z.string().max(255).optional().or(z.literal("")),
})

type GroupFormData = z.infer<typeof groupFormSchema>

// ── Add Group ─────────────────────────────────────────────────────────────────

function AddGroup() {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<GroupFormData>({
    resolver: zodResolver(groupFormSchema),
    mode: "onBlur",
    defaultValues: { name: "", description: "" },
  })

  const mutation = useMutation({
    mutationFn: (data: GroupFormData) =>
      AccessService.createGroup({
        requestBody: { name: data.name, description: data.description || null },
      }),
    onSuccess: () => {
      showSuccessToast("Group created successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-groups"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Add Group
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Group</DialogTitle>
          <DialogDescription>Create a new access group.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input placeholder="Staff" {...field} /></FormControl>
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
                    <FormControl><Input placeholder="Optional note" {...field} /></FormControl>
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

// ── Edit Group ────────────────────────────────────────────────────────────────

function EditGroup({ group, onSuccess }: { group: AccessGroupPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<GroupFormData>({
    resolver: zodResolver(groupFormSchema),
    mode: "onBlur",
    defaultValues: { name: group.name, description: group.description ?? "" },
  })

  const mutation = useMutation({
    mutationFn: (data: GroupFormData) =>
      AccessService.updateGroup({
        groupId: group.id,
        requestBody: { name: data.name, description: data.description || null },
      }),
    onSuccess: () => {
      showSuccessToast("Group updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-groups"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Pencil />
        Edit
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Group</DialogTitle>
          <DialogDescription>Update group details.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
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

// ── Delete Group ──────────────────────────────────────────────────────────────

function DeleteGroup({ group, onSuccess }: { group: AccessGroupPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => AccessService.deleteGroup({ groupId: group.id }),
    onSuccess: () => {
      showSuccessToast("Group deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-groups"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
        className="text-destructive focus:text-destructive"
      >
        <Trash2 />
        Delete
      </DropdownMenuItem>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Group</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete <strong>{group.name}</strong>? This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>Cancel</Button>
          </DialogClose>
          <LoadingButton
            variant="destructive"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Manage Group Access Points ────────────────────────────────────────────────

function ManageGroupPoints({
  group,
  onSuccess,
}: {
  group: AccessGroupPublic
  onSuccess: () => void
}) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const { data: pointsData } = useSuspenseQuery(getPointsQueryOptions())

  const togglePoint = useMutation({
    mutationFn: ({ pointId, add }: { pointId: string; add: boolean }) =>
      add
        ? AccessService.addGroupPoint({ groupId: group.id, pointId })
        : AccessService.removeGroupPoint({ groupId: group.id, pointId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["access-groups"] }),
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Settings2 />
        Manage Access Points
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Access Points — {group.name}</DialogTitle>
          <DialogDescription>Select which locations this group can access.</DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-2 py-4">
          {pointsData.data.length === 0 && (
            <p className="text-sm text-muted-foreground">No locations defined yet.</p>
          )}
          {pointsData.data.map((pt) => {
            const checked = group.access_point_ids.includes(pt.id)
            return (
              <label key={pt.id} className="flex items-center gap-2 cursor-pointer">
                <Checkbox
                  checked={checked}
                  onCheckedChange={(val) =>
                    togglePoint.mutate({ pointId: pt.id, add: !!val })
                  }
                />
                <span className="text-sm">{pt.name}</span>
                {pt.description && (
                  <span className="text-xs text-muted-foreground">— {pt.description}</span>
                )}
              </label>
            )
          })}
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button onClick={() => { onSuccess(); setIsOpen(false) }}>Done</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Group Actions Menu ────────────────────────────────────────────────────────

function GroupActionsMenu({ group }: { group: AccessGroupPublic }) {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditGroup group={group} onSuccess={() => setOpen(false)} />
        <ManageGroupPoints group={group} onSuccess={() => setOpen(false)} />
        <DeleteGroup group={group} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// ── Groups Table ──────────────────────────────────────────────────────────────

function GroupsTableContent() {
  const { data: groups } = useSuspenseQuery(getGroupsQueryOptions())

  const columns: ColumnDef<AccessGroupPublic>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
    },
    {
      accessorKey: "description",
      header: "Description",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.description || "—"}
        </span>
      ),
    },
    {
      id: "access_points",
      header: "Access Points",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.access_point_ids.length}
        </span>
      ),
    },
    {
      id: "actions",
      header: () => <span className="sr-only">Actions</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">
          <GroupActionsMenu group={row.original} />
        </div>
      ),
    },
  ]

  if (groups.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Layers className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No groups yet</h3>
        <p className="text-muted-foreground">Create a group to manage access in bulk</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={groups.data} />
}

function GroupsTab() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <AddGroup />
      </div>
      <Suspense fallback={<Skeleton className="h-48 w-full" />}>
        <GroupsTableContent />
      </Suspense>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOCATIONS (ACCESS POINTS) TAB
// ═══════════════════════════════════════════════════════════════════════════════

const pointFormSchema = z.object({
  name: z.string().min(1, { message: "Name is required" }).max(255),
  description: z.string().max(255).optional().or(z.literal("")),
})

type PointFormData = z.infer<typeof pointFormSchema>

// ── Add Location ──────────────────────────────────────────────────────────────

function AddLocation() {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<PointFormData>({
    resolver: zodResolver(pointFormSchema),
    mode: "onBlur",
    defaultValues: { name: "", description: "" },
  })

  const mutation = useMutation({
    mutationFn: (data: PointFormData) =>
      AccessService.createPoint({
        requestBody: { name: data.name, description: data.description || null },
      }),
    onSuccess: () => {
      showSuccessToast("Location created successfully")
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-points"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="my-4">
          <Plus className="mr-2" />
          Add Location
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Location</DialogTitle>
          <DialogDescription>
            Create a new access point (e.g. a door or gate). The name must match the{" "}
            <code className="text-xs">GATE_NAME</code> configured on the ESP32.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name <span className="text-destructive">*</span></FormLabel>
                    <FormControl><Input placeholder="Brama" {...field} /></FormControl>
                    <FormDescription>
                      Must match the <code className="text-xs">GATE_NAME</code> const in the ESP32 firmware.
                    </FormDescription>
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
                    <FormControl><Input placeholder="Optional note" {...field} /></FormControl>
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

// ── Edit Location ─────────────────────────────────────────────────────────────

function EditLocation({ point, onSuccess }: { point: AccessPointPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<PointFormData>({
    resolver: zodResolver(pointFormSchema),
    mode: "onBlur",
    defaultValues: { name: point.name, description: point.description ?? "" },
  })

  const mutation = useMutation({
    mutationFn: (data: PointFormData) =>
      AccessService.updatePoint({
        pointId: point.id,
        requestBody: { name: data.name, description: data.description || null },
      }),
    onSuccess: () => {
      showSuccessToast("Location updated successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-points"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={() => setIsOpen(true)}>
        <Pencil />
        Edit
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Location</DialogTitle>
          <DialogDescription>Update access point details.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((d) => mutation.mutate(d))}>
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

// ── Delete Location ───────────────────────────────────────────────────────────

function DeleteLocation({ point, onSuccess }: { point: AccessPointPublic; onSuccess: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () => AccessService.deletePoint({ pointId: point.id }),
    onSuccess: () => {
      showSuccessToast("Location deleted successfully")
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["access-points"] }),
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
        className="text-destructive focus:text-destructive"
      >
        <Trash2 />
        Delete
      </DropdownMenuItem>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Location</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete <strong>{point.name}</strong>? This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>Cancel</Button>
          </DialogClose>
          <LoadingButton
            variant="destructive"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            Delete
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Location Actions Menu ─────────────────────────────────────────────────────

function LocationActionsMenu({ point }: { point: AccessPointPublic }) {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditLocation point={point} onSuccess={() => setOpen(false)} />
        <DeleteLocation point={point} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// ── Locations Table ───────────────────────────────────────────────────────────

function LocationsTableContent() {
  const { data: points } = useSuspenseQuery(getPointsQueryOptions())

  const columns: ColumnDef<AccessPointPublic>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
    },
    {
      accessorKey: "description",
      header: "Description",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {row.original.description || "—"}
        </span>
      ),
    },
    {
      id: "actions",
      header: () => <span className="sr-only">Actions</span>,
      cell: ({ row }) => (
        <div className="flex justify-end">
          <LocationActionsMenu point={row.original} />
        </div>
      ),
    },
  ]

  if (points.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <MapPin className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No locations yet</h3>
        <p className="text-muted-foreground">Add a location to define where cards can grant access</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={points.data} />
}

function LocationsTab() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <AddLocation />
      </div>
      <Suspense fallback={<Skeleton className="h-48 w-full" />}>
        <LocationsTableContent />
      </Suspense>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOGS TAB
// ═══════════════════════════════════════════════════════════════════════════════

function getLogsQueryOptions() {
  return {
    queryFn: () => AccessService.listLogs({ skip: 0, limit: 200 }),
    queryKey: ["access-logs"],
    refetchInterval: 15_000,
    refetchOnWindowFocus: true,
  }
}

function LogsTableContent() {
  const { data: logs } = useSuspenseQuery(getLogsQueryOptions())

  const columns: ColumnDef<AccessLogPublic>[] = [
    {
      accessorKey: "timestamp",
      header: "Time",
      cell: ({ row }) => (
        <span className="text-sm tabular-nums text-muted-foreground whitespace-nowrap">
          {new Date(row.original.timestamp).toLocaleString()}
        </span>
      ),
    },
    {
      accessorKey: "label",
      header: "Card",
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span className="font-medium">{row.original.label ?? "—"}</span>
          <span className="font-mono text-xs text-muted-foreground">{row.original.uid}</span>
        </div>
      ),
    },
    {
      accessorKey: "username",
      header: "User",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">{row.original.username ?? "—"}</span>
      ),
    },
    {
      accessorKey: "gate_name",
      header: "Location",
      cell: ({ row }) => <span className="text-sm">{row.original.gate_name}</span>,
    },
    {
      accessorKey: "granted",
      header: "Result",
      cell: ({ row }) =>
        row.original.granted ? (
          <Badge variant="default" className="gap-1">
            <CheckCircle className="h-3 w-3" />
            Granted
          </Badge>
        ) : (
          <Badge variant="destructive" className="gap-1">
            <XCircle className="h-3 w-3" />
            Denied
          </Badge>
        ),
    },
  ]

  if (logs.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <ScrollText className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No logs yet</h3>
        <p className="text-muted-foreground">Access attempts will appear here</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={logs.data} />
}

function LogsTab() {
  return (
    <Suspense fallback={<Skeleton className="h-48 w-full" />}>
      <LogsTableContent />
    </Suspense>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// PAGE
// ═══════════════════════════════════════════════════════════════════════════════

function AccessCards() {
  const { tab } = Route.useSearch()
  const navigate = Route.useNavigate()

  const setTab = (value: string) =>
    navigate({ search: { tab: value as TabValue }, replace: true })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Access Cards</h1>
        <p className="text-muted-foreground">
          Manage RFID cards, groups, access locations and view access logs
        </p>
      </div>
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="cards">Cards</TabsTrigger>
          <TabsTrigger value="groups">Groups</TabsTrigger>
          <TabsTrigger value="locations">Locations</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>
        <TabsContent value="cards" className="mt-4">
          <CardsTab />
        </TabsContent>
        <TabsContent value="groups" className="mt-4">
          <GroupsTab />
        </TabsContent>
        <TabsContent value="locations" className="mt-4">
          <LocationsTab />
        </TabsContent>
        <TabsContent value="logs" className="mt-4">
          <LogsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
