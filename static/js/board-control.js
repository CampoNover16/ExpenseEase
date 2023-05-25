document.addEventListener(
  "DOMContentLoaded",
  function () {
    showExpensesFromCurrentAndPreviouseMonth();
  },
  false
);

const monthNames = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function deleteUserBoard() {
  fetch("/deleteUserBoard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-cache",
  }).then((response) => {
    response.json().then((data) => {
      showAlertInfo(data["message"], "success", "userSettings");
      setTimeout(() => {
        window.location.reload();
      }, "5000");
    });
  });
}

function generateCodeToBoard() {
  var parentPlacement = document.querySelector(".board-invitation-code");
  var data = { toExistingBoard: "True" };
  fetch("/createInvfromReq", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
    cache: "no-cache",
  }).then((response) => {
    showAlertInfo(
      "Your new invitation code has been generated!",
      "success",
      "userSettings"
    );

    response.json().then((data) => {
      parentPlacement.querySelector("strong").innerHTML = data["newBoardCode"];
      document.querySelector(".inv-code").value = data["newBoardCode"];
    });
  });
}

function changeBoardName(currentName) {
  var parentPlacement = document.querySelector(".board-name");
  var inputHtml =
    '<input type="text" class="form-control newBoardName" value="' +
    currentName +
    '" style="width: 235px;">';
  var saveButton =
    '<button onclick="saveBoardName()" class="btn btn-primary saveNewBoardName">Save</button>';

  document.querySelector(".changeBoardName").style.display = "none";
  parentPlacement.querySelector("strong").style.display = "none";
  parentPlacement.insertAdjacentHTML("afterEnd", saveButton);
  parentPlacement.insertAdjacentHTML("afterEnd", inputHtml);
}

function saveBoardName() {
  var parentPlacement = document.querySelector(".board-name");
  var newNameHook = document.querySelector(".newBoardName");
  var data = { newName: newNameHook.value };
  document.querySelector(".changeBoardName").style.display = "initial";
  parentPlacement.querySelector("strong").style.display = "initial";

  newNameHook.remove();
  document.querySelector(".saveNewBoardName").remove();

  if (newNameHook.value !== "") {
    fetch("/saveUserBoardName", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      cache: "no-cache",
    }).then(() => {
      showAlertInfo(
        "Your board name changed succesfully!",
        "success",
        "userSettings"
      );
      document.querySelector(".userBoardName").innerHTML = data["newName"];
    });
  } else {
    showAlertInfo("Something went wrong! Try again.", "danger", "userSettings");
  }
}

window.onload = () => {
  loadAllData();
};

modal.addEventListener("shown.bs.modal", function () {
  var isNameValid,
    isPriceValid = false;
  document.getElementById("expense-date").valueAsDate = new Date();
  const nameInput = document.getElementById("expense-name");
  const priceInput = document.getElementById("expense-price");
  const btn = document.getElementById("sub-btn");
  btn.disabled = true;

  nameInput.addEventListener("blur", function () {
    if (nameInput.value != "") {
      isNameValid = true;
      if (isNameValid && isPriceValid) {
        btn.disabled = false;
      }
    }
  });
  priceInput.addEventListener("blur", function () {
    if (priceInput.value != "") {
      isPriceValid = true;
      if (isNameValid && isPriceValid) {
        btn.disabled = false;
      }
    }
  });
});

function loadAllData() {
  const expensesList = document.getElementById("expenses-list");
  while (
    expensesList.firstChild &&
    expensesList.removeChild(expensesList.firstChild)
  );
  let html = "";

  fetch("/getAllExpenses", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  }).then((response) => {
    response.json().then((data) => {
      calculateExpensesByCategory(data);
      calculateCashFromCurrentMonth(data);
      data.forEach((item) => {
        html += generateListItem(item);
      });
      expensesList.innerHTML = html;
    });
  });
}

