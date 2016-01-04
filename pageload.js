// Page load time with phantomjs (runs page once)
// phantomjs pageload.js ADDRESS RUN_NUM LOG_FILE
var fs = require('fs')
var system = require('system');
var args = system.args;
var counter = args[2];

// number of runs
//var max = args[2];

// setup file to save data
var filepath = args.length >= 4 ? args[3] : 'pageload-log-' +
  encodeURIComponent((new Date()).toTimeString()) + '.csv'; // default name is timestamp
if (!fs.isFile(filepath)) {
  fs.touch(filepath);
  fs.write(filepath, 'address' + ',' + 'trial' + ',' + 'time in ms' + '\n', 'a');
}


var webpage = require('webpage');
var page = webpage.create();
page.settings.clearMemoryCaches = true;

/*function loadPage(address, counter, max, runningLoadTotal, callback) {
  var start = Date.now();
  page.onLoadFinished = function (status) {
    console.log(counter + 1 + ' of ' + max);
    if( status == 'fail' ) {
      // fail
      console.log('Fail, try again');
      start = Date.now();
      console.log(address + '?nonexistant=' + (new Date().getTime()));
      page.open(address + '?nonexistant=' + (new Date().getTime()));
    }
    var time = Date.now() - start;
    console.log('' + time);
    fs.write(filepath,
      encodeURIComponent(address) + ',' + counter + ',' + time + '\n',
      'a'
    );
    runningLoadTotal += time;
    counter++;
    if(counter < max) {
      start = Date.now();
      console.log(address + '?nonexistant=' + (new Date().getTime()));
      page.open(address + '?nonexistant=' + (new Date().getTime()));
    } else {
      callback(runningLoadTotal);
    }
  };

  console.log(address + '?nonexistant=' + (new Date().getTime()));
  page.open(address + '?nonexistant=' + (new Date().getTime()));
}*/

//var count = 0;
var address = args[1];//"http://golf620-linux.local:8080/";
console.log('Testing page load time of ' + address + '...');
phantom.setProxy('localhost', 82);

var start = Date.now();
page.open(address, function(status) {
  if(status === 'fail') {
    console.log('error code');
    phantom.exit(1);
  }

  var time = Date.now() - start;
  console.log(time);
  fs.write(filepath,
    encodeURIComponent(address) + ',' + counter + ',' + time + '\n',
    'a'
  );
  phantom.exit();
  /*loadPage(address, count, max, 0, function (runningLoadTotal) {
    //var avg = runningLoadTotal / max;
    console.log('Average: ' + avg);
    fs.write(filepath,
      encodeURIComponent(address) + ',' + counter + ',' + avg + '\n',
      'a'
    );
    phantom.exit();
  });*/
});
