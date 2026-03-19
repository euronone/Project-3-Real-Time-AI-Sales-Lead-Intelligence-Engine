import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { ChevronUp, ChevronDown } from "lucide-react";
import { Skeleton } from "./loading";

interface TableProps {
  children: ReactNode;
  isLoading?: boolean;
  emptyMessage?: string;
  className?: string;
}

interface TableHeadProps {
  children: ReactNode;
  sortable?: boolean;
  sortDirection?: "asc" | "desc" | null;
  onSort?: () => void;
  className?: string;
}

interface TableRowProps {
  children: ReactNode;
  isSelected?: boolean;
  onClick?: () => void;
  className?: string;
}

interface TableCellProps {
  children?: ReactNode;
  className?: string;
  colSpan?: number;
}

export function Table({ children, isLoading, emptyMessage, className }: TableProps) {
  return (
    <div className={cn("overflow-x-auto rounded-lg border border-gray-200", className)}>
      <table className="w-full text-sm">
        {isLoading ? (
          <tbody>
            {Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="border-b border-gray-100">
                {Array.from({ length: 4 }).map((__, j) => (
                  <td key={j} className="px-4 py-3">
                    <Skeleton className="h-4 w-full" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        ) : emptyMessage ? (
          <tbody>
            <tr>
              <td colSpan={100} className="px-4 py-12 text-center text-gray-500">
                {emptyMessage}
              </td>
            </tr>
          </tbody>
        ) : (
          children
        )}
      </table>
    </div>
  );
}

export function TableHeader({ children }: { children: ReactNode }) {
  return (
    <thead className="bg-gray-50 border-b border-gray-200">
      {children}
    </thead>
  );
}

export function TableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-gray-100 bg-white">{children}</tbody>;
}

export function TableRow({ children, isSelected, onClick, className }: TableRowProps) {
  return (
    <tr
      onClick={onClick}
      className={cn(
        "transition-colors",
        onClick && "cursor-pointer hover:bg-gray-50",
        isSelected && "bg-blue-50",
        className
      )}
    >
      {children}
    </tr>
  );
}

export function TableHead({ children, sortable, sortDirection, onSort, className }: TableHeadProps) {
  return (
    <th
      onClick={sortable ? onSort : undefined}
      className={cn(
        "px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap",
        sortable && "cursor-pointer hover:text-gray-700 select-none",
        className
      )}
    >
      <span className="flex items-center gap-1">
        {children}
        {sortable && (
          <span className="flex flex-col">
            <ChevronUp
              size={10}
              className={sortDirection === "asc" ? "text-blue-600" : "text-gray-300"}
            />
            <ChevronDown
              size={10}
              className={sortDirection === "desc" ? "text-blue-600" : "text-gray-300"}
            />
          </span>
        )}
      </span>
    </th>
  );
}

export function TableCell({ children, className, colSpan }: TableCellProps) {
  return (
    <td colSpan={colSpan} className={cn("px-4 py-3 text-gray-700", className)}>
      {children}
    </td>
  );
}
