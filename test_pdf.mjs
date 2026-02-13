import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist/legacy/build/pdf.mjs';

// Use absolute path for worker in Node environment to avoid relative path resolution issues
import { resolve } from 'path';
GlobalWorkerOptions.workerSrc = resolve('./frontend/public/pdf.worker.min.mjs');

const loadingTask = getDocument('backend/static/uploads/test.pdf');

loadingTask.promise.then(function(pdf) {
  console.log('PDF loaded');
  console.log('Number of pages: ' + pdf.numPages);
  
  // Fetch the first page
  var pageNumber = 1;
  pdf.getPage(pageNumber).then(function(page) {
    console.log('Page loaded');
    
    var scale = 1.5;
    var viewport = page.getViewport({scale: scale});
    console.log('Viewport width: ' + viewport.width);
    console.log('Viewport height: ' + viewport.height);
    
    console.log('Test PASSED');
  });
}, function (reason) {
  // PDF loading error
  console.error(reason);
  console.log('Test FAILED');
});
