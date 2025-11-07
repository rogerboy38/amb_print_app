cat > process_pdfs.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 PDF Processing Pipeline"
echo "=========================="
echo ""

# Process COA TRUROOTS
echo "📄 Processing COA TRUROOTS.pdf..."
python main.py --extract "pdf_files/COA TRUROOTS.pdf" > logs/coa_truroots.log
echo "✅ COA TRUROOTS processed"

# Process COA-25-0004
echo "📄 Processing COA-25-0004.pdf..."
python main.py --extract "pdf_files/COA-25-0004.pdf" > logs/coa_25_0004.log
echo "✅ COA-25-0004 processed"

echo ""
echo "✅ All PDFs processed successfully!"
echo "📊 Logs available in logs/ directory"

EOF

chmod +x process_pdfs.sh
