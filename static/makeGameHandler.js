function makeNewGame(){

  console.log('makeGame() triggered')
  var name = $('[name=NameMake]').val()
  var gameName = $('[name=GameNameMake]').val()

  var nrOfRounds = $('[name=NrOfRounds]').val()
  var time = $('[name=TimeForEachRound]').val()

  console.log(name)

  if (!/^([ÆØÅæøåA-Za-z1-9]{3,10})$/.test(name)){
    notyf.alert('Name not allowed. Please retry');
    return;
  }

  if (!/^([ÆØÅæøåA-Za-z1-9]{5,20})$/.test(gameName)){
    notyf.alert('Game name not allowed. Please retry');
    return;
  }

  if (parseInt(nrOfRounds)<1){
    notyf.alert('Game name not allowed. Please retry');
    return;
  }

  if (parseInt(nrOfRounds)>= 13){
    notyf.alert('Too many rounds selected. Please retry');
    return;
  }

  if (parseInt(time)<2 || (!parseInt(time))){
    notyf.alert('Not enough time selected. Please retry');
    return;
  }

  if (parseInt(time)> 180){
    notyf.alert('Too much time selected. Please retry');
    return;
  }



}

function joinGame(){
    console.log('joinGame() triggered')
    /////^([ÆØÅæøåA-Za-z1-9]{3,10})$/.test('abc1');
    ///^([ÆØÅæøåA-Za-z1-9]{5,20})$/.test('abc1');

}