function calculateExpensesByCategory(items) {
  const uniqueCategories = [...new Set(items.map((item) => item.category))];
  const finalPercentage = {};
  var sumOfAll = 0;

  items.forEach((temp2) => {
    sumOfAll += temp2.price;
  });

  uniqueCategories.forEach((category) => {
    const filteredByCategory = items.filter(
      (item) => item.category == category
    );
    let sum = 0;
    filteredByCategory.forEach((temp1) => {
      sum += temp1.price;
    });
    finalPercentage[category] = parseInt(sum);
  });
  donutGraphCreate(finalPercentage);
}

function showExpensesFromCurrentAndPreviouseMonth() {
  fetch("/getAllMonthlyExpenses", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  }).then((response) => {
    response.json().then((data) => {
      createCompareMonthsChart(data[0],data[1]);
    });
  });
}

function createCompareMonthsChart(incomeArray, expenseArray) {
  var columnsChartDivHook = document.getElementById("chartColumns");
  var rdyIncome = []
  var rdyExpense = []
  monthNames.forEach((item) => {
    rdyIncome[item] = 0
    rdyExpense[item] = 0
  })

  incomeArray.forEach((item) => {
    rdyIncome[item.month] = item.value
  })

  expenseArray.forEach((item) => {
    rdyExpense[item.month] = item.value;
  })

  var optionsColumns = {
    series: [{
        name: "Monthly expenses",
        data: Object.values(rdyExpense)
      },{
        name: "Monthly incomes",
        data: Object.values(rdyIncome)
      }],
    xaxis: {
      categories: Object.keys(rdyIncome),
      labels: {
        show: true,
        style: {
            colors: '#FFFFFF',
            fontSize: '12px',
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 400,
            cssClass: 'apexcharts-xaxis-label',
        },
      },
    },
    yaxis: {
      labels: {
        show: true,
        style: {
            colors: '#FFFFFF',
            fontSize: '12px',
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 400,
            cssClass: 'apexcharts-xaxis-label',
        },
      },
    },
    chart: {
      type: "bar",
      stacked: true,
    },
    tooltip: {
      enabled: true,
      theme: "dark",
    },
    legend: {
      show: true,
      labels: {
        colors: '#FFFFFF',
        useSeriesColors: true,
      },
    },
    colors: ["#ff00ff","#00E396"],
    dataLabels: {
      enabled: false,
    }
  };

  var chartColumns = new ApexCharts(
    columnsChartDivHook,
    optionsColumns
  );
  chartColumns.render();
}

function calculateCashFromCurrentMonth(items) {
  const uniqueDate = [...new Set(items.map((item) => item.date))];
  const finalDailyIncomes = {};
  const finalDailyExpenses = {};
  var sumOfAllIncomes = 0;
  var sumOfAllExpenses = 0;

  items.forEach((item) => {
    if (item.data_type == 1) {
      sumOfAllExpenses += item.price;
    }else{
      sumOfAllIncomes += item.price;
    }
  });

  uniqueDate.forEach((date) => {
    const filteredByDate = items.filter((item) => item.date == date);
    let sumIncomes = 0;
    let sumExpenses = 0;

    filteredByDate.forEach((item) => {
      if (item.data_type == 1) {
        sumExpenses += item.price;
      }else{
        sumIncomes += item.price;
      }
    });
    finalDailyIncomes[date] = sumIncomes.toFixed(2);
    finalDailyExpenses[date] = sumExpenses.toFixed(2);
  });

  currentMonthIncomesGraphCreate(finalDailyIncomes, sumOfAllIncomes);
  currentMonthExpensesGraphCreate(finalDailyExpenses, sumOfAllExpenses);
}

