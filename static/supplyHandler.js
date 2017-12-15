function collectSupply(nrOfEntries){
  console.log('Submitting supplasdy');

  var nrOfEntries = parseInt(nrOfEntries);
  var entries = {};
  console.log('Got these values:');

  for (var i = 0; i < nrOfEntries; i++){
    entries[String(i)] = $( "#autoComplete_"+String(i) ).val();
    console.log(entries[String(i)]);
  }

}
