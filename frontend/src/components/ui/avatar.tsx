import { cn, getInitials } from "@/lib/utils";

interface AvatarProps {
  name: string;
  src?: string;
  size?: "sm" | "md" | "lg" | "xl";
  status?: "online" | "offline" | "busy";
  className?: string;
}

const sizeClasses = {
  sm: "h-7 w-7 text-xs",
  md: "h-9 w-9 text-sm",
  lg: "h-11 w-11 text-base",
  xl: "h-14 w-14 text-lg",
};

const statusClasses = {
  online: "bg-green-400",
  offline: "bg-gray-400",
  busy: "bg-red-400",
};

const statusSizes = {
  sm: "h-1.5 w-1.5 border",
  md: "h-2.5 w-2.5 border-2",
  lg: "h-3 w-3 border-2",
  xl: "h-3.5 w-3.5 border-2",
};

export function Avatar({ name, src, size = "md", status, className }: AvatarProps) {
  return (
    <div className={cn("relative inline-flex flex-shrink-0", className)}>
      {src ? (
        <img
          src={src}
          alt={name}
          className={cn("rounded-full object-cover", sizeClasses[size])}
        />
      ) : (
        <div
          className={cn(
            "rounded-full bg-blue-600 text-white font-semibold flex items-center justify-center select-none",
            sizeClasses[size]
          )}
          title={name}
          aria-label={name}
        >
          {getInitials(name)}
        </div>
      )}
      {status && (
        <span
          className={cn(
            "absolute bottom-0 right-0 rounded-full border-white",
            statusClasses[status],
            statusSizes[size]
          )}
          aria-label={`Status: ${status}`}
        />
      )}
    </div>
  );
}
