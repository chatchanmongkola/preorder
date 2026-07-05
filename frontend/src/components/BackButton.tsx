import { useNavigate } from "react-router-dom";

interface BackButtonProps {
  to?: string;
}

export default function BackButton({ to }: BackButtonProps) {
  const navigate = useNavigate();
  return (
    <button
      onClick={() => (to ? navigate(to) : navigate(-1))}
      className="flex items-center gap-1 text-sm text-neutral-500 hover:text-neutral-800"
      aria-label="กลับ"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 12H5" />
        <polyline points="12 19 5 12 12 5" />
      </svg>
    </button>
  );
}
