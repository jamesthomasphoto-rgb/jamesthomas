// usage: node topdf.js in.html out.pdf
const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+require('path').resolve(process.argv[2]));await p.evaluate(()=>document.fonts.ready);await p.emulateMedia({media:'print'});await p.pdf({path:process.argv[3],preferCSSPageSize:true,printBackground:true});await b.close();})();
