import { twMerge } from "tailwind-merge"

type ClassNameValue = string | false | null | undefined

export function cn(...inputs: ClassNameValue[]) {
  return twMerge(inputs.filter(Boolean).join(" "))
}
