'use client';

import PDF from "../../components/pdf";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

export default function AboutPage() {
  const router = useRouter();

  return (
    <div style={{ position: "relative", height: "100vh" }}>
      {/* Back Button */}
      <button
        onClick={() => router.push("/")}
        style={{
          position: "absolute",
          top: "16px",
          left: "16px",
          zIndex: 10,
          background: "rgba(0,0,0,0.7)",
          border: "none",
          borderRadius: "9999px",
          padding: "10px",
          cursor: "pointer",
        }}
        aria-label="Go back home"
      >
        <ArrowLeft size={20} color="white" />
      </button>

      {/* PDF Viewer */}
      <PDF fileUrl="/about_eva.pdf" />
    </div>
  );
}
