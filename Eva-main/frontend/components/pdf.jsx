'use client';

export default function PDF({ fileUrl }) {
  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <iframe
        src={fileUrl}
        style={{
          width: "100%",
          height: "100%",
          border: "none",
        }}
      />
    </div>
  );
}
