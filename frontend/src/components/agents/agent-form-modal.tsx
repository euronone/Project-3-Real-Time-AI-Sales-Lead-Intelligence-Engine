"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import type { AgentPerformance } from "@/types/models";
import type { CreateAgentPayload, UpdateAgentPayload } from "@/lib/agents-api";

// ── Zod schema ───────────────────────────────────────────────────────────────

const agentSchema = z.object({
  full_name: z
    .string()
    .min(2, "Full name must be at least 2 characters")
    .max(255, "Full name is too long"),
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  role: z.enum(["tenant_admin", "manager", "agent"], {
    required_error: "Please select a role",
  }),
  phone: z.string().optional(),
});

type AgentFormValues = z.infer<typeof agentSchema>;

// ── Constants ────────────────────────────────────────────────────────────────

const ROLE_OPTIONS = [
  { value: "agent", label: "Agent" },
  { value: "manager", label: "Manager" },
  { value: "tenant_admin", label: "Admin" },
];

// ── Props ────────────────────────────────────────────────────────────────────

interface AgentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  /** If provided, the modal is in Edit mode; otherwise Create mode */
  agent?: AgentPerformance | null;
  onSubmit: (payload: CreateAgentPayload | UpdateAgentPayload) => void;
  isSubmitting?: boolean;
}

// ── Component ────────────────────────────────────────────────────────────────

export function AgentFormModal({
  isOpen,
  onClose,
  agent,
  onSubmit,
  isSubmitting = false,
}: AgentFormModalProps) {
  const isEditMode = !!agent;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AgentFormValues>({
    resolver: zodResolver(agentSchema),
    defaultValues: {
      full_name: "",
      email: "",
      role: "agent",
      phone: "",
    },
  });

  // Pre-fill form when switching to edit mode or when the target agent changes
  useEffect(() => {
    if (isOpen) {
      reset({
        full_name: agent?.full_name ?? "",
        email: agent?.email ?? "",
        role:
          (agent?.role as AgentFormValues["role"]) ??
          "agent",
        phone: "",
      });
    }
  }, [isOpen, agent, reset]);

  function handleClose() {
    reset();
    onClose();
  }

  function handleFormSubmit(values: AgentFormValues) {
    const payload: CreateAgentPayload | UpdateAgentPayload = {
      full_name: values.full_name,
      email: values.email,
      role: values.role,
      ...(values.phone ? { phone: values.phone } : {}),
    };
    onSubmit(payload);
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={isEditMode ? "Edit Agent" : "Create Agent"}
      size="lg"
      footer={
        <>
          <Button variant="outline" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            form="agent-form"
            type="submit"
            isLoading={isSubmitting}
            disabled={isSubmitting}
          >
            {isEditMode ? "Save Changes" : "Create Agent"}
          </Button>
        </>
      }
    >
      <form
        id="agent-form"
        onSubmit={handleSubmit(handleFormSubmit)}
        className="flex flex-col gap-5"
        noValidate
      >
        {/* Full Name */}
        <Input
          id="agent-full-name"
          label="Full Name"
          placeholder="Jane Smith"
          required
          error={errors.full_name?.message}
          {...register("full_name")}
        />

        {/* Email */}
        <Input
          id="agent-email"
          type="email"
          label="Email Address"
          placeholder="jane@company.com"
          required
          disabled={isEditMode} // email is immutable after creation
          error={errors.email?.message}
          helperText={isEditMode ? "Email cannot be changed after creation." : undefined}
          {...register("email")}
        />

        {/* Role */}
        <Select
          id="agent-role"
          label="Role"
          options={ROLE_OPTIONS}
          required
          error={errors.role?.message}
          {...register("role")}
        />

        {/* Phone (optional) */}
        <Input
          id="agent-phone"
          type="tel"
          label="Phone Number"
          placeholder="+1 (555) 000-0000"
          error={errors.phone?.message}
          {...register("phone")}
        />
      </form>
    </Modal>
  );
}
