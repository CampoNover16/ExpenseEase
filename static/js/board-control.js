function changeBoardName(currentName){
  var parentPlacement = document.querySelector('.board-name');
  var inputHtml = '<input type="text" class="form-control newBoardName" value="'+currentName+'" style="width: 235px;">';
  var saveButton = '<button onclick="saveBoardName()" class="btn btn-primary saveNewBoardName">Save</button>';
  
  document.querySelector('.changeBoardName').style.display='none';
  parentPlacement.querySelector('strong').style.display='none';
  parentPlacement.insertAdjacentHTML('afterEnd',saveButton);
  parentPlacement.insertAdjacentHTML('afterEnd',inputHtml);
}

function saveBoardName(){
  var parentPlacement = document.querySelector('.board-name');
  var newNameHook = document.querySelector('.newBoardName');
  var data = {newName: newNameHook.value}
  document.querySelector('.changeBoardName').style.display='initial';
  parentPlacement.querySelector('strong').style.display='initial';

  newNameHook.remove();
  document.querySelector('.saveNewBoardName').remove();

  if(newNameHook.value !== ''){
    fetch("/saveUserBoardName", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
      cache: "no-cache"
    }).then(() => {
      showAlertInfo("Your board name changed succesfully!",'success','userSettings');
      document.querySelector('.userBoardName').innerHTML = data['newName'];
    });
  }else{
    showAlertInfo("Something went wrong! Try again.",'danger','userSettings');
  }
}

loadBtn.addEventListener("click", function () {
  loadAllData();
})

modal.addEventListener('shown.bs.modal', function () {
  var isNameValid,isPriceValid,isCategoryValid,isDateValid,isFormValid = false;
  document.getElementById('expense-date').valueAsDate = new Date();
  const nameInput = document.getElementById("expense-name");
  const priceInput = document.getElementById("expense-price");
  const btn = document.getElementById("sub-btn");
  btn.disabled = true;

  nameInput.addEventListener( "blur" , function() {
    if (nameInput.value != ''){
      isNameValid = true;
      if(isNameValid && isPriceValid ){
      btn.disabled = false;
      }

    }
   });
   priceInput.addEventListener( "blur" , function() {
    if (priceInput.value != ''){
      isPriceValid = true;
      if(isNameValid && isPriceValid ){
      btn.disabled = false;
      }

    }
   });
})

function loadAllData(){
  console.log("DUPA");
  fetch("/getAllExpenses", {
    method: "GET",
    headers: {"Content-Type": "application/json"},
  }).then(() => {
    //TO DO
    //message
    // window.location.reload();
  });
}

function joinToBoard(){
  var inv_code = document.getElementsByClassName('inv-code')[0].value
  var join_code = document.getElementsByClassName('join-code')[0].value;
  if(inv_code !== join_code){
    let myModalEl = document.getElementById('joinWithCodeModal');
    let modal = bootstrap.Modal.getInstance(myModalEl);
    modal.hide();
    joinUserBoard(join_code);
  }else{
    showAlertInfo('You cannot join to your own board!','danger','joinWithCodeModal');
  }
}

function copyInviteContent(){
  var inv_code = document.getElementsByClassName('inv-code')[0].value;
  navigator.clipboard.writeText(inv_code);
  showAlertInfo('Code was successfully copied!','success','invitationCodeModal');
}

function addExpenseFormHandler(){
  var name = document.getElementById("expense-name").value;
  var price = document.getElementById("expense-price").value;
  var category = document.getElementById("expense-category").value;
  var date = document.getElementById("expense-date").value;
  
  var addExpenseData = {
    name,
    price,
    category,
    date,
  }

  fetch("/addExpense", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(addExpenseData),
    cache: "no-cache"
  }).then(() => {
    showAlertInfo("Your expense added successfully!",'success',null);
  });

  console.log(addExpenseData);
}

addExpenseForm.addEventListener("submit", function(e){
  e.preventDefault();
  addExpenseFormHandler();
  addExpenseForm.reset();
})

var optionsColumns = {
    chart: {
        type: 'bar'
    },
    series: [{
        name: 'sales',
        data: [30,40,45,50,49,60,70,91,125]
    }],
    xaxis: {
        categories: [1991,1992,1993,1994,1995,1996,1997, 1998,1999]
    },
    title: {
      text: 'Example title',
      offsetX: 0,
      style: {
        fontSize: '24px',
        color:'#FFFFFF',
      }
    },
}

var optionsDonut = {
      series: [44, 55, 41, 17, 15],
      chart: {
        type: 'donut',
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200
          },
          legend: {
            position: 'bottom'
          }
        }
      }],
      title: {
        text: 'Example title',
        offsetX: 0,
        style: {
          fontSize: '24px',
          color:'#FFFFFF',
        }
      },
    };

var optionsSpark3 = {
    series: [{
    data: [30,40,45,50,49,60,70,91,125]
}],
    chart: {
    type: 'area',
    height: 160,
    sparkline: {
    enabled: true
    },
},
stroke: {
    curve: 'straight'
},
fill: {
    opacity: 0.3
},
xaxis: {
    crosshairs: {
    width: 1
    },
},
yaxis: {
    min: 0
},
title: {
    text: '$135,965',
    offsetX: 0,
    style: {
    fontSize: '24px',
    color:'#FFFFFF',
    }
},
subtitle: {
    text: 'Profits',
    offsetX: 0,
    style: {
    fontSize: '14px',
    color:'#F5A623',
    }
}
};


var chartSpark1 = new ApexCharts(document.querySelector("#chartSpark1"), optionsSpark3);
var chartSpark2 = new ApexCharts(document.querySelector("#chartSpark2"), optionsSpark3);
var chartSpark3 = new ApexCharts(document.querySelector("#chartSpark3"), optionsSpark3);
var chartColumns = new ApexCharts(document.querySelector("#chartColumns"), optionsColumns);
var chartDonut = new ApexCharts(document.querySelector("#chartDonut"), optionsDonut);

chartSpark1.render();
chartSpark2.render();
chartSpark3.render();
chartColumns.render();
chartDonut.render();
