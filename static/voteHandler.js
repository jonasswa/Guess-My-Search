var favoriteAutocomplete;


function submitFavorite(searchStringID, autoCompleteID, nrAutocompletes){
  var nrAutocompletes = parseInt(nrAutocompletes) -1;
  favoriteAutocomplete = String(searchStringID) + "_" + String(autoCompleteID);
  var favBox = document.getElementById("checkBox_"+searchStringID+"_"+autoCompleteID);

  if (favBox.checked == false){
    favBox.checked = true;
    return;
  }

  for (var i = 0; i < nrAutocompletes; i++){
    if (i == parseInt(autoCompleteID)){continue;}
    document.getElementById("checkBox_"+searchStringID+"_"+String(i)).checked = false;
  }


}
