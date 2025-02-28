/* Copyright 2024 Marimo. All rights reserved. */
import React from "react";
import { sendRun } from "@/core/network/requests";
import { AddDatabaseForm } from "./add-database-form";
import type { DatabaseConnection } from "./schemas";
import { generateDatabaseCode } from "./as-code";
import { toast } from "@/components/ui/use-toast";

interface Props {
  cellId: string;
  onComplete: () => void;
}

export const DatabaseConnectionModalContent: React.FC<Props> = ({
  cellId,
  onComplete,
}) => {
  const [library, setLibrary] = React.useState<"sqlalchemy" | "sqlmodel">(
    "sqlalchemy"
  );

  const handleSubmit = async (data: DatabaseConnection) => {
    try {
      const code = generateDatabaseCode(data, library);
      
      if (cellId) {
        await sendRun({
          cellIds: [cellId],
          codes: [code],
        });
        
        onComplete();
        toast({
          title: "Connection code added",
          description: `${data.type.charAt(0).toUpperCase() + data.type.slice(1)} connection code added to cell`,
        });
      }
    } catch {
      toast({
        title: "Error adding connection",
        description: "Failed to add connection code",
        variant: "danger",
      });
    }
  };

  return (
    <div>
      <div className="p-4 flex gap-4 items-center">
        <label htmlFor="library-select" className="whitespace-nowrap">Preferred library:</label>
        <select
          id="library-select"
          value={library}
          onChange={(e) => setLibrary(e.target.value as "sqlalchemy" | "sqlmodel")}
          className="border rounded px-2 py-1"
        >
          <option value="sqlalchemy">SQLAlchemy</option>
          <option value="sqlmodel">SQLModel</option>
        </select>
      </div>
      
      <AddDatabaseForm onSubmit={handleSubmit} />
    </div>
  );
}; 