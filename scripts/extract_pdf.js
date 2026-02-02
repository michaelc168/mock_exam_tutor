const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');

const BANK_DIR = path.join(__dirname, '../exams/bank');
const OUTPUT_DIR = path.join(BANK_DIR, 'extracted');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function extractTextFromPdf(filePath) {
    const dataBuffer = fs.readFileSync(filePath);
    try {
        const data = await pdf(dataBuffer);
        return data.text;
    } catch (error) {
        console.error(`Error parsing ${filePath}:`, error.message);
        return null;
    }
}

async function main() {
    console.log(`Scanning directory: ${BANK_DIR}`);

    // Read all files in the bank directory
    const files = fs.readdirSync(BANK_DIR);
    const pdfFiles = files.filter(file => file.toLowerCase().endsWith('.pdf'));

    if (pdfFiles.length === 0) {
        console.log('No PDF files found.');
        return;
    }

    console.log(`Found ${pdfFiles.length} PDF files. Processing...`);

    let successCount = 0;

    for (const file of pdfFiles) {
        const sourcePath = path.join(BANK_DIR, file);
        const outputFilename = file.replace(/\.pdf$/i, '.txt');
        const outputPath = path.join(OUTPUT_DIR, outputFilename);

        // Skip if already extracted (optional, but good for retries. 
        // Here we overwrite to ensure fresh extraction based on user request)

        console.log(`Extracting: ${file}...`);
        const text = await extractTextFromPdf(sourcePath);

        if (text) {
            // Basic cleanup: remove excessive newlines
            const cleanedText = text.replace(/\n\s*\n/g, '\n');

            fs.writeFileSync(outputPath, cleanedText, 'utf8');
            console.log(`  -> Saved to: exams/bank/extracted/${outputFilename}`);
            successCount++;
        } else {
            console.log(`  -> Failed to extract text from ${file} (might be an image-only PDF or corrupted).`);
        }
    }

    console.log('\n------------------------------------------------');
    console.log(`Extraction Complete. Successfully processed ${successCount}/${pdfFiles.length} files.`);
    console.log(`Extracted text files are located in: ${OUTPUT_DIR}`);
}

main();
