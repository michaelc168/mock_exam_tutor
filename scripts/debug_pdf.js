const pdf = require('pdf-parse');
console.log('Type of exported module:', typeof pdf);
console.log('Exported module:', pdf);
try {
    const fs = require('fs');
    const path = require('path');
    const files = fs.readdirSync(path.join(__dirname, '../exams/bank')).filter(f => f.endsWith('.pdf'));
    if (files.length > 0) {
        const buffer = fs.readFileSync(path.join(__dirname, '../exams/bank', files[0]));
        console.log('Attempting to call pdf()...');
        pdf(buffer).then(data => {
            console.log('Success!');
            console.log('Text preview:', data.text.substring(0, 50));
        }).catch(err => {
            console.error('Promise error:', err);
        });
    } else {
        console.log('No PDF to test with');
    }
} catch (e) {
    console.error('Sync error:', e);
}
