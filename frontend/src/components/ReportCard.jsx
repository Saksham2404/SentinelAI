import React from "react";
import ReactMarkdown from "react-markdown";
import { Download, FileText, FileDown } from "lucide-react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

function ReportCard({ report }) {
  const downloadMarkdown = () => {
    try {
      const element = document.createElement("a");
      const file = new Blob([report], { type: "text/markdown" });
      element.href = URL.createObjectURL(file);
      element.download = "sentinelai_incident_report.md";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (err) {
      console.error("Failed to download Markdown:", err);
    }
  };

  const downloadPDF = async () => {
    const reportElement = document.getElementById("ai-report-content");
    if (!reportElement) return;

    try {
      // Temporarily change style of padding for nice PDF capture
      const originalPadding = reportElement.style.padding;
      reportElement.style.padding = "20px";

      const canvas = await html2canvas(reportElement, {
        scale: 2, // high quality
        useCORS: true,
        backgroundColor: "#030712" // match dark theme slate-950
      });

      reportElement.style.padding = originalPadding;

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      
      let position = 0;
      
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
      
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }
      
      pdf.save("sentinelai_incident_report.pdf");
    } catch (err) {
      console.error("Failed to generate PDF:", err);
    }
  };

  return (
    <div className="glass-card p-6 rounded-xl border border-slate-700 bg-slate-900/30 backdrop-blur-md relative">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-6 pb-4 border-b border-slate-800">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FileText size={20} className="text-teal-400" />
          AI Investigation Report
        </h2>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={downloadMarkdown}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
            title="Download report in Markdown format"
          >
            <Download size={14} />
            Markdown
          </button>
          
          <button 
            onClick={downloadPDF}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-teal-600 hover:bg-teal-500 text-white transition shadow-lg shadow-teal-500/10"
            title="Download report in PDF format"
          >
            <FileDown size={14} />
            PDF Report
          </button>
        </div>
      </div>
      
      <div id="ai-report-content" className="prose prose-invert max-w-none">
        <ReactMarkdown
          components={{
            h1: ({ children }) => <h1 className="mb-4 text-2xl font-bold text-white">{children}</h1>,
            h2: ({ children }) => <h2 className="mt-8 border-b border-slate-800 pb-3 text-xl font-bold text-white">{children}</h2>,
            h3: ({ children }) => <h3 className="mt-6 text-lg font-semibold text-white">{children}</h3>,
            p: ({ children }) => <p className="mt-4 leading-7 text-slate-300">{children}</p>,
            ul: ({ children }) => <ul className="mt-4 list-disc space-y-2 pl-6 text-slate-300">{children}</ul>,
            ol: ({ children }) => <ol className="mt-4 list-decimal space-y-2 pl-6 text-slate-300">{children}</ol>,
            li: ({ children }) => <li className="leading-7">{children}</li>,
            strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
            code: ({ children }) => <code className="rounded bg-slate-800 px-1.5 py-0.5 text-sm text-blue-300">{children}</code>,
            hr: () => <hr className="my-6 border-slate-800" />, 
          }}
        >
          {report}
        </ReactMarkdown>
      </div>
    </div>
  );
}

export default ReportCard;
