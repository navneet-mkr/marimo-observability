/* Copyright 2024 Marimo. All rights reserved. */
import React from "react";
import { Dialog } from "@/components/ui/dialog";
import { ZodForm } from "@/components/forms/form";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { ObservabilityConnectionSchema } from "./schemas";
import { generateObservabilityCode } from "./as-code";
import { sendRun } from "@/core/network/requests";
import { toast } from "@/components/ui/use-toast";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { FormItem, FormControl, FormLabel } from "@/components/ui/form";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  cellId: string;
}

export const ObservabilityConnectionModal: React.FC<Props> = ({
  isOpen,
  onClose,
  cellId,
}) => {
  const [activeTab, setActiveTab] = React.useState<"prometheus" | "loki" | "grafana">("prometheus");

  const form = useForm({
    resolver: zodResolver(ObservabilityConnectionSchema),
    defaultValues: { type: activeTab },
  });

  React.useEffect(() => {
    form.setValue("type", activeTab);
  }, [activeTab, form]);

  const handleConnectionSubmit = async (data: unknown) => {
    try {
      const connection = ObservabilityConnectionSchema.parse(data);
      const code = generateObservabilityCode(connection);
      
      if (cellId) {
        await sendRun({ cellIds: [cellId], codes: [code] });
        
        onClose();
        toast({
          title: "Connection code added",
          description: `${connection.type.charAt(0).toUpperCase() + connection.type.slice(1)} connection code added to cell`,
        });
      }
    } catch {
      // Log error silently
      toast({
        title: "Error adding connection",
        description: "Failed to add connection code",
        variant: "danger",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="bg-modal border border-border rounded-lg shadow-lg w-[700px] max-w-[90vw] max-h-[90vh] overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-xl font-semibold">Add Observability Connection</h2>
            <Button
              size="icon"
              variant="ghost"
              onClick={onClose}
              aria-label="Close"
            >
              <X size={18} />
            </Button>
          </div>
          
          <div className="border-b border-border">
            <div className="flex">
              <Button
                variant={activeTab === "prometheus" ? "default" : "ghost"}
                onClick={() => setActiveTab("prometheus")}
                className="rounded-none"
              >
                Prometheus
              </Button>
              <Button
                variant={activeTab === "loki" ? "default" : "ghost"}
                onClick={() => setActiveTab("loki")}
                className="rounded-none"
              >
                Loki
              </Button>
              <Button
                variant={activeTab === "grafana" ? "default" : "ghost"}
                onClick={() => setActiveTab("grafana")}
                className="rounded-none"
              >
                Grafana
              </Button>
            </div>
          </div>
          
          <div className="overflow-y-auto flex-1 p-6">
            <form onSubmit={form.handleSubmit(handleConnectionSubmit)}>
              <ZodForm schema={ObservabilityConnectionSchema} form={form} renderers={undefined} />
              <div className="mt-6 flex justify-end">
                <Button type="submit">Add</Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Dialog>
  );
}; 