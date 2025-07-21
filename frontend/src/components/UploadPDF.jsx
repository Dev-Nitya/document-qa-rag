export default function UploadPDF() {
  const [file, setFile] = useState(null);
  
  const handleUpload = async () => {
    if (!file) return alert("Choose a PDF first");
    const formData = new FormData();
    formData.append("file", file);
    await fetch("/upload-pdf", { method: "POST", body: formData });
    alert("Uploaded successfully");
  };

  return (
    <div className="mb-4">
      <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload} className="ml-2 px-4 py-2 bg-blue-500 text-white">
        Upload PDF
      </button>
    </div>
  );
}
