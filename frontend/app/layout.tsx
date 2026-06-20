import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PatchPilot — Autonomous software maintenance buyer",
  description: "One paid mission. Two independent CROO specialists. One verified patch.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