function currentMonthExpensesGraphCreate(items, sum) {
  const d = new Date();
  var spark2DivHook = document.getElementById("chartSpark2");

  var optionsSpark2 = {
    series: [{
        name: "Daily total",
        data: Object.values(items),
      },
    ],
    labels: Object.keys(items),
    legend: {
      show: true,
      labels: {
        useSeriesColors: true,
      },
    },
    chart: {
      type: "area",
      height: 160,
      sparkline: {
        enabled: true,
      },
    },
    stroke: {
      curve: "straight",
    },
    fill: {
      opacity: 0.3,
    },
    xaxis: {
      crosshairs: {
        width: 1,
      },
    },
    yaxis: {
      min: 0,
    },
    title: {
      text: sum + " PLN",
      offsetX: 0,
      style: {
        fontSize: "24px",
        color: "#FFFFFF",
      },
    },
    tooltip: {
      enabled: true,
      theme: "dark",
    },
    subtitle: {
      text:
        "Total expenses(" +
        monthNames[d.getMonth()] +
        " " +
        d.getFullYear() +
        ")",
      offsetX: 0,
      style: {
        fontSize: "14px",
        color: "#F5A623",
      },
    },
  };

  var chartSpark2 = new ApexCharts(spark2DivHook, optionsSpark2);
  if (spark2DivHook.childNodes.length == 0) {
    chartSpark2.render();
  }
}

function currentMonthIncomesGraphCreate(items, sum) {
  const d = new Date();
  var spark1DivHook = document.getElementById("chartSpark1");

  var optionsSpark2 = {
    series: [
      {
        name: "Daily total",
        data: Object.values(items),
      },
    ],
    labels: Object.keys(items),
    legend: {
      show: true,
      labels: {
        useSeriesColors: true,
      },
    },
    chart: {
      type: "area",
      height: 160,
      sparkline: {
        enabled: true,
      },
    },
    stroke: {
      curve: "straight",
    },
    fill: {
      opacity: 0.3,
    },
    xaxis: {
      crosshairs: {
        width: 1,
      },
    },
    yaxis: {
      min: 0,
    },
    title: {
      text: sum + " PLN",
      offsetX: 0,
      style: {
        fontSize: "24px",
        color: "#FFFFFF",
      },
    },
    tooltip: {
      enabled: true,
      theme: "dark",
    },
    subtitle: {
      text:
        "Total incomes(" +
        monthNames[d.getMonth()] +
        " " +
        d.getFullYear() +
        ")",
      offsetX: 0,
      style: {
        fontSize: "14px",
        color: "#F5A623",
      },
    },
  };

  var chartSpark1 = new ApexCharts(spark1DivHook, optionsSpark2);
  if (spark1DivHook.childNodes.length == 0) {
    chartSpark1.render();
  }
}

function donutGraphCreate(items) {
  var donutDivHook = document.getElementById("chartDonut");
  var optionsDonut = {
    series: Object.values(items),
    labels: Object.keys(items),
    legend: {
      show: true,
      labels: {
        useSeriesColors: true,
      },
      position: "bottom",
      horizontalAlign: "center",
      floating: false,
    },
    chart: {
      type: "donut",
    },
    responsive: [
      {
        breakpoint: 480,
        options: {
          chart: {
            width: 200,
          },
          legend: {
            position: "bottom",
          },
        },
      },
    ],
    tooltip: {
      enabled: true,
      theme: "dark",
    },
    title: {
      text: "Categorized monthly epxenses (PLN)",
      align: "center",
      offsetX: 0,
      style: {
        fontSize: "22px",
        color: "#FFFFFF",
      },
    },
  };
  var chartDonut = new ApexCharts(donutDivHook, optionsDonut);
  if (donutDivHook.childNodes.length == 0) {
    chartDonut.render();
  }
}

function generateListItem(item) {
  return `<li class="expense-element" id="element-${item.id}">
      <div class="expense-element_name">
        <h3 class="expense-element_name_name">${item.name}</h3>
        <p class="expense-element_name_category">${item.category}</p>
      </div>
      <div class="expense-element_date">
        ${item.date}
      </div>
      <div class="expense-element_price">
      ${item.price} PLN
    </div>
      <div class="expense-element_options">
        <button onClick="loadExpenseHandler(${item.id})" data-bs-toggle="modal" data-bs-target="#modalChangeCenter"">Change</button>
        <button onClick="deleteExpenseHandler(${item.id})">Delete</button>
      </div>
  </li>`;
}

