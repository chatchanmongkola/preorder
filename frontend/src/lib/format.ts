const THAI_MONTHS = [
  "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
  "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.",
];

export function formatThaiDate(isoString: string): string {
  const d = new Date(isoString);
  const beYear = d.getFullYear() + 543;
  return `${String(d.getDate()).padStart(2, "0")}-${THAI_MONTHS[d.getMonth()]}-${beYear}`;
}

export function formatThaiDatetime(isoString: string): string {
  const d = new Date(isoString);
  const beYear = d.getFullYear() + 543;
  return `${String(d.getDate()).padStart(2, "0")}-${THAI_MONTHS[d.getMonth()]}-${beYear} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
