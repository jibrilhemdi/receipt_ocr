"use client";

import React, { useEffect, useState } from "react";
import type { Receipt } from "../types/receipt";

export default function HomePage() {
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadReceipts();
  }, []);

  async function loadReceipts() {
    try {
      const data = await fetchReceipts();
      setReceipts(data);
    } catch {
      setError("Failed to load receipts.");
    }
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const newReceipt = await uploadReceipt(file);
      setReceipts([newReceipt, ...receipts]);
      setSelectedReceipt(newReceipt);
      setFile(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <main className="min-h-screen bg-white text-gray-900 p-8">
      <div className="mx-auto max-w-7xl grid grid-cols-1 md:grid-cols-[280px_1fr] gap-10">

        {/* SIDEBAR */}
        <aside className="space-y-8">

          {/* Upload Card */}
          <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Upload Receipt</h2>

            <form onSubmit={handleUpload} className="space-y-4">
              {/* Drag & Drop Zone */}
              <label
                className="
                  flex flex-col items-center justify-center 
                  px-4 py-10 text-center 
                  border-2 border-dashed border-gray-300 
                  rounded-xl cursor-pointer 
                  bg-gray-50 hover:bg-gray-100 transition
                "
              >
                <span className="text-sm text-gray-600">
                  {file ? `Selected: ${file.name}` : "Drag & drop or click to choose a file"}
                </span>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
              </label>

              {/* Upload button */}
              <button
                type="submit"
                disabled={!file || uploading}
                className={`w-full py-2 rounded-lg text-white font-medium 
                  ${!file || uploading ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"}
                `}
              >
                {uploading ? "Processing…" : "Upload"}
              </button>

              {error && <p className="text-sm text-red-600">{error}</p>}
            </form>
          </div>

          {/* Receipts List */}
          <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-200 h-[460px] flex flex-col">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold">Receipts</h3>
              <button
                onClick={loadReceipts}
                className="text-xs px-2 py-1 border rounded-lg bg-gray-50 hover:bg-gray-100"
              >
                Refresh
              </button>
            </div>

            <div className="overflow-y-auto space-y-2">
              {receipts.map((r) => (
                <div
                  key={r.id}
                  onClick={() => setSelectedReceipt(r)}
                  className={`p-3 rounded-lg border text-sm cursor-pointer
                    ${
                      selectedReceipt?.id === r.id
                        ? "bg-blue-50 border-blue-400"
                        : "bg-gray-50 hover:bg-gray-100 border-gray-300"
                    }
                  `}
                >
                  <p className="font-medium">{r.merchant || "Unknown"}</p>
                  <p className="text-xs text-gray-500">
                    {r.purchase_date
                      ? new Date(r.purchase_date).toLocaleString()
                      : "No date"}
                  </p>
                </div>
              ))}
            </div>
          </div>

        </aside>

        {/* MAIN CONTENT */}
        <section className="p-8 rounded-xl shadow-sm border border-gray-200 bg-white">
          {selectedReceipt ? (
            <ReceiptDetails
              receipt={selectedReceipt}
              onDelete={async (id) => {
                try {
                  await deleteReceipt(id);
                  setReceipts((prev) => prev.filter(r => r.id !== id));
                  setSelectedReceipt(null);
                } catch (err) {
                  alert("Failed to delete receipt");
                }
              }}
            />
          ) : (
            <p className="text-gray-500 text-center text-sm mt-20">
              Select a receipt on the left or upload a new one.
            </p>
          )}
        </section>
      </div>
    </main>
  );
}

function ReceiptDetails({
  receipt,
  onDelete,
}: {
  receipt: Receipt;
  onDelete: (id: number) => void;
}) {

  return (
    <div className="space-y-10">

      {/* Delete Button */}
      <div className="flex justify-end">
        <button
          className="px-3 py-1 text-sm rounded-lg bg-red-500 text-white hover:bg-red-600"
          onClick={() => {
            if (!confirm("Delete this receipt?")) return;
            onDelete(receipt.id);
          }}
        >
          Delete
        </button>
      </div>

      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold mb-2">
          {receipt.merchant || "Untitled Receipt"}
        </h1>
        <p className="text-gray-600">
          Date:{" "}
          {receipt.purchase_date
            ? new Date(receipt.purchase_date).toLocaleString()
            : "Unknown"}
        </p>
        <p className="text-gray-800 font-medium mt-1">
          Total: {receipt.total ? `${receipt.total} ${receipt.currency}` : "N/A"}
        </p>
      </div>

      {/* Items */}
      <div>
        <h2 className="text-xl font-semibold mb-3">Items</h2>

        {receipt.items.length === 0 ? (
          <p className="text-gray-500 text-sm">No items detected.</p>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="[&>th]:text-left border-b border-gray-300">
                <th className="py-2">Item</th>
                <th className="py-2 text-right">Qty</th>
                <th className="py-2 text-right">Unit</th>
                <th className="py-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {receipt.items.map((item) => (
                <tr key={item.id} className="border-b border-gray-200">
                  <td className="py-2">{item.name}</td>
                  <td className="py-2 text-right">{item.quantity}</td>
                  <td className="py-2 text-right">{item.unit_price ?? "-"}</td>
                  <td className="py-2 text-right">{item.line_total ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Raw OCR Text */}
      <div>
        <h2 className="text-xl font-semibold mb-2">Raw OCR Text</h2>
        <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs whitespace-pre-wrap max-h-[300px] overflow-y-auto">
{receipt.raw_text}
        </pre>
      </div>

    </div>
  );
}