function joinToBoard() {
  var inv_code = document.getElementsByClassName("inv-code")[0].value;
  var join_code = document.getElementsByClassName("join-code")[0].value;
  if (inv_code !== join_code) {
    let myModalEl = document.getElementById("joinWithCodeModal");
    let modal = bootstrap.Modal.getInstance(myModalEl);
    modal.hide();
    joinUserBoard(join_code);
  } else {
    showAlertInfo(
      "You cannot join to your own board!",
      "danger",
      "joinWithCodeModal"
    );
  }
}

function copyInviteContent() {
  var inv_code = document.getElementsByClassName("inv-code")[0].value;
  navigator.clipboard.writeText(inv_code);
  showAlertInfo(
    "Code was successfully copied!",
    "success",
    "invitationCodeModal"
  );
}

function loadExpenseHandler(id) {
  var date = document.getElementById("expense-change-date");
  var nameInput = document.getElementById("expense-change-name");
  var priceInput = document.getElementById("expense-change-price");
  var categoryInput = document.getElementById("expense-change-category");
  var incomeCategoryInput = document.getElementById("income-change-category");
  var incomeRadio = document.getElementById("incomeRadioChange");
  var expenseRadio = document.getElementById("expenseRadioChange");

  changeExpenseForm.dataset.expenseId = id;

  fetch("/getExpense", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(id),
    cache: "no-cache",
  }).then((response) => {
    response.json().then((data) => {
      nameInput.value = data.name;
      priceInput.value = data.price;
      if (data.data_type == 0) {
        incomeRadio.checked = true;
        incomeRadio.click();
        incomeCategoryInput.value = data.category;
      } else {
        expenseRadio.checked = true;
        expenseRadio.click();
        categoryInput.value = data.category;
      }
      var dateParts = data.date.split("-");
      date.valueAsDate = new Date(
        Date.UTC(dateParts[2], dateParts[1] - 1, dateParts[0])
      );
    });
  });
}

function deleteExpenseHandler(id) {
  fetch("/deleteExpense", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(id),
    cache: "no-cache",
  }).then(() => {
    loadAllData();
  });
}

function changeExpenseFormHandler(id) {
  var name = document.getElementById("expense-change-name").value;
  var price = document.getElementById("expense-change-price").value;
  var category = "";
  var date = document.getElementById("expense-change-date").value;
  var incomeRadio = document.getElementById("incomeRadioChange");
  var expenseRadio = document.getElementById("expenseRadioChange");
  var expenseOrIncome = null;

  if (expenseRadio.checked) {
    category = document.getElementById("expense-change-category").value;
    expenseOrIncome = expenseRadio.value;
  } else if (incomeRadio.checked) {
    category = document.getElementById("income-change-category").value;
    expenseOrIncome = incomeRadio.value;
  }

  var changeExpenseData = {
    id,
    name,
    price,
    category,
    date,
    expenseOrIncome,
  };

  fetch("/changeExpense", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changeExpenseData),
    cache: "no-cache",
  }).then(() => {
    showAlertInfo("Your expense updated successfully!", "success", null);
    loadAllData();
  });
}

changeExpenseForm.addEventListener("submit", function (e) {
  e.preventDefault();
  changeExpenseFormHandler(changeExpenseForm.dataset.expenseId);
});

function addExpenseFormHandler() {
  var name = document.getElementById("expense-name").value;
  var price = document.getElementById("expense-price").value;
  var category = "";
  var date = document.getElementById("expense-date").value;
  var incomeRadio = document.getElementById("incomeRadio");
  var expenseRadio = document.getElementById("expenseRadio");
  var expenseOrIncome = null;

  if (expenseRadio.checked) {
    category = document.getElementById("expense-category").value;
    expenseOrIncome = expenseRadio.value;
  } else if (incomeRadio.checked) {
    category = document.getElementById("income-category").value;
    expenseOrIncome = incomeRadio.value;
  }

  var addExpenseData = {
    name,
    price,
    category,
    date,
    expenseOrIncome,
  };

  fetch("/addExpense", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(addExpenseData),
    cache: "no-cache",
  }).then(() => {
    showAlertInfo("Your expense added successfully!", "success", null);
    loadAllData();
  });
}

