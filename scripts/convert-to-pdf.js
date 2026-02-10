const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// 使用 MathJax 將 LaTeX 轉換為 SVG
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');

// 初始化 MathJax
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

const tex = new TeX({ packages: AllPackages });
const svg = new SVG({ fontCache: 'none' });
const mjaxDoc = mathjax.document('', { InputJax: tex, OutputJax: svg });

function texToSvg(texStr, inline = true) {
    const node = mjaxDoc.convert(texStr, { display: !inline });
    return adaptor.outerHTML(node);
}

// 將 Markdown 中的 LaTeX 公式轉換為 SVG
function convertLatexToSvg(markdown) {
    // 處理行內公式 $...$
    let result = markdown.replace(/\$([^$\n]+)\$/g, (match, tex) => {
        try {
            const svgHtml = texToSvg(tex, true);
            return svgHtml;
        } catch (e) {
            console.error(`公式轉換失敗: ${tex}`, e.message);
            return match;
        }
    });
    
    // 處理區塊公式 $$...$$
    result = result.replace(/\$\$([^$]+)\$\$/g, (match, tex) => {
        try {
            const svgHtml = texToSvg(tex, false);
            return `<div style="text-align: center; margin: 1em 0;">${svgHtml}</div>`;
        } catch (e) {
            console.error(`公式轉換失敗: ${tex}`, e.message);
            return match;
        }
    });
    
    return result;
}

// 簡單的 Markdown 轉 HTML（不使用 markdown-it-katex）
const markdownIt = require('markdown-it');
const md = markdownIt({ html: true, linkify: false, typographer: false });

async function convertToPdf(inputFile) {
    try {
        console.log('正在讀取 Markdown 檔案...');
        let markdown = fs.readFileSync(inputFile, 'utf-8');

        console.log('正在將 LaTeX 公式轉換為 SVG...');
        markdown = convertLatexToSvg(markdown);

        console.log('正在轉換 Markdown 為 HTML...');
        let html = md.render(markdown);

        // 處理圖片路徑 - 將相對路徑轉換為 Base64 嵌入
        const inputDir = path.dirname(path.resolve(inputFile));
        const imagesDir = path.resolve(inputDir, '..', 'images');
        
        html = html.replace(
            /src="\.\.\/images\/([^"]+)"/g,
            (match, filename) => {
                const imagePath = path.join(imagesDir, filename);
                
                // 檢查圖片是否存在
                if (!fs.existsSync(imagePath)) {
                    console.log(`  ✗ 圖片不存在：${filename}`);
                    return match;
                }
                
                // 讀取圖片並轉換為 Base64
                const imageBuffer = fs.readFileSync(imagePath);
                const base64Image = imageBuffer.toString('base64');
                const ext = path.extname(filename).toLowerCase();
                const mimeType = ext === '.png' ? 'image/png' : 
                                ext === '.jpg' || ext === '.jpeg' ? 'image/jpeg' : 
                                ext === '.svg' ? 'image/svg+xml' : 'image/png';
                
                console.log(`  ✓ 圖片：${filename} (${(imageBuffer.length / 1024).toFixed(1)} KB)`);
                return `src="data:${mimeType};base64,${base64Image}"`;
            }
        );

        // 讀取自訂 CSS 樣式
        const cssPath = path.join(__dirname, '..', 'pdf-style.css');
        const css = fs.readFileSync(cssPath, 'utf-8');

        // 組合完整 HTML
        const fullHtml = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
${css}

/* SVG 數學公式樣式 */
mjx-container {
    display: inline-block;
    vertical-align: middle;
}
mjx-container[display="true"] {
    display: block;
    text-align: center;
    margin: 1em 0;
}
mjx-container svg {
    overflow: visible;
}
    </style>
</head>
<body>
${html}
</body>
</html>
`;

        // 輸出檔案路徑
        const outputFile = inputFile.replace('.md', '.pdf');

        console.log(`正在生成 PDF：${outputFile}`);

        // 啟動 Puppeteer
        const browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // 載入 HTML 內容
        await page.setContent(fullHtml, { 
            waitUntil: ['load', 'domcontentloaded', 'networkidle0']
        });

        // 生成 PDF
        await page.pdf({
            path: outputFile,
            format: 'A4',
            margin: {
                top: '20mm',
                right: '15mm',
                bottom: '20mm',
                left: '15mm'
            },
            printBackground: true,
            displayHeaderFooter: true,
            headerTemplate: '<div></div>',
            footerTemplate: `
                <div style="font-size: 10px; text-align: center; width: 100%; padding: 5px;">
                    <span class="pageNumber"></span> / <span class="totalPages"></span>
                </div>
            `
        });

        await browser.close();

        console.log('✓ PDF 生成成功！');
        return outputFile;
    } catch (error) {
        console.error('錯誤：', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// 從命令列參數取得輸入檔案
const inputFile = process.argv[2];

if (!inputFile) {
    console.error('使用方式: node convert-to-pdf.js <markdown檔案路徑>');
    process.exit(1);
}

if (!fs.existsSync(inputFile)) {
    console.error(`檔案不存在: ${inputFile}`);
    process.exit(1);
}

convertToPdf(inputFile);
