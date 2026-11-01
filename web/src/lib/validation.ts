import * as z from "zod";

/** One password rule for signup, reset and change, so the three can never drift apart. */
export const passwordRule = z
  .string()
  .min(8, "At least 8 characters")
  .max(72, "At most 72 characters")
  .regex(/[A-Za-z]/, "Include a letter")
  .regex(/\d/, "Include a number");