addExpenseForm.addEventListener("submit", function (e) {
  e.preventDefault();
  addExpenseFormHandler();
  addExpenseForm.reset();
});



var raport_generator = document.getElementById("raport_generator");
raport_generator.addEventListener(event, getDateForUsersBoardData(), {
  once: true,
});

function createOptionsForSelect(data, target_element) {
  data.forEach((element) => {
    let newOption = document.createElement("option");
    if (target_element.name == "date-select") {
      newOption.text = monthNames[element.month] + " " + element.year;
      newOption.value = element.month + " " + element.year;
    }
    target_element.appendChild(newOption);
  });
}

function getDateForUsersBoardData() {
  var raport_date_select = document.getElementById("raport-date-select");
  fetch("/getDateForUsersBoardData", {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  }).then((response) => {
    response.json().then((data) => {
      createOptionsForSelect(data, raport_date_select);
    });
  });
}

async function exportExcel() {
  var dateSelect = document.getElementById("raport-date-select");
  if (dateSelect.value == "select-default") {
    showAlertInfo(
      "Select month and year before raport generation request!",
      "danger",
      null
    );
  } else {
    var temp_dataSelect = dateSelect.value;
    var dataSelectArray = temp_dataSelect.split(" ");
    var data = {
      month: parseInt(dataSelectArray[0]),
      year: parseInt(dataSelectArray[1]),
    };

    let response = await fetch("/download_excel_api", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    let blobResponse = await response.blob();
    const fileName =
      "expenses-raport_" +
      dataSelectArray[0] +
      "_" +
      dataSelectArray[1] +
      ".xlsx";
    downloadExcelSilently(blobResponse, fileName);
  }
}
function downloadExcelSilently(blobExcelFile, filename) {
  const url = window.URL.createObjectURL(blobExcelFile);
  const hiddenAnchor = document.createElement("a");
  hiddenAnchor.style.display = "none";
  hiddenAnchor.href = url;
  hiddenAnchor.download = filename;
  document.body.appendChild(hiddenAnchor);
  hiddenAnchor.click();
  window.URL.revokeObjectURL(url);
}

// function addNextGoalRow(){
//   var goals_tbody = document.getElementById("goals-tbody");
//   let rawHtml = "<tr><td style='width: 75%'>I don't want to exceed the expenses in the <strong style='color: var(--accent);'>[name]</strong> category over <strong style='color: var(--accent);'>[X PLN]</strong>.</td>" +
//                 "<td><input type='text' class='form-control'></td>"+
//                 "</tr>";
//   goals_tbody.insertAdjacentHTML('beforeend',rawHtml);
// }

function setUserGoals(){
  var endMonthSaved = document.getElementById("end_month_saved");
  var totalMaxExpense = document.getElementById("total_max_expense");
  var dailyMaxExpense = document.getElementById("daily_max_expense");
  var foodMaxExpense = document.getElementById("food_max_expense");
  var entertainmentMaxExpense = document.getElementById("entertainment_max_expense");
  var homeMaxExpense = document.getElementById("home_max_expense");
  var carMaxExpense = document.getElementById("car_max_expense");

  var inputChecker = [endMonthSaved,totalMaxExpense,dailyMaxExpense,foodMaxExpense,entertainmentMaxExpense,homeMaxExpense,carMaxExpense]
  var data = {}
  inputChecker.forEach(element => {
    if(element.value != '' && element.value > 0){
      data[element.id] = element.value
    }
  })

  fetch("/setUsersBoardGoals", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data),
  }).then((response) => {
    response.json().then((data)=>{
      console.log(data);
      showAlertInfo("Your goals has been set!",'success',null);
    })
  });
}
