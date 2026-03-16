import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PaginationProps {
  /** Total number of items (used to compute totalPages if not provided) */
  total?: number;
  /** Alias for total */
  totalItems?: number;
  /** Current page (1-indexed) */
  page?: number;
  /** Alias for page */
  currentPage?: number;
  pageSize: number;
  /** Pre-computed total pages (overrides the total / pageSize calculation) */
  totalPages?: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  total,
  totalItems,
  page,
  currentPage,
  pageSize,
  totalPages: totalPagesProp,
  onPageChange,
  className,
}: PaginationProps) {
  const resolvedTotal = totalItems ?? total ?? 0;
  const resolvedPage = currentPage ?? page ?? 1;
  const totalPages =
    totalPagesProp ?? Math.ceil(resolvedTotal / pageSize);

  if (totalPages <= 1) return null;

  const from = (resolvedPage - 1) * pageSize + 1;
  const to = Math.min(resolvedPage * pageSize, resolvedTotal);

  const getPageNumbers = (): (number | "...")[] => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    const pages: (number | "...")[] = [1];
    if (resolvedPage > 3) pages.push("...");
    for (
      let i = Math.max(2, resolvedPage - 1);
      i <= Math.min(totalPages - 1, resolvedPage + 1);
      i++
    ) {
      pages.push(i);
    }
    if (resolvedPage < totalPages - 2) pages.push("...");
    pages.push(totalPages);
    return pages;
  };

  return (
    <div className={cn("flex items-center justify-between gap-4", className)}>
      <p className="text-sm text-gray-500">
        Showing <span className="font-medium">{from}</span>–
        <span className="font-medium">{to}</span> of{" "}
        <span className="font-medium">{resolvedTotal}</span>
      </p>

      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(resolvedPage - 1)}
          disabled={resolvedPage === 1}
          className="p-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          aria-label="Previous page"
        >
          <ChevronLeft size={16} />
        </button>

        {getPageNumbers().map((num, i) =>
          num === "..." ? (
            <span key={`ellipsis-${i}`} className="px-2 text-gray-400 text-sm">
              ...
            </span>
          ) : (
            <button
              key={num}
              onClick={() => onPageChange(num)}
              className={cn(
                "h-8 w-8 rounded-lg text-sm font-medium transition-colors",
                resolvedPage === num
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:bg-gray-100 border border-gray-200"
              )}
              aria-current={resolvedPage === num ? "page" : undefined}
            >
              {num}
            </button>
          )
        )}

        <button
          onClick={() => onPageChange(resolvedPage + 1)}
          disabled={resolvedPage === totalPages}
          className="p-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          aria-label="Next page"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
